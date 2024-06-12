<?php

/**
 *    Copyright (C) 2023 Digital Solutions <support@ds.co.ug>
 *    Copyright (C) 2023 Wire Labs
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

use Exception;
use OPNsense\Base\ApiMutableModelControllerBase;
use OPNsense\OPNCore\Api\FileUploadService;
use OPNsense\Base\UserException;
use OPNsense\OPNCore\Api\UserRepository;
use OPNsense\Core\Config;
use OPNsense\Core\Backend;
use OPNsense\Phalcon\Filter\Filter;
use ReflectionException;

header("Access-Control-Allow-Origin: *");


class UserController extends ApiMutableModelControllerBase
{

    protected static $internalModelClass = '\OPNsense\OPNCore\User';
    protected static $internalModelName = 'user';


    public function multipartValues($value, $key): array
    {
        $apn = [];
        $jsonString = json_encode($value);
        $dataArray = json_decode($jsonString, true);
        foreach ($dataArray as $command_key => $command_value) {
            if ($command_value["selected"] === 1) {
                $apn[$key] = $command_key;
            }
        }
        return $apn;
    }

    public function multipart($value): array
    {
        $selected_apn = [];
        $jsonString = json_encode($value);
        $dataArray = json_decode($jsonString, true);
        foreach ($dataArray as $command_key => $command_value) {
            if ($command_value["selected"] === 1) {
                $selected_apn[] = $command_key;
            }
        }
        return $selected_apn;
    }
    public function multipartAPN($value): array
    {
        $apn = [];
        $jsonString = json_encode($value);
        $dataArray = json_decode($jsonString, true);
        $count = 0;
        foreach ($dataArray as $command_key => $command_value) {
            if ($command_value["selected"] === 1) {
                $count+=1;
                $apn['apn'] = $command_key;
            }
        }
        return $apn;
    }


    /**
     * @throws ReflectionException
     */

    public function searchSubAction(): array
    {
        $backend = new Backend();
        $userRepository = new UserRepository($backend);
        $data = $userRepository->getUsers();
        $details = [];
        if ($data != null) {
            foreach ($data as $index => $process) {
                $item = array();
                $item['uuid']=$index;
                $item['imsi'] = $process['imsi'];
                $item['profile'] = $process['apn'];
                $details[] = $item;
            }
        }

        // fetch query parameters (limit results to prevent out of memory issues)
        $itemsPerPage = $this->request->getPost('rowCount', 'int', 9999);
        $currentPage = $this->request->getPost('current', 'int', 1);
        $offset = ($currentPage - 1) * $itemsPerPage;
        $searchPhrase = $this->request->getPost('searchPhrase', 'string', '');

        $filteredResult = $this->filterResults($details, $searchPhrase);
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


    //Get the correlation between users and profiles.

    /**
     * @throws ReflectionException
     */
    public function profileAndUsersListAction(): array
    {
        $result = [];
        $user = $this->searchSubAction();
        if (count($user) > 0) {
            $profiles = array_column($user['rows'], 'profile');
            $initialProfileCount = [];
            #Cater for situations where one imsi has multiple profiles attached.
            foreach ($profiles as $profile) {
                $split_elements = explode(",", $profile);
                $initialProfileCount = array_merge($initialProfileCount, $split_elements);
            }
            $finalProfileCount = array_count_values($initialProfileCount);
            foreach ($finalProfileCount as $profile => $count) {
                $result[$profile] = $count;
            }
        }

        return  $result;
    }
    public function getSubAction($uuid = null): array
    {
        $this->sessionClose();

        return $this->getBase('user', 'users.user', $uuid);
    }

    /**
     * @throws ReflectionException
     */
    public function editSubAction($uuid): array
    {
        $this->sessionClose();
        $profile_uuid = null;
        $user_array = $this->getBase('user', 'users.user', $uuid);
        foreach ($user_array as $user_record) {
            if ($user_record['profile']) {
                $profile_uuid = $this->multipart($user_record['profile']);
            }
        }
        $profileClass = new ProfileController();
        $profile= $profileClass->getProfileAction($profile_uuid);

        //return the user + the details of the serviceType/profile they are attached to
        return array_merge($user_array, $profile);
    }


    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function deleteSubAction($uuid)
    {

        $user = $this->getBase('user', 'users.user', $uuid);
        $imsi = $user['user']['imsi'];
        $backend = new Backend();
        $userRepository = new UserRepository($backend);
         //remove user from db
        $db_result = $userRepository->deleteUser($imsi);
        if ($db_result == "deleted") {
            return $this->delBase('users.user', $uuid);
        }
    }
    public function deleteSubFromDBAction($imsi)
    {
        $backend = new Backend();
        $userRepository = new UserRepository($backend);
        $db_result = $userRepository->deleteUser($imsi);
        if ($db_result == "deleted") {
            return array("result"=>"success");
        } else {
            return array("result"=>"failed");
        }
    }

//    public function searchSubAction(): array
//    {
//        $profile_array = $this->searchBase('users.user', array("imsi","profile"));
//        return $profile_array;
//    }
    /**
     * @throws ReflectionException
     * @throws UserException
     */
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
        $allProfiles = $profileClass->singleSearchAction($item['attached']);
        $item['profile'] = $allProfiles;
        $details['user'] = $item;
        return $details;
    }

    /**
     * @throws ReflectionException
     * @throws Exception
     */
    public function setSubAction($imsi): array
    {
        $backend = new Backend();
        $userDetails = [];
        $updatedUserDetails = $this->request->getPost('user');

        $userRepository = new UserRepository($backend);
        $data = $userRepository->getUser($imsi);
        if ($data != null) {
            foreach ($data as $process) {
                $userDetails['imsi'] = $process['imsi'];
                $userDetails['ki'] = $process['ki'];
                $userDetails['opc'] = $process['opc'];
            }
        }
        $index = 0;
        $profileIDS = $updatedUserDetails['profile'];
        $userClass = new UserController();
        $profileClass = new ProfileController();
        $userRepository = new UserRepository($backend);
        $profileList = explode(",", $profileIDS);
        $numberOfProfiles = count($profileList);
        $sub_user['count'] = $numberOfProfiles;
        if ($profileIDS != "") {
            $this->deleteSubFromDBAction($imsi);
            foreach ($profileList as $profileID) {
                $profile = $profileClass->getProfileAction($profileID);
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
        }
        if ($data != "Success") {
            return array("result"=>"Failed");
        } else {
            return array("result"=>"success");
        }
//            return $this->setBase('user', 'users.user', $uuid);
//        }
    }

    # bulk insertion of users

    public function uploadAction():array
    {
        global $outputKeyValue;
        $fileUploadService = new FileUploadService();
        $result = ["result" => "failed"];
        if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_FILES["file"])) {
            $file = $_FILES["file"];

            if ($file["error"] === UPLOAD_ERR_OK) {
                $outputKeyValue = $fileUploadService->processFile($file);
            } else {
                echo "Error: Failed to upload file.";
            }
        } else {
            return $result;
        }

        return $outputKeyValue;
    }

    /**
     * @throws ReflectionException
     * @throws UserException
     * @throws Exception
     */
    public function addSubAction()
    {
        $userDetails = array();
        $backend = new Backend();
        $userRepository = new UserRepository($backend);
        $userUUID = $this->addBase('user', 'users.user');
        if ($userUUID['result'] == 'saved') {
            $uuid = $userUUID['uuid'];
            $selected_profile_uuid = [];
            $sub = [];
            if ($uuid) {
                $record = $this->getSubAction($uuid);
                foreach ($record as $user_record) {
                    $userDetails["imsi"] = $user_record['imsi'];
                    $userDetails["ki"] = $user_record['ki'];
                    $userDetails["opc"] = $user_record['opc'];
                    $userDetails["ip"] = $user_record['ip'];
                    if ($user_record['profile']) {
                        $selected_profile_uuid = $this->multipart($user_record['profile']);
                    }
                }
                $numberOfProfiles = count($selected_profile_uuid);
                $profileClass = new ProfileController();
                $index = 0;
                $sub['count'] = $numberOfProfiles;
                foreach ($selected_profile_uuid as $p_uuid) {
                    $profile = $profileClass->getProfileAction($p_uuid);
                    $index+=1;
                    $userDetails['sst'] = $profile['profile']['sst'];
                    $userDetails["dl"] = $profile['profile']['dl'];
                    $userDetails["ul"] = $profile['profile']['ul'];
                    $userDetails["QoS"] = $profile['profile']['QoS'];
                    $userDetails["arp_priority"] = $profile['profile']['arp_priority'];
                    $userDetails["apn"] = $profile['profile']['apn'];
                    $userDetails = $this->getUserDetails($profile['profile'], $userDetails);
                    $sub[$index] = $userDetails;
                }
                $data = $userRepository->saveUser($sub);
                if ($data != "Success") {
                    $this->delBase('users.user', $uuid);
                    return array("result"=>"failed");
                } else {
                    return array("result"=>"success");
                }
            } else {
                return array("result"=>"failed");
            }
        } else {
            return $userUUID;
        }
    }

    /**
     * @param $profile1
     * @param array $userDetails
     * @return array
     */
    public function getUserDetails($profile1, array $userDetails): array
    {
        $val = $this->multipart($profile1['arp_capability']);
        if ($val == 'enabled') {
            $userDetails["arp_capability"] = '1';
        } else {
            $userDetails["arp_capability"] = '2';
        }
        $val2 = $this->multipart($profile1['arp_vulnerability']);

        if ($val2 == 'enabled') {
            $userDetails["arp_vulnerability"] = '1';
        } else {
            $userDetails["arp_vulnerability"] = '2';
        }
        return $userDetails;
    }
}
