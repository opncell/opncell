<?php

/**
 *    Copyright (C) 2023 Digital Solutions <support@ds.co.ug>
 *    Copyright (C) 2023 WIRE LAB
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

namespace OPNsense\OPNCell\Api;

use Phalcon\Messages\Message;
use OPNsense\Base\ApiMutableModelControllerBase;
use OPNsense\Base\UserException;
use OPNsense\Core\Config;
use OPNsense\Core\Backend;
use OPNsense\OPNCell\User;
use OPNsense\Phalcon\Filter\Filter;
use ReflectionException;

class BulkController extends ApiMutableModelControllerBase
{
    protected static $internalModelClass = '\OPNsense\OPNCell\Bulk';
    protected static $internalModelName = 'bulk';

    public function multipart($value): array
    {
        $selectedKey = [];
        $jsonString = json_encode($value);
        $dataArray = json_decode($jsonString, true);
        foreach ($dataArray as $command_key => $command_value) {
            if ($command_value["selected"] === 1) {
                $selectedKey[] = $command_key;
            }
        }
        return $selectedKey;
    }
    public function multipartAPNS($value): array
    {
        $selectedKey = [];
        $jsonString = json_encode($value);
        $dataArray = json_decode($jsonString, true);
        foreach ($dataArray as $command_key => $command_value) {
            if ($command_value["selected"] === 1) {
                $selectedKey[] = $command_key;
            }
        }
        return $selectedKey;
    }

    public function getAction($uuid = null): array
    {
//        $this->sessionClose(); # no longer needed or supported RPH 2026-01-24

        return $this->getBase('bulk', 'bulks.bulk', $uuid);
    }

    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function addBulkSubAction(): array
    {
        return $this->addBase('bulk', 'bulks.bulk');
    }

    /**
     * @throws ReflectionException
     */
    public function saveBulkUsersAction($uuid): array
    {
        $backend = new Backend();
        $mdlUser = new User();
        $userRepository = new UserRepository($backend);
        session_start();
        $result['status'] = "Failed";
        $duplicates = array();
        $profile = $this->getAction($uuid);
        $selected_profile_uuid = $this->multipart($profile['bulk']['profile']);
        $numberOfProfiles = count($selected_profile_uuid);
        $profileClass = new ProfileController();
        $userClass = new UserController();

        if (isset($_SESSION['fileValues'])) {
            $outputKeyValue = $_SESSION['fileValues'];
            foreach ($outputKeyValue as $item) {
                $userDetails = [];
                $index = 0;
                $sub_user = [];
                $sub_user['count'] = $numberOfProfiles;
                $userDetails["imsi"] = $item['imsi'];
                $userDetails["ki"] = $item['ki'];
                $userDetails["opc"] = $item['opc'];

                foreach ($selected_profile_uuid as $p_uuid) {
                    $profile = $profileClass->getProfileAction($p_uuid);
                    $index += 1;
                    $userDetails['sst'] = $profile['profile']['sst'];
                    $userDetails["dl"] = $profile['profile']['dl'];
                    $userDetails["ul"] = $profile['profile']['ul'];
                    $userDetails["QoS"] = $profile['profile']['QoS'];
                    $userDetails["arp_priority"] = $profile['profile']['arp_priority'];
                    $userDetails["apn"] = $profile['profile']['apn'];
                    $userDetails = $userClass->getUserDetails($profile['profile'], $userDetails);
                    $sub_user[$index] = $userDetails;
                }
                $data = $userRepository->saveUser($sub_user);
                if ($data == "Duplicate") {
                    $duplicates[] = $userDetails["imsi"];
                }
            }
        }
        else {
            echo "Error: outputKeyValue not found in session.";
        }

        return $duplicates;
    }
}
