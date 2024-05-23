<?php

/**
 *    Copyright (C) 2023 Digital Solutions <support@ds.co.ug>
 *
 *    All rights reserved.
 *
 *    Redistribution and use in source and binary forms, with or without
 *    modification, are permitted provided that the following conditions are met:
 *
 *    1. Redistributions of source code must retain the above copyright notice,
 *       this list of conditions and the following disclaimer.
 *
 *    2. Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *
 *    THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 *    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 *    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *    AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 *    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 *    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 *    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 *    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 *    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *    POSSIBILITY OF SUCH DAMAGE.
 *
 */

namespace OPNsense\Base;

namespace OPNsense\OPNCore\Api;

use OPNsense\Base\ApiMutableModelControllerBase;
use OPNsense\OPNCore\Profile;
use OPNsense\Core\Config;

class ProfileController extends ApiMutableModelControllerBase
{
    protected static $internalModelName = 'profile';
    protected static $internalModelClass = '\OPNsense\OPNCore\Profile';

//    public function getAction()
//    {
//        // define list of configurable settings
//        $result = array();
//        if ($this->request->isGet()) {
//            $mdlUser = new Profile();
//            $result['profile'] = $mdlUser->getNodes();
//            $values = json_encode($result);
//            // $values = json_encode($result) ;
//            // $escapedData = str_replace('"', '\"', $values);
//            $g = array($values);
//        }
//        return $result;
//    }

    /**
     * update HelloWorld settings
     * @return array status
     */
//    public function setAction()
//    {
//        $result = array("result"=>"failed");
//        if ($this->request->isPost()) {
//            echo("here");
//            // load model and update with provided data
//            $mdlProfile = new Profile();
//            $mdlProfile->setNodes(['name'=>"Test"]);
//
//            // perform validation
//            $valMsgs = $mdlProfile->performValidation();
//            foreach ($valMsgs as $field => $msg) {
//                if (!array_key_exists("validations", $result)) {
//                    $result["validations"] = array();
//                }
//                $result["validations"]["profile.".$msg->getField()] = $msg->getMessage();
//            }
//
//            // serialize model to config and save
//            if ($valMsgs->count() == 0) {
//                $mdlProfile->serializeToConfig();
//                Config::getInstance()->save();
//                $result["result"] = "saved";
//            }
//        }
//        return $result;
//    }

    public function addProfileAction()
    {
        return $this->addBase('profile', 'profiles.profile');
    }
    public function getAction($uuid = null)
    {
        $this->sessionClose();
        return $this->getBase('profile', 'profiles.profile', $uuid);
    }
//    public function delAclAction($uuid)
//    {
//        return $this->delBase('profiles.profile', $uuid);
//    }

    public function setProfileAction($uuid): array
    {
        return $this->setBase('profile', 'profiles.profile', $uuid);
    }
}
