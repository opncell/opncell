<?php

/*
    Copyright (C) 2023 Digital Solutions
    Copyright (C) 2023 Wire Labs
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
*/


namespace OPNsense\OPNCore\Api;

use Exception;
use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;
use OPNsense\OPNCore\General;
use OPNsense\OPNCore\Opncore;
use OPNsense\Core\Config;
use Phalcon\Messages\Message;

/**
 * Class ServiceController
 * @package OPNsense\OPNCore
 */
class ServiceController extends ApiControllerBase
{
    /**
     * start services
     * @param $process
     * @return array
     */

    public function startAction($process): array
    {
        if ($this->request->isPost()) {
            $backend = new Backend();
            if ($process == "mongodd") {
                $response = $backend->configdRun("opncore startMongo");
            } else {
                $response = $backend->configdRun($process . ' '. 'start');
            }
            return array('response' => $response);
        } else {
            return array('response' => array());
        }
    }
    public function restartAction($process): array
    {
        if ($this->request->isPost()) {
            $backend = new Backend();
            if ($process == "mongodd") {
                $response = $backend->configdRun("opncore restartMongo");
            } else {
                $backend->configdRun($process . ' '. 'stop');
                $response = $backend->configdRun($process . ' '. 'start');
            }
            return array('response' => $response);
        } else {
            return array('response' => array());
        }
    }
    public function stopAction($process): array
    {
        if ($this->request->isPost()) {
            $backend = new Backend();
            if ($process == "mongodd") {
                $response = $backend->configdRun("opncore stopMongo");
            } else {
                $response = $backend->configdRun($process . ' '. 'stop');
            }
            return array('response' => $response);
        } else {
            return array('response' => array());
        }
    }

    /**
     * @throws Exception
     */
    public function reconfigureActAction($network)
    {

        if ($this->request->isPost()) {
            // close session for long running action
            $this->sessionClose();

            $mdlServices = new Opncore();   // all services as nodes.(makes them easier to work /manipulate this way)
            $backend = new Backend();
            (new GeneralController)->setNetwork($network);
            $backend->configdRun("opncore startMongo");

            // generate template
            $backend->configdRun('template reload OPNsense/OPNCore');
            $services['service_lst'] = $mdlServices->getNodes();

            $fourGServices =["enablehssd"=>"hssd","enablemmed"=>"mmed",
                "enablepcrfd"=>"pcrfd","enablesgwud"=>"sgwud", "enablesgwcd"=>"sgwcd",
                "enablesmfd"=>"smfd","enableupfd"=>"upfd"];

            $fiveNSAGServices = ["enablehssd"=>"hssd","enablemmed"=>"mmed",
                "enablepcrfd"=>"pcrfd","enablesgwud"=>"sgwud", "enablesgwcd"=>"sgwcd",
                "enablesmfd"=>"smfd","enableupfd"=>"upfd"];

            $fiveGSAServices =["enablenrfd"=>"nrfd","enablescpd"=>"scpd","enableamfd"=>"amfd","enablesmfd"=>"smfd",
                "enableupfd"=>"upfd","enableausfd"=>"ausfd","enableudmd"=>"udmd","enableudrd"=>"udrd",
                "enablepcfd"=>"pcfd","enablenssfd"=>"nssfd","enablebsfd"=>"bsfd"];

            if ($network == "enablefour") {
                foreach ($services['service_lst'] as $daemonKey => $value) {
                    if (array_key_exists($daemonKey, $fourGServices)) {
                        $daemon = str_replace("enable", "", $daemonKey);
                        $this->stopAction($daemon);
                        $this->startAction($daemon);
                    } else {
                        $daemon = str_replace("enable", "", $daemonKey);
                        $backend->configdRun($daemon . ' '. 'stop');
                    }
                }
            } elseif ($network== "enablefiveNSA") {
                foreach ($services['service_lst'] as $daemonKey => $value) {
                    if (array_key_exists($daemonKey, $fiveNSAGServices)) {
                        $daemon = str_replace("enable", "", $daemonKey);
                        $this->stopAction($daemon);
                        $this->startAction($daemon);
                    } else {
                        $daemon = str_replace("enable", "", $daemonKey);
                        $backend->configdRun($daemon . ' '. 'stop');
                    }
                }
            } elseif ($network == "enablefiveSA") {
                foreach ($services['service_lst'] as $daemonKey => $value) {
                    if (array_key_exists($daemonKey, $fiveGSAServices)) {
                        $daemon = str_replace("enable", "", $daemonKey);
                        $this->stopAction($daemon);
                        $this->startAction($daemon);
                    } else {
                        $daemon = str_replace("enable", "", $daemonKey);
                        $backend->configdRun($daemon . ' '. 'stop');
                    }
                }
            }

        }
    }

    /**
     * @throws Exception
     */
    public function setAction($network): array
    {
        $result = array("result" => "failed");
        $backend = new Backend();
        if ($this->request->isPost()) {
            // load model and update with provided data
            $mdlGeneral = new General();

            $mdlGeneral->setNodes($this->request->getPost("general"));
            $mdlGeneral->setNodes([$network => "1"]);
            // perform validation
            $valMsgs = $mdlGeneral->performValidation();
            $mcc = $mdlGeneral->mcc->__toString();
            $mnc = $mdlGeneral->mnc->__toString();
            $tac = $mdlGeneral->tac->__toString();


            if (strlen($mcc) != 3) {
                $valMsgs->appendMessage(new Message(gettext('Should be 3 digits in the range  001-999'), 'mcc'));
            }
            if (strlen($mnc) < 2 || strlen($mnc) > 3) {
                $valMsgs->appendMessage(new Message(gettext('Should be either 2 or 3 digits'), 'mnc'));
            }
            if (strlen($tac) > 3) {
                $valMsgs->appendMessage(new Message(gettext('Should be 2 or 1 digits'), 'tac'));
            }

            foreach ($valMsgs as $field => $msg) {
                if (!array_key_exists("validations", $result)) {
                    $result["validations"] = array();
                }
                $result["validations"]["general." . $msg->getField()] = $msg->getMessage();
            }
            $result['general'] = $mdlGeneral->getNodes();
            $result['general']['network'] = $network;

            $values =  json_encode($result);

            //serialize model to config and save
            if ($valMsgs->count() == 0) {
                $mdlGeneral->serializeToConfig();
                Config::getInstance()->save();

                $backend->configdpRun("opncore loadConfiguration", array($values));

                $result["result"] = "saved";
            }
        }
        return $result;
    }
}
