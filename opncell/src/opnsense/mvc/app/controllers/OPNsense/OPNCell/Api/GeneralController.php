<?php

/*

 * Copyright (C) 2023 Digital Solutions
 * Copyright (C) 2023 Wire Labs
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

namespace OPNsense\OPNCell\Api;

use OPNsense\Base\BaseModel;
use OPNsense\Base\UserException;
use OPNsense\OPNCell\ServiceNames;
use OPNsense\Core\Backend;


use OPNsense\Mvc\Request;
use OPNsense\OPNCell\Opncell;
use OPNsense\OPNCell\User;
use OPNsense\OPNCell\General;
use OPNsense\Base\UIModelGrid;
use OPNsense\Base\ApiMutableModelControllerBase;
use Phalcon\Exception;
use Phalcon\Messages\Message;
use ReflectionException;

header("Access-Control-Allow-Origin: *");
class GeneralController extends ApiMutableModelControllerBase
{

    protected static $internalModelName = 'opncell';
    protected static $internalModelClass = '\OPNsense\OPNCell\Opncell';
    public Request $request;
//
    /**
     * @throws ReflectionException
     */
    public function getAction()
    {
        $result = array();
//            $mdlGeneral = $this->getModel();
            $mdlGeneral = new General();
            $result['general'] = $mdlGeneral->getNodes();
            return $result;
    }

    public function getUserAction(): array
    {
        $result = array();
        $this->request = new Request();
        if ($this->request->isGet()) {
            $mdlUser = new  User();
            $result['user'] = $mdlUser->getNodes();
        }
        return $result;
    }
    public function statusAction($serviceName)
    {
        $topic = ServiceNames::topic($serviceName);
        if ($topic === null) {
            return 'unknown';
        }
        $backend = new Backend();
        $model = new Opncell();
        try {
            $response = (string)$backend->configdRun($topic . ' status');
            $node = 'enable' . $topic;
            if (strpos($response, "not running") !== false) {
                if ($topic === 'mongod') {
                    $status = "stopped";
                } else {
                    $status = ($model->$node->__toString() == 1) ? "stopped" : "disabled";
                }
            } elseif (strpos($response, "is running") !== false) {
                $status = "running";
            } else {
                $status = "unknown";
            }
            return  $status ;
        } catch (Exception $e) {
            return "error: " . $e->getMessage();
        }
    }

    public function editServerConfigAction($params)
    {
        if (!(new Request())->isPost()) {
            return ['result' => 'failed', 'message' => 'POST required'];
        }
        $parts = explode(',', $params);
        $topic = ServiceNames::topic($parts[0]);
        if (count($parts) !== 3 || $topic === null) {
            return ['result' => 'failed', 'message' => 'Invalid cellular service'];
        }
        $backend = new Backend();
        $net = ['server' => $topic, 'pid' => $parts[1], 'ip' => $parts[2]];
        $val = json_encode($net);
        $response = $backend->configdpRun('opncell editServerConf', [$val]);
        $result = json_decode((string)$response, true);
        if (($result['result'] ?? '') !== 'saved') {
            return $result ?? ['result' => 'failed', 'message' => 'Could not save the service configuration'];
        }
        $backend->configdRun($topic . ' stop');
        if ($backend->configdRun($topic . ' start') !== 'OK') {
            return ['result' => 'failed', 'message' => 'Address saved, but the service failed to start'];
        }
        return $result;
    }

    private array $bindAddress = [
        'hssd' => '127.0.0.8',
        'mongod' => '127.0.0.1',
        'sgwcd' => '127.0.0.3',
        'pcrfd' => '127.0.0.9',
    ];

    /**
     * @throws \Exception
     */
    public function getProcessNamesAction($network): array
    {
        $result = array();
        $backend = new Backend();
        $net['network'] = $network;
        $values = json_encode($net);
        $response = $backend->configdpRun("opncell processNames", array($values));
        $data = json_decode((string)$response, true);

        if ($data != null) {
            foreach ($data as $index => $process) {
                $topic = ServiceNames::topic($process['Name'] . 'd');
                if ($topic !== null) {
                    $result[] = $this->formatProcessData($index, $process, $topic);
                }
            }
        }

        return $result;
    }

    private function formatProcessData($index, $process, string $topic): array
    {
        $item = [];
        $item['uuid'] = $index;
        $serviceName = ServiceNames::canonical($topic);
        $item['status'] = $this->statusAction($serviceName);
        $item['serviceName'] = $serviceName;
        $item['name'] = $serviceName;
        $item['PID'] = $process['PID'];

        if (isset($this->bindAddress[$topic])) {
            $item['mme_add'] = $this->bindAddress[$topic];
        } else {
            foreach ($process['config'] ?? [] as $configKey => $configValue) {
                $this->extractProcessConfig($item, $configKey, $configValue);
            }
        }

        return $item;
    }
    private function extractProcessConfig(&$item, $configKey, $configValue)
    {
        if (strpos($configKey, '.metrics') !== false) {
            $metrics = $configValue[0];
            $item['metrics_addr'] = $metrics['addr'];
            $item['metrics_port'] = $metrics['port'];
        } elseif (strpos($configKey, 's1ap.server') !== false ||
            strpos($configKey, 'sbi.server') !== false ||
            strpos($configKey, 'gtpu.server') !== false ||
            strpos($configKey, 'ngap.server') !== false) {
            $mme = $configValue[0];
            $item['mme_add'] = $mme['address'];
        } elseif (strpos($configKey, 'tai') !== false) {
            $tac = $configValue[0];
            $item['tac'] = $tac['tac'];
        } elseif (strpos($configKey, 'nsi') !== false) {
            $nsi = $configValue[0];
            $item['sst'] = $nsi['s_nssai']['sst'];
        }
    }

    public function startedServicesAction($network = null): array
    {
        if ($network === null) {
            $settings = (new General())->getNodes();
            $enabled = array_filter(
                ['enablefour', 'enablefiveSA', 'enablefiveNSA', 'enableupf'],
                static fn ($mode) => (string)($settings[$mode] ?? '') === '1'
            );
            $network = count($enabled) === 1 ? reset($enabled) : null;
        }
        $result = $network === null ? [] : $this->getProcessNamesAction($network);
        $this->request = new Request();
        $itemsPerPage = $this->request->getPost('rowCount', 'int', 9999);
        $currentPage = $this->request->getPost('current', 'int', 1);
        $offset = ($currentPage - 1) * $itemsPerPage;
        $searchPhrase = $this->request->getPost('searchPhrase', 'string', '');

        $filteredResult = $this->filterResults($result, $searchPhrase);
        $paginatedResult = array_slice($filteredResult, $offset, $itemsPerPage);
//        return $filteredResult;
        return [
            'total' => count($filteredResult),
            'rowCount' => $itemsPerPage,
            'current' => $currentPage,
            'rows' => $paginatedResult,
        ];
    }

    private function filterResults(array $results, string $searchPhrase): array
    {
        if ($searchPhrase === '') {
            return $results;
        }

        return array_filter($results, function ($item) use ($searchPhrase) {
            foreach ($item as $value) {
                if (strpos($value, $searchPhrase) !== false) {
                    return true;
                }
            }
            return false;
        });
    }

    /**
     * @throws ReflectionException
     */
    public function getStartedServicesAction($uuid = null): array
    {
        return $this->getBase("configs", "configs.config", $uuid);
    }

    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function setStartedServicesAction($uuid): array
    {
        return $this->setBase("configs", "configs.config", $uuid);
    }
}
