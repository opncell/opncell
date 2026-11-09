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

use OPNsense\Base\ApiControllerBase;
use OPNsense\Base\ApiMutableModelControllerBase;
use OPNsense\OPNCell\Api\FileUploadService;
use OPNsense\Base\UserException;
use OPNsense\OPNCell\Api\UserRepository;
use OPNsense\Core\Config;
use OPNsense\Core\Backend;
use OPNsense\OPNCell\User;
use OPNsense\Phalcon\Filter\Filter;

use Phalcon\Messages\Message;

use ReflectionException;

header("Access-Control-Allow-Origin: *");


class UserController extends ApiMutableModelControllerBase
{

    protected static $internalModelClass = '\OPNsense\OPNCell\User';
    protected static $internalModelName = 'user';
    public \OPNsense\Mvc\Request $request;


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

    public function fetchUsersAction():array
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
        return $details;
    }

    /**
     * @throws ReflectionException
     */
    public function searchSubAction()
    {

        $this->request = new \OPNsense\Mvc\Request();
        // fetch query parameters (limit results to prevent out of memory issues)
        if ($this->request->isPost()) {
            $itemsPerPage = $this->request->getPost('rowCount', 'int', 9999);
            $currentPage = $this->request->getPost('current', 'int', 1);

            $searchPhrase = $this->request->getPost('searchPhrase', 'string', '');
            $filteredResult = $this->filterResults($this->fetchUsersAction(), $searchPhrase);
            return \OPNsense\OPNCell\SubscriberGrid::page(
                $filteredResult, $this->request->getPost('sort'), $itemsPerPage, $currentPage
            );
        }

        return ['total' => 0, 'rowCount' => 0, 'current' => 1, 'rows' => []];
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
        $user = $this->fetchUsersAction();
        if (count($user) > 0) {
            $profiles = array_column($user, 'profile');
            $initialProfileCount = [];
//            #Cater for situations where one imsi has multiple profiles attached.
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
//        $this->sessionClose(); # no longer needed or supported RPH 2026-01-24

        return $this->getBase('user', 'users.user', $uuid);
    }

    /**
     * @throws ReflectionException
     */
    public function editSubAction($uuid): array
    {
//        $this->sessionClose(); # no longer needed or supported RPH 2026-01-24
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

        return $result;
    }

    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function deleteSubAction($uuid): array
    {
        if (!(new \OPNsense\Mvc\Request())->isPost()) {
            return ['result' => 'failed'];
        }
        $user = $this->getBase('user', 'users.user', $uuid);
        $imsi = $user['user']['imsi'] ?? '';
        return $this->deleteSubFromDBAction($imsi);
    }

    public function deleteSubFromDBAction($imsi): array
    {
        if (!(new \OPNsense\Mvc\Request())->isPost() || !preg_match('/^[0-9]{5,16}$/D', $imsi)) {
            return ['result' => 'failed', 'message' => 'Invalid subscriber deletion request'];
        }

        $repository = new UserRepository(new Backend());
        $result = $repository->deleteUser($imsi);
        if (is_array($result)) {
            if (($result['result'] ?? '') !== 'deleted') {
                return $result;
            }
        } elseif ($result !== 'deleted') {
            return [
                'result' => $result === 'not found' ? 'not found' : 'failed',
                'message' => $result === 'not found'
                    ? 'Subscriber was not found in MongoDB. Refresh the subscriber list.'
                    : 'Deletion was not confirmed. Refresh the subscriber list before retrying.',
            ];
        }

        $users = $this->getModelNodes()['users']['user'] ?? [];
        foreach ($users as $uuid => $user) {
            if ($user['imsi'] === $imsi) {
                $this->delAction($uuid);
                break;
            }
        }
        return ['result' => 'deleted'];
    }

    /**
     * @throws ReflectionException
     * @throws UserException
     */

    /**
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
        $this->request = new \OPNsense\Mvc\Request();
        $userDetails = $this->request->getPost("user");
        if (!$this->request->isPost() || !is_string($userDetails['profile'] ?? null) || $userDetails['profile'] === '') {
            return ['result' => 'failed', 'message' => 'Select at least one subscriber profile'];
        }
        $selected_profile_uuid = explode(",", $userDetails['profile']);
        $numberOfProfiles = count($selected_profile_uuid);
        $profileClass = new ProfileController();
        $index = 0;
        $sub['count'] = $numberOfProfiles;
        foreach ($selected_profile_uuid as $p_uuid) {
            $profile = $profileClass->getProfileAction($p_uuid);
            if (empty($profile['profile']['apn'])) {
                return ['result' => 'failed', 'message' => 'Selected profile no longer exists'];
            }
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
            return array("result" => $data);
        }
    }

    public function setSubAction($imsi): array
    {
        try {
            $this->request = new \OPNsense\Mvc\Request();
            $details = $this->request->getPost('user');
            if (!$this->request->isPost() || !preg_match('/^[0-9]{5,16}$/D', $imsi)
                || !is_string($details['profile'] ?? null) || $details['profile'] === ''
            ) {
                return ['result' => 'failed', 'message' => 'Invalid subscriber or profile selection'];
            }

            $profileController = new ProfileController();
            $profiles = [];
            foreach (array_unique(explode(',', $details['profile'])) as $id) {
                $profile = $profileController->getProfileAction($id)['profile'] ?? [];
                if (empty($profile['apn'])) {
                    return ['result' => 'failed', 'message' => 'Selected profile no longer exists'];
                }
                $profiles[] = $this->getUserDetails($profile, $profile);
            }

            $changes = array_intersect_key($details, array_flip(['imsi', 'ki', 'opc', 'op', 'amf', 'msisdn', 'ip',
                    'ue_ambr_downlink', 'ue_ambr_downlink_unit', 'ue_ambr_uplink', 'ue_ambr_uplink_unit', 'subscriber_status', 'operator_determined_barring', 'default_slice', 'session_addresses', 'pcc_rules']));
            if ($changes && !preg_match('/^[a-f0-9]{64}$/D', (string)($details['edit_token'] ?? ''))) {
                return ['result' => 'failed', 'message' => 'Reload the subscriber before saving'];
            }
            foreach ($changes as $field => $value) {
                $valid = is_string($value) && match ($field) {
                    'imsi' => preg_match('/^[0-9]{5,16}$/D', $value),
                    'ki', 'opc', 'op' => $value === '' || preg_match('/^[a-fA-F0-9]{32}$/D', $value),
                    'amf' => $value === '' || preg_match('/^[a-fA-F0-9]{4}$/D', $value),
                    'msisdn' => preg_match('/^\s*(?:[0-9]{1,15}(?:\s*,\s*[0-9]{1,15})?)?\s*$/D', $value),
                    'ip' => $value === '' || filter_var($value, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4),
                    'session_addresses', 'pcc_rules' => strlen($value) <= 16384,
                    'default_slice' => $value === '' || preg_match('/^[0-9]{1,3}(?::[a-fA-F0-9]{6})?$/D', $value),
                    default => $value === '' || preg_match('/^[0-9]{1,10}$/D', $value),
                };
                if (!$valid) {
                    return ['result' => 'failed', 'message' => 'Invalid subscriber field: ' . $field];
                }
            }

            $repository = new UserRepository(new Backend());
            return $repository->editSubscriber([
                'imsi' => $imsi,
                'profiles' => $profiles,
                'changes' => $changes,
                'token' => $details['edit_token'] ?? null,
                'managedNames' => array_column(
                    (new \OPNsense\OPNCell\Profile())->getNodes()['profiles']['profile'] ?? [],
                    'apn'
                ),
            ]);
        } catch (Exception $e) {
            return ['result' => 'failed', 'message' => 'Subscriber update failed'];
        }
    }

    /**
     * @param $profile1
     * @param array $userDetails
     * @return array
     */
    public function getUserDetails($profile1, array $userDetails): array
    {

        foreach (['sd', 'session_type', 'lbo_roaming_allowed'] as $field) {
            $userDetails[$field] = $profile1[$field] ?? '';
        }
        $userDetails['arp_capability'] = ($this->multipart($profile1['arp_capability']) == 'enabled') ? '1' : '2';
        $userDetails['arp_vulnerability'] = ($this->multipart($profile1 ['arp_vulnerability']) == 'enabled') ? '1' : '2';
        return $userDetails;
    }
}
