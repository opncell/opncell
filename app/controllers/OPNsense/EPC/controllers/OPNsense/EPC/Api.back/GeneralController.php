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
use OPNsense\Core\Config;
use OPNsense\EPC\General;
use OPNsense\EPC\Opncore;
use OPNsense\EPC\OtherConfigs;
use function OPNsense\EPC\Api\count;

class GeneralController extends ApiControllerBase
{
    public function getAction()
    {
        // define list of configurable settings
        $result = array();
        if ($this->request->isGet()) {
            $mdlGeneral = new Opncore();
            $result['general'] = $mdlGeneral->getNodes();
        }
        return $result;
    }


//    public function setAction()
//    {
//        $result = array("result" => "failed");
//        if ($this->request->isPost()) {
//            // load model and update with provided data
//            $mdlGeneral = new Opncore();
//            $mdlGeneral->setNodes($this->request->getPost("opncore"));
//
//            // perform validation
//            $valMsgs = $mdlGeneral->performValidation();
//            foreach ($valMsgs as $field => $msg) {
//                if (!array_key_exists("validations", $result)) {
//                    $result["validations"] = array();
//                }
//                $result["validations"]["general." . $msg->getField()] = $msg->getMessage();
//            }
//
//            // serialize model to config and save
//            if ($valMsgs->count() == 0) {
//                $mdlGeneral->serializeToConfig();
//                Config::getInstance()->save();
//                $result["result"] = "saved";
//            }
//        } else {
//         echo "Failed";
//        }
//        return $result;
//    }

    public function getProcessNamesAction()
    {
        $result = array();
        $backend = new Backend();
        $response = $backend->configdRun("epc processNames");
        $data = json_decode((string)$response, true);
        if ($data != null) {
            foreach ($data as $process) {
                $item = array();
                $item['name'] = $process['Name'];
                $item['PID'] = $process['PID'];
                $result[] = $item;
            }
        }
        return $result;
    }
    public function listRulesetsAction()
    {
        $result = array();
        $this->sessionClose();
        $result['rows'] = $this->getProcessNamesAction();
        $result['rowCount'] = empty($result['rows']) ? 0 :  count($result['rows']);
        $result['total'] = empty($result['rows']) ? 0 : count($result['rows']);
        $result['current'] = 1;
        return $result;
    }

    public function setOtherConfigAction()
    {
        $result = array("result" => "failed");
        if ($this->request->isPost()) {
            // load model and update with provided data
            $mdlGeneral = new General();
            $mdlGeneral->setNodes($this->request->getPost("general"));

            // perform validation
            $valMsgs = $mdlGeneral->performValidation();
            foreach ($valMsgs as $field => $msg) {
                if (!array_key_exists("validations", $result)) {
                    $result["validations"] = array();
                }
                $result["validations"]["general." . $msg->getField()] = $msg->getMessage();
            }

            // serialize model to config and save
            if ($valMsgs->count() == 0) {
                $mdlGeneral->serializeToConfig();
                Config::getInstance()->save();
                $result["result"] = "saved";
            }
        }
        return $result;
    }

    public function getOtherConfigAction()
    {
        // define list of configurable settings
        $result = array();
        if ($this->request->isGet()) {
            $mdlOther = new OtherConfigs();
            $result['service'] = $mdlOther->getNodes();
        }
        return $result;
    }



}
