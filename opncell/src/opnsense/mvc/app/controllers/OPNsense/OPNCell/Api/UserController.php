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

namespace OPNsense\OPNCell\Api;

use Exception;
use http\Client\Request;
use OPNsense\Base\ApiControllerBase;
use OPNsense\Base\ApiMutableModelControllerBase;
use OPNsense\OPNCell\Api\FileUploadService;
use OPNsense\Base\UserException;
use OPNsense\OPNCell\Api\UserRepository;
use OPNsense\Core\Config;
use OPNsense\Core\Backend;
use OPNsense\OPNCell\User;
use OPNsense\Phalcon\Filter\Filter;
use Phalcon\Http\RequestInterface;
use Phalcon\Messages\Message;
use phpDocumentor\Reflection\Type;
use Psr\Http\Message\ServerRequestInterface;
use ReflectionException;

header("Access-Control-Allow-Origin: *");


class UserController extends ApiMutableModelControllerBase
{

    protected static $internalModelClass = '\OPNsense\OPNCell\User';
    protected static $internalModelName = 'user';
//    public \OPNsense\Mvc\Request $request;


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
                $count += 1;
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
                $item['uuid'] = $index;
                $item['imsi'] = $process['imsi'];
                $item['profile'] = $process['apn'];
                $details[] = $item;
            }

        }
//        $this->request = new \OPNsense\Mvc\Request();

        // fetch query parameters (limit results to prevent out of memory issues)
        if ($this->request->isPost()) {
            $itemsPerPage = $this->request->getPost('rowCount', 'int', 9999);
            $currentPage = $this->request->getPost('current', 'int', 1);
            $offset = ($currentPage - 1) * $itemsPerPage;
            $searchPhrase = $this->request->getPost('searchPhrase', 'string', '');
            $filteredResult = $this->filterResults($details, $searchPhrase);
            $paginatedResult = array_slice($filteredResult, $offset, $itemsPerPage);

        }

        return ['total' => count($filteredResult), 'rowCount' => $itemsPerPage, 'current' => $currentPage, 'rows' => $paginatedResult,];
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

        return $result;
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
        $profile = $profileClass->getProfileAction($profile_uuid);

        //return the user + the details of the serviceType/profile they are attached to
        return array_merge($user_array, $profile);
    }

    public function delAction($uuid): array
    {
        $result = array("result" => "failed");
        $path = 'users.user';

        Config::getInstance()->lock();
        $mdl = $this->getModel();
        if ($uuid != null) {
            $tmp = $mdl;
            foreach (explode('.', $path) as $step) {
                $tmp = $tmp->{$step};
            }
            if ($tmp->del($uuid)) {
                $this->save();
                $result['result'] = 'success';
            } else {
                $result['result'] = 'not found';
            }
        }
//        }
        return $result;
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

    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function deleteSubFromDBAction($imsi): array
    {
        $backend = new Backend();
        $target_uuid = '';
        $userRepository = new UserRepository($backend);
        $allUsers = $this->getModelNodes();

        foreach ($allUsers['users']['user'] as $uuid => $user) {
            if ($user['imsi'] === $imsi) {
                $target_uuid = $uuid;
                break;
            }
        }
        $db_result = $userRepository->deleteUser($imsi);


        if ($db_result == "deleted") {
            return $this->delAction($target_uuid);
        } else {
            return array("result" => "failed");
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


    # bulk insertion of users

    public function uploadAction(): array
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
    public function addSubAction(): array
    {
        $backend = new Backend();
        $mdlUser = new User();
        $result = array();
        $userRepository = new UserRepository($backend);
//        $this->request = new \OPNsense\Mvc\Request();
        $userDetails = $this->request->getPost("user");
        $selected_profile_uuid = explode(",", $userDetails['profile']);
        $numberOfProfiles = count($selected_profile_uuid);
        $profileClass = new ProfileController();
        $index = 0;
        $sub['count'] = $numberOfProfiles;
        foreach ($selected_profile_uuid as $p_uuid) {
            $profile = $profileClass->getProfileAction($p_uuid);
            $index += 1;
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
        if ($data == "Duplicate") {
            $valMsgs = $mdlUser->performValidation();
            $valMsgs->appendMessage(new Message(gettext(" A User with this imsi already exists."), 'imsi'));
            foreach ($valMsgs as $msg) {
                if (!isset($result["validations"])) {
                    $result["validations"] = array();
                }
                $result["validations"]["user." . $msg->getField()] = $msg->getMessage();
            }
            return $result;
        }
        if ($data == "Success") {
            return array("result" => $data);
        } else {
            return array("result" => $sub);
        }
    }

    public function setSubAction($imsi): array
    {
        try {
            $backend = new Backend();
//            $this->request = new \OPNsense\Mvc\Request();
            $updatedUserDetails = $this->request->getPost('user');

            // Fetch user details
            $userRepository = new UserRepository($backend);
            $userDetails = $this->fetchUserDetails($userRepository, $imsi);

            if (!$userDetails) {
                return ["result" => "Failed", "message" => "User not found"];
            }

            $profileIDs = $updatedUserDetails['profile'];
            if (empty($profileIDs)) {
                return ["result" => "Failed", "message" => "No profiles provided"];
            }

            $profileClass = new ProfileController();
            $this->deleteSubFromDBAction($imsi);

            $subUser = $this->buildSubUser($userDetails, $profileIDs, $profileClass);

            // Save user details
            $result = $userRepository->saveUser($subUser);

            if ($result != "Success") {
                return ["result" => $subUser];
            }
            return ["result" => "success"];
        } catch (Exception $e) {
            return ["result" => "Failed", "message" => $e->getMessage()];
        }
    }

    private function fetchUserDetails($userRepository, $imsi): ?array
    {
        $data = $userRepository->getUser($imsi);
        if ($data === null) {
            return null;
        }

        $userDetails = [];
        foreach ($data as $process) {
            $userDetails['imsi'] = $process['imsi'];
            $userDetails['ki'] = $process['ki'];
            $userDetails['opc'] = $process['opc'];
        }

        return $userDetails;
    }

    private function buildSubUser($userDetails, $profileIDs, $profileClass): array
    {
        $profileList = explode(",", $profileIDs);
        $subUser = ['count' => count($profileList)];

        foreach ($profileList as $index => $profileID) {
            $profile = $profileClass->getProfileAction($profileID);
            $userDetails = array_merge($userDetails, ['sst' => $profile['profile']['sst'], 'dl' => $profile['profile']['dl'], 'ul' => $profile['profile']['ul'], 'QoS' => $profile['profile']['QoS'], 'arp_priority' => $profile['profile']['arp_priority'], 'apn' => $profile['profile']['apn']]);
            $userDetails = $this->getUserDetails($profile['profile'], $userDetails);
            $subUser[$index + 1] = $userDetails;
        }

        return $subUser;
    }

    /**
     * @param $profile1
     * @param array $userDetails
     * @return array
     */
    public function getUserDetails($profile1, array $userDetails): array
    {

        $userDetails['arp_capability'] = ($this->multipart($profile1['arp_capability']) == 'enabled') ? '1' : '2';
        $userDetails['arp_vulnerability'] = ($this->multipart($profile1 ['arp_vulnerability']) == 'enabled') ? '1' : '2';
        return $userDetails;
    }
}
