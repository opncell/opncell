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

namespace OPNsense\OPNCore\Api;

use OPNsense\Base\BaseModel;
use OPNsense\Base\UserException;
use OPNsense\Core\Backend;
use OPNsense\Core\Config;


use OPNsense\OPNCore\Opncore;
use OPNsense\OPNCore\User;
use OPNsense\OPNCore\General;
use OPNsense\Base\UIModelGrid;
use OPNsense\Base\ApiMutableModelControllerBase;
use Phalcon\Exception;
use Phalcon\Messages\Message;

header("Access-Control-Allow-Origin: *");
class GeneralController extends ApiMutableModelControllerBase
{

    protected static $internalModelName = 'opncore';
    protected static $internalModelClass = '\OPNsense\OPNCore\Opncore';

    public function getModel(): General
    {
        return new General();
    }

    /**
     * @throws \ReflectionException
     */
    public function getAction(): array
    {
        // define list of configurable settings
        $result = array();
        if ($this->request->isGet()) {
            $mdlGeneral = $this->getModel();
            $result['general'] = $mdlGeneral->getNodes();
            $values = json_encode($result) ;
            $g = array($values);
        }
        return $result;
    }

    /**
     * @throws \ReflectionException
     */
    public function getUserAction(): array
    {
        // define list of configurable settings
        $result = array();
        if ($this->request->isGet()) {
            $mdlUser = new  User();
            $result['user'] = $mdlUser->getNodes();
            $values = json_encode($result) ;
            $g = array($values);
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

        $response = $backend->configdRun($serviceName ." " . "status");
        $mynode = "enable".$serviceName;
        $node = str_replace('"', '', $mynode);
        if (strpos($response, "not running") > 0) {
            if ($model->$node->__toString() == 1) {
                $status = "stopped";
            } else {
                $status = "disabled";
            }
        } elseif (strpos($response, "is running") > 0) {
            $status = "running";
        } elseif ($model->enablemmed->__toString() == 0) {
            $status = "disabled";
        } else {
            $status = "unknown";
        }

        return  $status ;
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

    public function reconfigureService()
    {
    }
    public function getProcessNamesAction($network)
    {
        $descriptions = array(
            'mme' => gettext('Mobility Management Entity '),
            'hss' => gettext('Home Subscriber System '),
            'pcrf' => gettext('Policy and Charging Rules Function'),
            'sgwu' => gettext('Serving Gateway User Plane'),
            'ausf' => gettext('Authentication Server Function'),
            'amf' => gettext('Access and Mobility Function'),
            'udm' => gettext('Unified Data Management'),
            'smf' => gettext('Session Management Function'),
            'pcf' => gettext('Policy and Charging Function'),
            'nssf' => gettext('Network Slice Selection Function'),
            'sgwc' => gettext('Serving Gateway Control Plane'),
            'upf' => gettext('User Plane Function'),
            'nrf' => gettext('Network Repository Function'),
            'scp' => gettext('Service Communication Proxy'),
            'bsf' => gettext('Binding Support Function'),
            'mongod' => gettext('Mongo DB'),
            'udr' => gettext('Unified Data Repository'),
        );
        $bindAddress = array(
            'hssd' => gettext('127.0.0.8'),
            'mongod' => gettext('127.0.0.1'),
            'sgwcd' => gettext('127.0.0.3'),
            'pcrfd' => gettext('127.0.0.9'),
        );

        $result = array();
        $backend = new Backend();
        $net['network'] = $network;
        $bindAddrToNotChange = ['sgwcd','mongod','pcrfd','hssd'];
        $val = json_encode($net);
        $response = $backend->configdpRun("opncore processNames", array($val));

        $data = json_decode((string)$response, true);

        if ($data != null) {
            foreach ($data as $index => $process) {
                $item = array();
                $item['uuid']=$index;
                $serviceName =  $process['Name']."d";
                $item['status'] = $this->statusAction($serviceName);
                #This is what we pass to the start function, From the table UI
                $item['serviceName'] = $serviceName;
                $item['name'] = $descriptions[$process['Name']] . " - " . "(" .$process['Name'] .")";
                $item['PID'] = $process['PID'];
                if (in_array($item['serviceName'], $bindAddrToNotChange)) {
                    $item['mme_add'] = $bindAddress[$item['serviceName']];
                } else {
                    //TODO Better way of doing this??
                    foreach ($process['config'] as $configKey => $configValue) {
                        // Check for specific substrings
                        if (strpos($configKey, '.metrics') !== false) {
                            $metrics = $configValue[0];
                            $item['metrics_addr'] = $metrics['addr'];
                            $item['metrics_port'] = $metrics['port'];
                        } elseif (strpos($configKey, 'mongod.bind') !== false) {
                            $mme = $configValue[0];
                            $item['mme_add'] = $mme['address'];
                        } elseif (strpos($configKey, 'freeDiameter') !== false) {
                            $item['freeDiameter'] = $configValue;
                        } elseif (strpos($configKey, 's1ap.server') !== false) {
                            $mme = $configValue[0];
                            $item['mme_add'] = $mme['address'];
                        } elseif (strpos($configKey, 'sbi.server') !== false) {
                            $mme = $configValue[0];
                            $item['mme_add'] = $mme['address'];
                        } elseif (strpos($configKey, 'gtpu.server') !== false) {
                            $mme = $configValue[0];
                            $item['mme_add'] = $mme['address'];
                        } elseif (strpos($configKey, 'ngap.server') !== false) {
                            $mme = $configValue[0];
                            $item['mme_add'] = $mme['address'];
                        } elseif (strpos($configKey, 'tai') !== false) {
                            $tac = $configValue[0];
                            $item['tac'] = $tac['tac'];
                        } elseif (strpos($configKey, 'nsi') !== false) {
                            $nsi = $configValue[0];
                            $item['sst'] =  $nsi['s_nssai']['sst'];
                        }
                    }
                }


                $result[] = $item;
            }
        }
        return $result;
    }

    /**
     * @throws \Exception
     */
    public function startedServicesAction($network): array
    {
        $this->sessionClose();
        $result = $this->getProcessNamesAction($network);
        // fetch query parameters (limit results to prevent out of memory issues)
        $itemsPerPage = $this->request->getPost('rowCount', 'int', 9999);
        $currentPage = $this->request->getPost('current', 'int', 1);
        $offset = ($currentPage - 1) * $itemsPerPage;

        $entry_keys = array_keys($result);
        if ($this->request->hasPost('searchPhrase') && $this->request->getPost('searchPhrase') !== '') {
            $searchPhrase = $this->request->getPost('searchPhrase');
            $entry_keys = array_filter($entry_keys, function ($key) use ($searchPhrase, $result) {
                foreach ($result[$key] as $itemval) {
                    if (strpos($itemval, $searchPhrase) !== false) {
                        return true;
                    }
                }
                return false;
            });
        }
        $formatted = array_map(function ($value) use (&$result) {
            $item = ['#' => $value];
            foreach ($result[$value] as $ekey => $evalue) {
                $item[$ekey] = $evalue;
            }
            return $item;
        }, array_slice($entry_keys, $offset, $itemsPerPage));


        return [
            'total' => count($entry_keys),
            'rowCount' => $itemsPerPage,
            'current' => $currentPage,
            'rows' => $formatted,
        ];

    }

    /**
     * @throws \ReflectionException
     */
    public function getStartedServicesAction($uuid = null): array
    {
        return $this->getBase("configs", "configs.config", $uuid);
    }

    /**
     * @throws \ReflectionException
     * @throws UserException
     */
    public function setStartedServicesAction($uuid): array
    {
        return $this->setBase("configs", "configs.config", $uuid);
    }
}
