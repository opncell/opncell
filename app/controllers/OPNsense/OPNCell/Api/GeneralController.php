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
use OPNsense\Core\Backend;
use OPNsense\Core\Config;


use OPNsense\OPNCell\Opncore;
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

    protected static $internalModelName = 'opncore';
    protected static $internalModelClass = '\OPNsense\OPNCell\Opncore';

    /**
     * @throws ReflectionException
     */
    public function getAction(): array
    {
        $result = array();
        if ($this->request->isGet()) {
//            $mdlGeneral = $this->getModel();
            $mdlGeneral = new General();
            $result['general'] = $mdlGeneral->getNodes();
        }
        return $result;
    }

    public function getUserAction(): array
    {
        $result = array();
        if ($this->request->isGet()) {
            $mdlUser = new  User();
            $result['user'] = $mdlUser->getNodes();
        }
        return $result;
    }
    /**
     * @throws \Exception
     */
    public function setNetwork($network): array
    {
        $result = array("result" => "failed");
        $mdlGeneral = new General();
        $mdlGeneral->setNodes($this->request->getPost("general"));
        $mdlGeneral->setNodes(["enablefour" => "0"]);
        $mdlGeneral->setNodes(["enablefiveSA" => "0"]);
        $mdlGeneral->setNodes(["enablefiveNSA" => "0"]);
        $mdlGeneral->setNodes(["enableupf" => "0"]);
        $mdlGeneral->setNodes([$network => "1"]);
        $valMsgs = $mdlGeneral->performValidation();
        foreach ($valMsgs as $field => $msg) {
            if (!array_key_exists("validations", $result)) {
                $result["validations"] = array();
            }
            $result["validations"]["general." . $msg->getField()] = $msg->getMessage();
        }
        //serialize model to config and save
        if ($valMsgs->count() == 0) {
            $mdlGeneral->serializeToConfig();
            Config::getInstance()->save();
            $result["result"] = "saved";
        }
        return $result;
    }
    public function statusAction($serviceName)
    {
        $backend = new Backend();
        $model = new Opncore();
        try {
            $response = $backend->configdRun($serviceName ." " . "status");
            $mynode = "enable".$serviceName;
            $node = str_replace('"', '', $mynode);
            if (strpos($response, "not running") > 0) {
                $status = ($model->$node->__toString() == 1) ? "stopped" : "disabled";
            } elseif (strpos($response, "is running") > 0) {
                $status = "running";
            } elseif ($model->enablemmed->__toString() == 0) {
                $status = "disabled";
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
        $result = array();
        $backend = new Backend();
        $parts = explode(",", $params);
        $net['server'] = $parts[0];
        $net['pid'] = $parts[1];
        $net['ip'] = $parts[2];
        $val = json_encode($net);
        $backend->configdpRun("opncore editServerConf", array($val));
        //Restart that service
        $backend->configdRun($net['server'] . ' '. 'stop');
        $backend->configdRun($net['server'] . ' '. 'start');
    }

    private array $processDescriptions = [
        'mme' => 'Mobility Management Entity ',
        'hss' => 'Home Subscriber System ',
        'pcrf' => 'Policy and Charging Rules Function',
        'sgwu' => 'Serving Gateway User Plane',
        'ausf' => 'Authentication Server Function',
        'amf' => 'Access and Mobility Function',
        'udm' => 'Unified Data Management',
        'smf' => 'Session Management Function',
        'pcf' => 'Policy and Charging Function',
        'nssf' => 'Network Slice Selection Function',
        'sgwc' => 'Serving Gateway Control Plane',
        'upf' => 'User Plane Function',
        'nrf' => 'Network Repository Function',
        'scp' => 'Service Communication Proxy',
        'bsf' => 'Binding Support Function',
        'mongod' => 'Mongo DB',
        'udr' => 'Unified Data Repository',
    ];

    private array $bindAddress = [
        'hssd' => '127.0.0.8',
        'mongod' => '127.0.0.1',
        'sgwcd' => '127.0.0.3',
        'pcrfd' => '127.0.0.9',
    ];

    public function getProcessNamesAction($network): array
    {
        $result = array();
        $backend = new Backend();
        $net['network'] = $network;
        $values = json_encode($net);
        $response = $backend->configdpRun("opncore processNames", array($values));
        $data = json_decode((string)$response, true);

        if ($data != null) {
            foreach ($data as $index => $process) {
                $item = $this->formatProcessData($index, $process);
                $result[] = $item;
            }
        }

        return $result;
    }

    private function formatProcessData($index, $process): array
    {
        $item = [];
        $item['uuid'] = $index;
        $serviceName = $process['Name'] . "d";
        $item['status'] = $this->statusAction($serviceName);
        $item['serviceName'] = $serviceName;
        $item['name'] = $this->processDescriptions[$process['Name']] . " - (" . $process['Name'] . ")";
        $item['PID'] = $process['PID'];

        if (isset($this->bindAddress[$serviceName])) {
            $item['mme_add'] = $this->bindAddress[$serviceName];
        } else {
            foreach ($process['config'] as $configKey => $configValue) {
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

    public function startedServicesAction($network): array
    {
        $this->sessionClose();
        $result = $this->getProcessNamesAction($network);

        $itemsPerPage = $this->request->getPost('rowCount', 'int', 9999);
        $currentPage = $this->request->getPost('current', 'int', 1);
        $offset = ($currentPage - 1) * $itemsPerPage;
        $searchPhrase = $this->request->getPost('searchPhrase', 'string', '');

        $filteredResult = $this->filterResults($result, $searchPhrase);
        $paginatedResult = array_slice($filteredResult, $offset, $itemsPerPage);

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
