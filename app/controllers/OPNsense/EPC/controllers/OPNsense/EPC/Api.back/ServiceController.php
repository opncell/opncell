<?php

/*
 * Copyright (C) 2015-2017 Deciso B.V.
 * Copyright (C) 2017 Fabian Franz
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

namespace OPNsense\EPC\Api;

use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;
use OPNsense\EPC\General;
use OPNsense\EPC\Opncore;

/**
 * Class ServiceController
 * @package OPNsense\EPC
 */
class ServiceController extends ApiControllerBase
{
    /**
     * start epcmmed service

     * @return array
     */
    public function startAction($process)
    {
        if ($this->request->isPost()) {
            $backend = new Backend();
            $response = $backend->configdRun($process . ' '. 'start');
//            $backend->configdRun('filter reload');
            return array('response' => $response);
        } else {
            return array('response' => array());
        }
    }

    /**
     * stop epcmmed service
     * @return array
     */
    public function stopAction()
    {
        if ($this->request->isPost()) {
            $backend = new Backend();
            $response = $backend->configdRun('epc stop');
            $mdlGeneral = new General();

            $result['general'] = $mdlGeneral->getNodes();

            foreach ($result["general"] as $key => $value) {
                if ($value === "0") {
                    // Remove "enable" from the key so that you remain with only the daemon name
                    $daemon = str_replace("enable", "", $key);
                    $response = $backend->configdRun($daemon . ' '. 'stop');
                }
            }
            return array('response' => $response);
        } else {
            return array('response' => array());
        }
    }

    /**
     * restart epcmmed service
     * @return array
     */
    public function restartAction()
    {
        if ($this->request->isPost()) {
            $backend = new Backend();
            $response = $backend->configdRun('epc restart');
            $backend->configdRun('filter reload');
            return array('response' => $response);
        } else {
            return array('response' => array());
        }
    }

    /**
     * retrieve status of epcmmed
     * @return array
     * @throws \Exception
     */
    public function statusAction()
    {
        $backend = new Backend();
        $mdlGeneral = new General();
        $response = $backend->configdRun('epc status');

        if (strpos($response, 'not running') > 0) {
            if ($mdlGeneral->enabled->__toString() == 1) {
                $status = 'stopped';
            } else {
                $status = 'disabled';
            }
        } elseif (strpos($response, 'is running') > 0) {
            $status = 'running';
        } elseif ($mdlGeneral->enablemmed->__toString() == 0) {
            $status = 'disabled';
        } else {
            $status = 'unknown';
        }


        return array('status' => $status);
    }

    public function reconfigureAction()
    {
        if ($this->request->isPost()) {
            // close session for long running action
            $this->sessionClose();

            $mdlGeneral = new General();
            $mdlOPN = new Opncore();
            $backend = new Backend();

            $this->sessionClose();

            // stop if it is running or not
            $this->stopAction();

            // generate template
            $backend->configdRun('template reload OPNsense/EPC');

            $selectedNetwork['opnc'] = $mdlOPN->getNodes();
            $result['general'] = $mdlGeneral->getNodes();

            $fourGServices =["enablehssd"=>"hssd","enablemmed"=>"mmed",
                "enablepcrfd"=>"pcrfd","enablesgwud"=>"sgwud"];

            $fiveGSAServices =["enableausfd"=>"ausfd","enableamfd"=>"amfd","enableudmd"=>"udmd",
                "enablesmfd"=>"smfd","enablenssfd"=>"nssfd", "enablenrfd"=>"nrfd",
                "enablepcfd"=>"pcfd", "enableupfd"=>"upfd"];

            $fiveNSAGServices = ["enableausfd"=>"ausfd","enableamfd"=>"amfd","enableudmd"=>"udmd",
                "enablesmfd"=>"smfd","enablenssfd"=>"nssfd", "enablenrfd"=>"nrfd",
                "enablepcfd"=>"pcfd", "enableupfd"=>"upfd","enablesgwud"=>"sgwud",
                "enablesgwcd"=>"sgwcd","enablemmed"=>"mmed"];

            foreach ($selectedNetwork["opnc"] as $networKey => $value) {
                if ($value === "1" && $networKey == "enablefour") {
                    foreach ($result["general"] as $daemonKey => $valueg) {
                        $daemon = str_replace("enable", "", $daemonKey);
                        if (array_key_exists($daemonKey, $fourGServices)) {
                            $mdlGeneral->setNodes([$daemonKey=>1]);
                            $status = $this->startAction($daemon);
                            //Track services that have not successfully started.
                            if ($status != "OK") {
                                $this->startAction($daemon);
                            }
                        } else {
                            $backend->configdRun($daemon . ' '. 'stop');
                        }
                    }
                } elseif ($value === "1" && $networKey == "enablefiveNSA") {
                    foreach ($result["general"] as $daemonKey => $valueg) {
                        $daemon = str_replace("enable", "", $daemonKey);
                        if (array_key_exists($daemonKey, $fiveGSAServices)) {
                            $mdlGeneral->setNodes([$daemonKey=>1]);
//                            $result['general'] = $mdlGeneral->getNodes();
//                            print_r( $result);

                            $this->startAction($daemon);
                        } else {
                            $backend->configdRun($daemon . ' '. 'stop');
                        }
                    }
                } elseif ($value === "1" && $networKey == "enablefiveSA") {
                    $daemon = str_replace("enable", "", $daemonKey);
                    foreach ($result["general"] as $daemonKey => $valueg) {
                        if (array_key_exists($daemonKey, $fiveNSAGServices)) {
                            $mdlGeneral->setNodes([$daemonKey=>1]);
//                            $result['general'] = $mdlGeneral->getNodes();
//                            print_r( $result);

                            $this->startAction($daemon);
                        } else {
                            $backend->configdRun($daemon . ' '. 'stop');
                        }
                    }
                }
            }
        }
    }

    public function reconfigureNAction()
    {
        if ($this->request->isPost()) {
            // close session for long running action

            $mdlGeneral = new General();
            $mdlOPN = new Opncore();
            $backend = new Backend();

            $this->sessionClose();

            // stop if it is running or not
            $this->stopAction();

            // generate template
            $backend->configdRun('template reload OPNsense/EPC');

            $selectedNetwork['opnc'] = $mdlOPN->getNodes();

            $result['general'] = $mdlGeneral->getNodes();
                    foreach ($result["general"] as $daemonKey => $valueg){
                        if($valueg == 1){
                            $daemon = str_replace("enable", "", $daemonKey);
                            $backend->configdRun($daemon . ' '. 'start');
                        }

                    }
        }
    }
}
