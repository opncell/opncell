<?php

/*

 * Copyright (C) 2023 Digital Solutions
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


use OPNsense\OPNCore\User;
use OPNsense\OPNCore\General;
use OPNsense\Base\UIModelGrid;
use OPNsense\Base\ApiMutableModelControllerBase;
use Phalcon\Messages\Message;

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
    public function getAction()
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
    public function getUserAction()
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
    public function setNetwork($network): string
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
            $result = "saved";
        }
        return $result;
    }

    public function getProcessNamesAction(): array
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
            'bsf' => gettext('Binding Support Function')
        );

        $result = array();
        $backend = new Backend();
        $response = $backend->configdRun("opncore processNames");
        $data = json_decode((string)$response, true);

        if ($data != null) {
            foreach ($data as $process) {
                $item = array();

                $item['name'] = $descriptions[$process['Name']] . " - " . "(" .$process['Name'] .")";
                $item['PID'] = $process['PID'];
                $item['network_name'] = $process['network_name'];

                //TODO Better way of doing this??
                foreach ($process['config'] as $configKey => $configValue) {
                    // Check for specific substrings
                    if (strpos($configKey, '.metrics') !== false) {
                        $metrics = $configValue[0];
                        $item['metrics_addr'] = $metrics['addr'];
                        $item['metrics_port'] = $metrics['port'];
                    } elseif (strpos($configKey, 'db_uri') !== false) {
                        $item['db_uri'] = $configValue;
                    } elseif (strpos($configKey, 'freeDiameter') !== false) {
                        $item['freeDiameter'] = $configValue;
                    } elseif (strpos($configKey, 's1ap') !== false) {
                        $mme = $configValue[0];
                        $item['mme_add'] = $mme['addr'];
                    } elseif (strpos($configKey, 'ngap') !== false) {
                        $amf = $configValue[0];
                        $item['amf_add'] = $amf['addr'];
//                    }
//                    elseif (strpos($configKey, 'dns') !== false) {
//                        $dns = $configValue[0];
//                        $dns_t = $configValue[1];
//                        $item['dns'] = "$dns $dns_t";
                    } elseif (strpos($configKey, 'tai') !== false) {
                        $tac = $configValue[0];
                        $item['tac'] = $tac['tac'];
                    } elseif (strpos($configKey, 'nsi') !== false) {
                        $nsi = $configValue[0];
                        $item['sst'] =  $nsi['s_nssai']['sst'];
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
    public function startedServicesAction(): array
    {
        $result = array();
        $this->sessionClose();
        $result['rows'] = $this->getProcessNamesAction();
        // sort by description

        $result['rowCount'] = empty($result['rows']) ? 0 :  count($result['rows']);
        $result['total'] = empty($result['rows']) ? 0 : count($result['rows']);
        $result['current'] = 1;
        return $result;
    }

    /**
     * @throws \ReflectionException
     */
    public function getStartedServicesAction($uuid = null)
    {
        return $this->getBase("configs", "configs.config", $uuid);
    }

    /**
     * @throws \ReflectionException
     * @throws UserException
     */
    public function setStartedServicesAction($uuid)
    {
        return $this->setBase("configs", "configs.config", $uuid);
    }
}
