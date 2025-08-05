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

namespace OPNsense\OPNCell\Api;

use OPNsense\Base\ApiMutableModelControllerBase;
use OPNsense\Base\UIModelGrid;
use OPNsense\Base\UserException;
use OPNsense\Core\Config;
use OPNsense\Core\Backend;
use OPNsense\Mvc\Request;
use ReflectionException;

class ProfileController extends ApiMutableModelControllerBase
{

    protected static $internalModelClass = '\OPNsense\OPNCell\Profile';
    protected static $internalModelName = 'profile';

    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function addProfileAction(): array
    {
        return $this->addBase('profile', 'profiles.profile');
    }



    /**
     * @throws ReflectionException
     */
    public function searchProfileAction(): array
    {
        $profile_array = $this->searchBase('profiles.profile', array("apn"));
        $profile_array =  $this->searchBase(
            'profiles.profile',
            null,
            "description",
            array("apn")
        );
        $user = new UserController();
        $profile_user = $user->profileAndUsersListAction();

        // Create a mapping of counts
        $counts = [];
        foreach ($profile_user as $name => $count) {
            $counts[$name] = $count;
        }

        // Loop through the first array to attach counts
        foreach ($profile_array["rows"] as &$item) {
            $name = $item["apn"];
            $item["count"] = $counts[$name] ?? "none";
            $profile_array[] = $item;
        }

        return $profile_array;
    }

    /**
     * @throws ReflectionException
     */
    public function singleSearchAction($profile): array
    {
        $customProfile = [];
        $r = $this->searchBase('profiles.profile', array("apn"));
        $APNArray = explode(",", $profile);

        foreach ($r['rows'] as $data) {
            $customProfile[$data['uuid']] = array("value" => $data['apn'], "selected" => 0);
        }

// Iterate over the APNArray to set selected to 1 for matching APNs
        foreach ($APNArray as $apn) {
            foreach ($r['rows'] as $data) {
                if ($data['apn'] == $apn) {
                    $customProfile[$data['uuid']]['selected'] = 1;
                }
            }
        }


        return $customProfile;
    }

    public function getSingleSubAction($imsi): array
    {
        $backend = new Backend();
        $profileClass = new ProfileController();
        $userRepository = new UserRepository($backend);
        $data = $userRepository->getUser($imsi);
        $item = array();
        if ($data != null) {
            foreach ($data as $process) {
                $item['imsi'] = $process['imsi'];
                $item['attached'] = $process['apn'];
            }
        }
        $customProfile = [];
        $r = $this->searchBase('profiles.profile', array("apn"));
        $APNArray = explode(",", $item['attached']);

        foreach ($r['rows'] as $data) {
            $customProfile[$data['uuid']] = array("value" => $data['apn'], "selected" => 0);
        }

// Iterate over the APNArray to set selected to 1 for matching APNs
        foreach ($APNArray as $apn) {
            foreach ($r['rows'] as $data) {
                if ($data['apn'] == $apn) {
                    $customProfile[$data['uuid']]['selected'] = 1;
                }
            }
        }

        $item['profile'] = $customProfile;
        $details['user'] = $item;
        return $details;
    }


    /**
     * @throws ReflectionException
     */
    public function getProfileAction($uuid = null): array
    {
        $this->sessionClose();
        return $this->getBase('profile', 'profiles.profile', $uuid);
    }

    /**
     * @throws ReflectionException
     */
    public function editProfileAction($uuid = null): array
    {
        $this->sessionClose();
        return $this->getBase('profile', 'profiles.profile', $uuid);
    }

    public function multipart($value): array
    {
        $apn = [];
        $jsonString = json_encode($value);
        $dataArray = json_decode($jsonString, true);
        $count = 0;
        foreach ($dataArray as $command_key => $command_value) {
            if ($command_value["selected"] === 1) {
                $count++;
                $apn['apn'.$count] = $command_key;
            }
        }
        return $apn;
    }

    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function setProfileAction($uuid): array
    {
        $backend = new Backend();
        $this->request = new Request();
        $newProfile = $this->request->getPost('profile'); //the new values for that profile
        $profileName = $newProfile['apn'];

        $user = new UserController();
        $userProfileArray = $user->searchSubAction();
        $newProfile['profileName'] = $profileName;

        // Filter $userProfileArray for 'profile' equal to $profileName
        $resultArray = array_filter($userProfileArray['rows'], function ($row) use ($profileName) {
            return in_array($profileName, explode(',', $row['profile']));
        });

        $imsiArray = array_column($resultArray, 'imsi');
        $newProfile['arp_capability'] = $newProfile['arp_capability'] === 'enabled' ? '1' : '2';
        $newProfile['arp_vulnerability'] = $newProfile['arp_vulnerability'] === 'enabled' ? '1' : '2';

        //cascade the changes of the profile, to the attached users.
        foreach ($imsiArray as $imsi) {
            $newProfile['imsi'] = $imsi;
            $values = json_encode($newProfile);
            $backend->configdpRun("opncore updateUser", array($values));
        }
        return $this->setBase('profile', 'profiles.profile', $uuid);
    }

    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function deleteProfileAction($uuid): array
    {
        return $this->delBase('profiles.profile', $uuid);
    }
}
