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


namespace OPNsense\OPNCell\Api;

use Exception;
use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;
use OPNsense\Mvc\Request;
use OPNsense\OPNCell\General;
use OPNsense\OPNCell\Opncore;
use OPNsense\Core\Config;
use Phalcon\Messages\Message;

/**
 * Class ServiceController
 * @package OPNsense\OPNCore
 */
class ServiceController extends ApiControllerBase
{
    private function manageService($process, $action): array
    {
        try {
            $backend = new Backend();
            $command = ($process == "mongodd" ? "mongod" : $process) . ' ' . $action;
            $response = $backend->configdRun($command);
            return array('response' => $response);
        } catch (Exception $e) {
            return array('response' => 'error', 'message' => $e->getMessage());
        }
    }

    /**
     * start services
     * @param $process
     * @return array
     */

    public function startAction($process): array
    {
        $this->request = new Request();
        if ($this->request->isPost()) {
            return $this->manageService($process, 'start');
        }
        return array('response' => array());
    }
    public function restartAction($process): array
    {
        $this->request = new Request();
        if ($this->request->isPost()) {
            $this->manageService($process, 'stop');
            return $this->manageService($process, 'start');
        }
        return array('response' => array());
    }
    public function stopAction($process): array
    {
        $this->request = new Request();
        if ($this->request->isPost()) {
            return $this->manageService($process, 'stop');
        }
        return array('response' => array());
    }
    public function statusAction()
    {

    }

    private array $serviceMapping = [
        'enablefour' => [
            "enablehssd" => "hssd", "enablemmed" => "mmed", "enablepcrfd" => "pcrfd",
            "enablesgwud" => "sgwud", "enablesgwcd" => "sgwcd", "enablesmfd" => "smfd",
            "enableupfd" => "upfd","enablescpd" => "scpd","enablenrfd" => "nrfd"
        ],
        'enablefiveNSA' => [
            "enablehssd" => "hssd", "enablemmed" => "mmed", "enablepcrfd" => "pcrfd",
            "enablesgwud" => "sgwud", "enablesgwcd" => "sgwcd", "enablesmfd" => "smfd",
            "enableupfd" => "upfd"
        ],
        'enablefiveSA' => [
            "enablenrfd" => "nrfd", "enablescpd" => "scpd", "enableamfd" => "amfd",
            "enablesmfd" => "smfd", "enableupfd" => "upfd", "enableausfd" => "ausfd",
            "enableudmd" => "udmd", "enableudrd" => "udrd", "enablepcfd" => "pcfd",
            "enablenssfd" => "nssfd", "enablebsfd" => "bsfd","enablesepp" =>"sepp"
        ],
        'enableupf' => [
            "enableamfd" => "amfd", "enablesmfd" => "smfd", "enableupfd" => "upfd", "enableausfd" => "ausfd",
            "enableudmd" => "udmd", "enableudrd" => "udrd", "enablepcfd" => "pcfd",
            "enablenssfd" => "nssfd"
        ]
    ];

    private function manageNetworkServices($network): void
    {
        $services = $this->serviceMapping[$network] ?? [];
        $allServices = [];
        foreach ($this->serviceMapping as $networkServices) {
            foreach ($networkServices as $daemon) {
                $allServices[$daemon] = true;
            }
        }

        // Stop all services that are not in the current network's services
        foreach ($allServices as $daemon => $value) {
            if (!in_array($daemon, $services)) {
                $this->stopAction($daemon);
            }
        }

        // Start the services that belong to the current network
        foreach ($services as $daemon) {
            $this->stopAction($daemon);
            $this->startAction($daemon);
        }
    }

    /**
     * @throws Exception
     */
    public function reconfigureActAction($network)
    {
        if ($this->request->isPost()) {
            $this->sessionClose();
            (new GeneralController)->setNetwork($network);
            $backend = new Backend();
            $backend->configdRun('mongod start');
            $backend->configdRun('template reload OPNsense/OPNCell');
            $this->manageNetworkServices($network);
        }
    }

    private function validateGeneral($mdlGeneral)
    {
        $valMsgs = $mdlGeneral->performValidation();
        $fields = [
            'mcc' => [3, 3, 'Should be 3 digits in the range 001-999'],
            'mnc' => [2, 3, 'Should be either 2 or 3 digits'],
            'tac' => [1, 2, 'Should be 1 or 2 digits']
        ];

        foreach ($fields as $field => [$min, $max, $message]) {
            $value = $mdlGeneral->$field->__toString();
            if (strlen($value) < $min || strlen($value) > $max) {
                $valMsgs->appendMessage(new Message(gettext($message), $field));
            }
        }

        return $valMsgs;
    }

    /**
     * @throws Exception
     */
    public function setAction($network): array
    {
        $result = array("result" => "failed");
        if ($this->request->isPost()) {
            $mdlGeneral = new General();
            $mdlGeneral->setNodes($this->request->getPost("general"));
            $mdlGeneral->setNodes([$network => "1"]);

            $valMsgs = $this->validateGeneral($mdlGeneral, $network);

            foreach ($valMsgs as $msg) {
                if (!isset($result["validations"])) {
                    $result["validations"] = array();
                }
                $result["validations"]["general." . $msg->getField()] = $msg->getMessage();
            }

            $result['general'] = $mdlGeneral->getNodes();
            $result['general']['network'] = $network;
            $values = json_encode($result);

            if ($valMsgs->count() == 0) {
                $mdlGeneral->serializeToConfig();
                Config::getInstance()->save();
                $backend = new Backend();
                $backend->configdpRun("opncore loadConfiguration", array($values));
                $result["result"] = "saved";
            }
        }
        return $result;
    }
}
