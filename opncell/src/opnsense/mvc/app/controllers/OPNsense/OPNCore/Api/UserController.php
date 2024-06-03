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
use OPNsense\Base\UserException;
use OPNsense\Core\Config;
use OPNsense\Core\Backend;
use OPNsense\OPNCore\User;
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
        $count = 0;
        foreach ($dataArray as $command_key => $command_value) {
            if ($command_value["selected"] === 1) {
                $count+=1;
                $apn[$key] = $command_key;
            }
        }
        return $apn;
    }

    public function multipart($value): array
    {
        $selected_apn = [];
        $selectedString = " ";
        $jsonString = json_encode($value);
        $dataArray = json_decode($jsonString, true);
        $count = 0;
        foreach ($dataArray as $command_key => $command_value) {
            if ($command_value["selected"] === 1) {
//                $selectedString = $command_key;
                $count+=1;
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


//    public function searchSubAction(): array
//    {
//        $backend = new Backend();
//        // fetch query parameters (limit results to prevent out of memory issues)
//        $itemsPerPage = $this->request->getPost('rowCount', 'int', 9999);
//        $currentPage = $this->request->getPost('current', 'int', 1);
//        $offset = ($currentPage - 1) * $itemsPerPage;
//
//        $response = $backend->configdpRun("opncore showUsers");
//
//        $data = json_decode((string)$response, true);
//        $details = [];
//        if ($data != null) {
//            foreach ($data as $index => $process) {
//                $item = array();
//                $item['uuid']=$index;
//                $item['imsi'] = $process['imsi'];
//                $item['profile'] = $process['apn'];
//                $details[] = $item;
//            }
//        }
//        $entry_keys = array_keys($details);
//        if ($this->request->hasPost('searchPhrase') && $this->request->getPost('searchPhrase') !== '') {
//            $searchPhrase = $this->request->getPost('searchPhrase');
//            $entry_keys = array_filter($entry_keys, function ($key) use ($searchPhrase, $details) {
//                foreach ($details[$key] as $itemval) {
//                    if (strpos($itemval, $searchPhrase) !== false) {
//                        return true;
//                    }
//                }
//                return false;
//            });
//        }
//        $formatted = array_map(function ($value) use (&$details) {
//            $item = ['#' => $value];
//            foreach ($details[$value] as $ekey => $evalue) {
//                $item[$ekey] = $evalue;
//            }
//            return $item;
//        }, array_slice($entry_keys, $offset, $itemsPerPage));
//
//
//        return [
//            'total' => count($entry_keys),
//            'rowCount' => $itemsPerPage,
//            'current' => $currentPage,
//            'rows' => $formatted,
//        ];
//    }


    //Get the correlation between users and profiles.

    /**
     * @throws ReflectionException
     */
    public function profileAndUsersListAction(): array
    {
        $result = [];
//        $user = $this->searchBase('users.user', array("imsi", "profile")); // users' list having only imsi and profile
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
        $verdict = [];
        $user = $this->getBase('user', 'users.user', $uuid);
        $imsi = $user['user']['imsi'];
        $backend = new Backend();
        $net['imsi'] = $imsi;
        $values = json_encode($net);
        $db_result = $backend->configdpRun("opncore deleteUser", array($values));  //remove user from db
        $data = json_decode((string)$db_result, true);
        if ($data == "deleted") {
            return $this->delBase('users.user', $uuid);
        } else {
            return array("result"=>"failed");

        }
    }
    public function deleteSubFromDBAction($imsi)
    {
        $verdict = [];
        $backend = new Backend();
        $net['imsi'] = $imsi;
        $values = json_encode($net);
        $db_result = $backend->configdpRun("opncore deleteUser", array($values));  //remove user from db
        $data = json_decode((string)$db_result, true);
        if ($data == "deleted") {
            return array("result"=>"success");
        } else {
            return array("result"=>"failed");

        }
    }

    public function searchSubAction(): array
    {
        $profile_array = $this->searchBase('users.user', array("imsi","profile"));
        return $profile_array;
    }
    /**
     * @throws ReflectionException
     * @throws UserException
     */
    public function getSingleSubAction($imsi): array
    {
        $backend = new Backend();
        $net['imsi'] = $imsi;
        $values = json_encode($net);
        $profileClass = new ProfileController();
        $response = $backend->configdpRun("opncore getUser", array($values));
        $data =  json_decode((string)$response, true);
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
     * @throws UserException
     * @throws Exception
     */
    public function setSubAction($uuid): array
    {
        $this->setBase('user', 'users.user', $uuid);
        $backend = new Backend();
        $result = ["result" => "failed"];
        $userDetails = [];
        $user = $this->getSubAction($uuid);
        $imsi = $user['user']['imsi'];
        $imsi_string["imsi"] = $imsi;
        $val = json_encode($imsi_string);
        $updatedUserDetails = $this->request->getPost('user');
        $response = $backend->configdpRun("opncore getUser", array($val));
        $data =  json_decode((string)$response, true);
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
        $profileList = explode(",", $profileIDS);
        $numberOfProfiles = count($profileList);
        $sub_user['count'] = $numberOfProfiles;
        $sub_result = "";
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
            $val = json_encode($sub_user);
            $sub_result= $backend->configdpRun("opncore saveUsers", array($val));
        }
        $data = json_decode((string)$sub_result, true);
        if ($data != "Success") {
            return array("result"=>"Failed");
        } else {
            return $this->setBase('user', 'users.user', $uuid);
        }
    }

    public function headersToLowerCase($headers)
    {
        $i=0;
        foreach ($headers as $item) {
            $headers[$i] = strtolower($item);
            $i++;
        }
        return $headers;
    }
    public function processInpOutFiles($handle): array
    {
        $foundStart = false;
        $headers = array();
        $isOutFile = false;
        $contentLines = array();

        $counter = 0;
        while (($line = fgets($handle)) !== false) {
            if (empty(trim($line))) { // ignore empty lines
                continue;
            }
            $counter +=1;
            // Check if the line starts with "var_out:"
            if (strpos($line, "var_out:") === 0) {
                $foundStart = true;
                if ($counter === 1) { // if var_out: is on the very first line it is an outfile
                    $isOutFile = true;
                }
                $line = str_replace("var_out:", "", $line);
                $headers = explode("/", trim($line));
                $headers = $this->headersToLowerCase($headers);
            }
            if ($foundStart) {
                // Split the line by tabs or multiple spaces if inp file and by comma if outfile
                if ($isOutFile) {
                    $record = explode(",", trim($line));
                } else {
                    $record = preg_split('/\t+|\s{2,}/', trim($line));
                }
                // Check if the number of elements in $headers matches the number of elements
                // in $record (for empty rows)
                if (count($headers) == count($record)) {
                    // Map the values to keys from headers array
                    $mappedRecord = array_combine($headers, $record);
                    $contentLines[] = $mappedRecord;
                }
            }
        }
        return $contentLines;
    }

    public function processCSVFile($handle): array
    {
        $headers = fgetcsv($handle);
        $headers = $this->headersToLowerCase($headers);
        $data = array();
        while (($row = fgetcsv($handle)) !== false) {
            $row = array_combine($headers, $row);
            $data[] = $row;
            while (($row = fgetcsv($handle)) !== false) {
                $row = array_combine($headers, $row);
                $data[] = $row;
            }
        }
        return $data;
    }

    # bulk insertion of users

    public function uploadAction():array
    {
        global $outputKeyValue;
        $result = ["result" => "failed"];
        if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_FILES["file"])) {
            $file = $_FILES["file"];
            $isCsvFile = $file["type"] === "text/csv";

            if ($file["error"] === UPLOAD_ERR_OK) {
                $fileTmpPath = $file["tmp_name"];
                $fileName = $file["name"];

                $handle = fopen($fileTmpPath, "r");
                if ($handle !== false) {
                    if ($isCsvFile) {
                         $outputKeyValue = $this->processCSVFile($handle);
                    } else {
                        $outputKeyValue = $this->processInpOutFiles($handle);
                    }
                    fclose($handle);
                    session_start();
                    $_SESSION['fileValues'] = $outputKeyValue;
                }
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
                $val = json_encode($sub);

                $sub_result = $backend->configdpRun("opncore saveUsers", array($val));
                $data = json_decode((string)$sub_result, true);

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
