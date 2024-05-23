<?php
//
///**
// *    Copyright (C) 2018 Michael Muenz <m.muenz@gmail.com>
// *
// *    All rights reserved.
// *
// *    Redistribution and use in source and binary forms, with or without
// *    modification, are permitted provided that the following conditions are met:
// *
// *    1. Redistributions of source code must retain the above copyright notice,
// *       this list of conditions and the following disclaimer.
// *
// *    2. Redistributions in binary form must reproduce the above copyright
// *       notice, this list of conditions and the following disclaimer in the
// *       documentation and/or other materials provided with the distribution.
// *
// *    THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
// *    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
// *    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
// *    AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
// *    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// *    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// *    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// *    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// *    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// *    POSSIBILITY OF SUCH DAMAGE.
// *
// */
//
//
//namespace OPNsense\Base;
//
//namespace OPNsense\OPNCore\Api;
//
//use OPNsense\Base\ApiMutableModelControllerBase;
//use OPNsense\OPNCore\Profile;
//use OPNsense\OPNCore\User;
//use OPNsense\Core\Config;
//use OPNsense\Core\Backend;
//use OPNsense\Phalcon\Filter\Filter;
//
//class UserController extends ApiMutableModelControllerBase
//{
////    protected static $internalModelClass = '\OPNsense\OPNCore\User';
////    protected static $internalModelName = 'user';
//
//
////    public function getAction()
////    {
////        // define list of configurable settings
////        $result = array();
////        $userDetails = array();
////        if ($this->request->isGet()) {
////            $mdlUser = new User();
////            $result['ppppppp'] = $mdlUser->getNodes();
////            $values = json_encode($result);
////            // $values = json_encode($result) ;
////            // $escapedData = str_replace('"', '\"', $values);
////            $g = array($values);
////            $profileClass = new ProfileController();
////            $profile_uuid = 'ad05e7b4-eb40-4aeb-aaf1-9afe6958cfc1';
////            $profile = $profileClass->getAction($profile_uuid);
////
////            foreach ($profile as $detail) {
////                $userDetails["sst"] = $detail['sst'];
////                if ($detail['apn']) {
////                    $userDetails["apn"] = $this->multipart($detail['apn']);
////                }
////                if ($detail['unit']) {
////                    $userDetails["unit"] = $this->multipart($detail['unit']);
////                }
////                if ($detail['arp_capability']) {
////                    $val = $this->multipart($detail['arp_capability']);
////                    if ($val == 'enabled') {
////                        $userDetails["arp_capability"] = '1';
////                    } else {
////                        $userDetails["arp_capability"] = '2';
////                    }
////                }
////                if ($detail['arp_vulnerability']) {
////                    $val = $this->multipart($detail['arp_vulnerability']);
////
////                    if ($val == 'enabled') {
////                        $userDetails["arp_vulnerability"] = '1';
////                    } else {
////                        $userDetails["arp_vulnerability"] = '2';
////                    }
////                }
////                $userDetails["QoS"] = $detail['QoS'];
////            }
////        }
////        return $result;
////    }
//
//    public function multipart($value): string
//    {
//        $selectedKey = " ";
//        $jsonString = json_encode($value);
//        $dataArray = json_decode($jsonString, true);
//        foreach ($dataArray as $command_key => $command_value) {
//            if ($command_value["selected"] === 1) {
//                $selectedKey = $command_key;
//                break;
//            }
//        }
//        return $selectedKey;
//    }
//
//    /**
//     * @throws \ReflectionException
//     */
//    public function searchSubAction()
//    {
//        return $this->searchBase('users.user', array("imsi, name"));
//    }
//
//    public function addSubAction()
//    {
//        return $this->addBase('user', 'users.user');
//    }
//
//    public function getSubAction($uuid = null)
//    {
//        $this->sessionClose();
//        $element = $this->getModel();
//      return $element->getNodes();
//
////        return $this->getBase('user', 'users.user', $uuid);
//    }
//
//    public function delSubAction($uuid): array
//    {
//        $backend = new Backend();
//        $details = $this->getSubAction($uuid);
//        $imsi = $details['imsi'];
//        $user['imsi'] = $imsi;
//        $values = json_encode($user);
//        $backend->configdpRun("opncore deleteUser", array($values));  //remove user from db
//        return $this->delBase('users.user', $uuid);     //remove them from opnsense internal db as well
//    }
//
//    /**
//     * @throws \Exception
//     */
////    public function setAction(): array
////    {
////        $result = array("result" => "failed");
////        $backend = new Backend();
////        $selectedKey = null;
////        $profile_uuid = null;
////        $mdlUser = new User();
////        $userDetails = array();
////        $db_commands = ["add" => "customAdd", "add_ip" => "add",
////        "addT1" => "addT1", "adddT1_ip" => "addT1"];
////        $mdlUser->setNodes($this->request->getPost("user"));
////        $valMsgs = $mdlUser->performValidation();
////        foreach ($valMsgs as $field => $msg) {
////            if (!array_key_exists("validations", $result)) {
////                $result["validations"] = array();
////            }
////            $result["validations"]["user." . $msg->getField()] = $msg->getMessage();
////        }
////
////        $result = $this->getAction();
////        //quick loop coz key command, is always in first position.
////        foreach ($result as $Key => $value) {
////            if ($Key == "command") {
////                $selectedKey = $this->multipart($value);
////            }
////            if ($Key == "profile") {
////                $profile_uuid = $this->multipart($value);
////            }
////        }
////        foreach ($db_commands as $key => $value) {
////            if (array_key_exists($selectedKey, $db_commands)) {
////                $selectedKey = $value;
////            }
////        }
////        $profileClass = new ProfileController();
//////        $profile_uuid = 'ad05e7b4-eb40-4aeb-aaf1-9afe6958cfc1';
////        $profile = $profileClass->getAction($profile_uuid);
////
////        $userDetails["command"] = $selectedKey;
////        $userDetails["imsi"] = $mdlUser->imsi->__toString();
////        $userDetails["ki"] = $mdlUser->ki->__toString();
////        $userDetails["opc"] = $mdlUser->opc->__toString();
////
////        foreach ($profile as $detail) {
////            $userDetails["sst"] = $detail['sst'];
////            $userDetails["ip"] = $detail['ip'];
////            $userDetails["dl"] = $detail['dl'];
////            $userDetails["ul"] = $detail['ul'];
////            $userDetails["QoS"] = $detail['QoS'];
////            $userDetails["arp_priority"] = $detail['arp_priority'];
////
////            if ($detail['apn']) {
////                $userDetails["apn"] = $this->multipart($detail['apn']);
////            }
////            //TODO Use cater for other units as well.
////            if ($detail['unit']) {
////                $val = $this->multipart($detail['unit']);
////                if ($val == 'Mbs') {
////                    $userDetails["unit"] = '1';
////                } else {
////                    $userDetails["unit"] = '2';
////                }
////            }
////            if ($detail['arp_capability']) {
////                $val = $this->multipart($detail['arp_capability']);
////                if ($val == 'enabled') {
////                    $userDetails["arp_capability"] = '1';
////                } else {
////                    $userDetails["arp_capability"] = '2';
////                }
////            }
////            if ($detail['arp_vulnerability']) {
////                $val = $this->multipart($detail['arp_vulnerability']);
////
////                if ($val == 'enabled') {
////                    $userDetails["arp_vulnerability"] = '1';
////                } else {
////                    $userDetails["arp_vulnerability"] = '2';
////                }
////            }
////        }
////
////        $values = json_encode($userDetails);
////
////        //serialize model to config and save
////        if ($valMsgs->count() == 0) {
////            $response = $backend->configdpRun("opncore saveUsers", array($values));
////            $mdlUser->serializeToConfig();
////            Config::getInstance()->save();
////            $result = array(
////                "result" => "saved",
////            );
////        }
////        return $result;
////    }
////
////    public function fetchUsersAction(): array
////    {
////        $result_rows = array();
////        $backend = new Backend();
////        $response = $backend->configdRun("opncore showUsers");
////        $data = json_decode((string)$response, true);
////        if ($data != null) {
////            foreach ($data as $process) {
////                $item = array();
////                #$item['opc'] = $process['opc'];
////    //          $item['ki'] = $process['k'];
////                $item['imsi'] = $process['imsi'];
////                $apn = $process['apn'];
////                $apn_1 = $apn[0];
////                $apn_2 = $apn[1];
////                $apn_3 = $apn[2];
////                $item['apn'] = "$apn_1 $apn_3 $apn_2";
////
////                $result_rows[] = $item;
////            }
////            $result['rows'] = $result_rows;
////            $result['rowCount'] = count($result['rows']);
////            $result['total'] = count($result['rows']);
////            $result['current'] = 1;
////        }
////        return $result;
////    }
////
////    /**
////     * @throws \Exception
////     */
////
////    //So this function is called from the UI,(Edit button) with the imsi. The particular user is picked from the db,
////    // then the user model is updated with those details. This updated node is then pushed to the UI to be edited.
////    public function getUserAction($imsi)
////    {
////        $backend = new Backend();
////        $user = array();
////        $user['imsi'] = $imsi;
////        $values = json_encode($user);
////        $response = $backend->configdpRun("opncore getUser", array($values));
////        $data = json_decode((string)$response, true);
////        $result['user'] = array();
////        $mdlUser = new User();
////        if ($data != null) {
////            foreach ($data as $process) {
////                $item = array();
////                $mdlUser->setNodes(["imsi"=>$process['imsi']]);
////                $mdlUser->setNodes(["opc"=>$process['opc']]);
////                $mdlUser->setNodes(["opc"=>$process['opc']]);
////                $mdlUser->setNodes(["QoS"=>$process['index']]);
////                $mdlUser->setNodes(["arp_capability"=>$process['arp_capability']]);
////                $mdlUser->setNodes(["arp_vulnerability"=>$process['arp_vulnerability']]);
////                $mdlUser->setNodes(["arp_priority"=>$process['priority_level']]);
////                $mdlUser->setNodes(["dl"=>$process['downlink_value']]);
////                $mdlUser->setNodes(["dl_unit"=>$process['downlink_unit']]);
////                $mdlUser->setNodes(["ul"=>$process['uplink_value']]);
////                $mdlUser->setNodes(["ul_unit"=>$process['uplink_unit']]);
////                $apn = $process['apn'];
////                $apn_1 = $apn[0];
////                $apn_2 = $apn[1];
////                $apn_3 = $apn[2];
////                $item['apn'] = "$apn_1 $apn_3 $apn_2";
////                $mdlUser->setNodes(["apn"=>$item['name']]);
////            }
////            $result['user'] = $mdlUser->getNodes();
////        }
////        return $result;
////    }
////    public function deleteUserAction($imsi)
////    {
////        $backend = new Backend();
////        $user['imsi'] = $imsi;
////        $values = json_encode($user);
////        $response = $backend->configdpRun("opncore deleteUser", array($values));
////        $response_show = $backend->configdpRun("opncore showUsers");
////        $data = json_decode((string)$response_show, true);
////        if ($data != null) {
////            foreach ($data as $process) {
////                $item = array();
////
////                $item['opc'] = $process['opc'];
////                //$item['ki'] = $process['k'];
////                $item['imsi'] = $process['imsi'];
////                $apn = $process['apn'];
////                $apn_1 = $apn[0];
////                $apn_2 = $apn[1];
////                $apn_3 = $apn[2];
////                $item['apn'] = "$apn_1 $apn_3 $apn_2";
////
////                $result_rows[] = $item;
////            }
////            $result['rows'] = $result_rows;
////            $result['rowCount'] = count($result['rows']);
////            $result['total'] = count($result['rows']);
////            $result['current'] = 1;
////        }
////        return $result;
////    }
//}
