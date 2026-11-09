<?php

/*
    Copyright (C) 2025 Digital Solutions
    Copyright (C) 2025 Wire Labs
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
use OPNsense\OPNCell\ServiceNames;
use OPNsense\Core\Backend;
use OPNsense\Mvc\Request;
use OPNsense\OPNCell\General;
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
            $topic = ServiceNames::topic($process);
            if ($topic === null) {
                return ['response' => 'error', 'message' => 'Unknown cellular service'];
            }
            $backend = new Backend();
            $command = $topic . ' ' . $action;
            $response = trim((string)$backend->configdRun($command));
            if ($response !== 'OK') {
                return ['response' => 'error', 'message' => 'Could not ' . $action . ' ' . ServiceNames::canonical($topic) . '. Check the configd log.'];
            }
            $status = trim((string)$backend->configdRun($topic . ' status'));
            $expected = $action === 'stop' ? 'not running' : 'is running';
            if (!str_contains($status, $expected)) {
                return [
                    'response' => 'error',
                    'message' => 'Could not verify ' . ServiceNames::canonical($topic) . ' after ' . $action . '. Check its diagnostic log.',
                ];
            }

            return ['response' => 'OK'];
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
            return $this->manageService($process, 'restart');
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
            "enableupfd" => "upfd", "enablescpd" => "scpd","enablenrfd" => "nrfd"
        ],
        'enablefiveSA' => [
            "enablenrfd" => "nrfd", "enablescpd" => "scpd", "enableamfd" => "amfd",
            "enablesmfd" => "smfd", "enableupfd" => "upfd", "enableausfd" => "ausfd",
            "enableudmd" => "udmd", "enableudrd" => "udrd", "enablepcfd" => "pcfd",
            "enablenssfd" => "nssfd", "enablebsfd" => "bsfd"
        ],
        'enableupf' => ["enableupfd" => "upfd"]
    ];

    private function manageNetworkServices(string $network, Backend $backend): array
    {
        $services = array_values($this->serviceMapping[$network]);
        $allServices = array_unique(array_merge(...array_map('array_values', array_values($this->serviceMapping))));
        $failed = [];

        foreach ($allServices as $daemon) {
            $backend->configdRun($daemon . ' stop');
            $status = (string)$backend->configdRun($daemon . ' status');
            if (!str_contains($status, 'not running')) {
                $failed[] = ServiceNames::canonical($daemon) . ' stop';
            }
        }

        if ($failed) {
            return [
                'result' => 'failed',
                'message' => 'Could not stop services before applying the topology: ' . implode(', ', $failed),
            ];
        }

        foreach ($services as $daemon) {
            $started = trim((string)$backend->configdRun($daemon . ' start'));
            $status = (string)$backend->configdRun($daemon . ' status');
            if ($started !== 'OK' || !str_contains($status, 'is running')) {
                $failed[] = ServiceNames::canonical($daemon) . ' start';
            }
        }

        return $failed ? [
            'result' => 'failed',
            'message' => 'Could not verify the requested state for: ' . implode(', ', $failed),
        ] : ['result' => 'applied'];
    }

    public function reconfigureActAction($network): array
    {
        if (!$this->request->isPost() || !isset($this->serviceMapping[$network])) {
            return ['result' => 'failed', 'message' => 'Invalid network apply request'];
        }
        $backend = new Backend();
        $result = $this->saveNetworkSettings($network, $backend);
        if ($result['result'] !== 'saved') {
            return $result;
        }

        $template = trim((string)$backend->configdpRun('template reload', ['OPNsense/OPNCell']));
        if ($template !== 'OK') {
            return ['result' => 'failed', 'message' => 'Could not render service enablement'];
        }
        if (!str_contains((string)$backend->configdRun('mongod status'), 'is running')) {
            $backend->configdRun('mongod start');
        }
        if (!str_contains((string)$backend->configdRun('mongod status'), 'is running')) {
            return ['result' => 'failed', 'message' => 'MongoDB did not start'];
        }
        $runtime = $this->manageNetworkServices($network, $backend);
        if ($runtime['result'] !== 'applied') {
            return $runtime;
        }
        $boot = json_decode((string)$backend->configdpRun('opncell verifyBoot', [$network]), true);
        if (($boot['result'] ?? '') !== 'verified') {
            return ['result' => 'failed', 'message' => $boot['message'] ?? 'Services started, but boot settings could not be verified'];
        }
        return ['result' => 'applied'];
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
        if (!$this->request->isPost() || !isset($this->serviceMapping[$network])) {
            return ['result' => 'failed', 'message' => 'Invalid network settings request'];
        }
        return $this->saveNetworkSettings($network);
    }

    private function saveNetworkSettings(string $network, ?Backend $backend = null): array
    {
        $model = new General();
        $settings = (array)$this->request->getPost('general');
        foreach (array_keys($this->serviceMapping) as $mode) {
            unset($settings[$mode]);
        }
        $model->setNodes($settings);

        $validations = [];
        foreach ($this->validateGeneral($model) as $message) {
            $validations['general.' . $message->getField()] = $message->getMessage();
        }
        if ($validations) {
            return ['result' => 'failed', 'validations' => $validations];
        }

        // Every activation path renders YAML, including direct requests from Hnet.
        if ($backend !== null) {
            $general = $model->getNodes();
            $general['network'] = $network;
            $payload = base64_encode(json_encode(['general' => $general], JSON_THROW_ON_ERROR));
            $response = $backend->configdpRun('opncell loadConfiguration', [$payload]);
            if ((json_decode((string)$response, true)['result'] ?? '') !== 'rendered') {
                return ['result' => 'failed', 'message' => 'Could not write Open5GS configuration'];
            }
            foreach (array_keys($this->serviceMapping) as $mode) {
                $model->setNodes([$mode => $mode === $network ? '1' : '0']);
            }
        }

        $model->serializeToConfig();
        Config::getInstance()->save();
        return ['result' => 'saved'];
    }
}
