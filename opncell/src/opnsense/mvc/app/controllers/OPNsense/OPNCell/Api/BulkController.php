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
        if (!(new \OPNsense\Mvc\Request())->isPost()) {
            return ['result' => 'failed'];
        }
        $userRepository = new UserRepository($backend);
        if (session_status() !== PHP_SESSION_ACTIVE) {
            session_start();
        }
        $duplicates = [];
        $failed = [];
        $inserted = 0;
        $errors = [];
        $profile = $this->getAction($uuid);
        $selected_profile_uuid = $this->multipart($profile['bulk']['profile']);
        $profileClass = new ProfileController();
        $userClass = new UserController();
        $profileMap = [];
        foreach ((new \OPNsense\OPNCell\Profile())->profiles->profile->iterateItems() as $id => $node) {
            $p = $profileClass->getProfileAction($id)['profile'];
            $selector = (string)(int)$p['sst'] . (!empty($p['sd']) ? ':' . strtolower($p['sd']) : '') . '/' . $p['apn'];
            $profileMap[$selector][] = $id;
        }

        if (isset($_SESSION['fileValues'])) {
            $outputKeyValue = $_SESSION['fileValues'];
            foreach ($outputKeyValue as $indexInFile => $item) {
                $userDetails = array_intersect_key($item, array_flip(['imsi', 'ki', 'opc', 'op', 'amf', 'msisdn',
                    'ue_ambr_downlink', 'ue_ambr_downlink_unit', 'ue_ambr_uplink', 'ue_ambr_uplink_unit', 'subscriber_status', 'operator_determined_barring', 'default_slice', 'session_addresses', 'pcc_rules']));
                try {
                    $rowProfiles = $selected_profile_uuid;
                    if (isset($item['profiles']) && trim($item['profiles']) !== '') {
                        $selectors = json_decode($item['profiles'], true, 32, JSON_THROW_ON_ERROR);
                        if (!is_array($selectors) || !array_is_list($selectors) || !$selectors) {
                            throw new \RuntimeException('Profiles must be a nonempty JSON list of SST[:SD]/APN selectors');
                        }
                        $rowProfiles = [];
                        foreach ($selectors as $selector) {
                            if (!is_string($selector) || count($profileMap[$selector] ?? []) !== 1) {
                                throw new \RuntimeException('Missing or ambiguous profile for exported slice/APN');
                            }
                            $rowProfiles[] = $profileMap[$selector][0];
                        }
                    }
                    if (!$rowProfiles) {
                        throw new \RuntimeException('At least one profile is required');
                    }
                } catch (\JsonException | \RuntimeException $error) {
                    $failed[] = $indexInFile + 1;
                    $errors[] = 'Record ' . ($indexInFile + 1) . ': ' . $error->getMessage();
                    continue;
                }
                $index = 0;
                $sub_user = ['count' => count($rowProfiles)];

                foreach ($rowProfiles as $p_uuid) {
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
                    $userDetails = $userClass->getUserDetails($profile['profile'], $userDetails);
                    $sub_user[$index] = $userDetails;
                }
                $data = $userRepository->saveUser($sub_user);
                if ($data == "Duplicate") {
                    $duplicates[] = $userDetails["imsi"];
                } elseif ($data === 'Success') {
                    $inserted++;
                } else {
                    $failed[] = $indexInFile + 1;
                    $errors[] = 'Record ' . ($indexInFile + 1) . ': ' . (is_string($data) ? $data : 'Subscriber validation or save failed');
                }
            }
        }
        else {
            return ['result' => 'failed', 'message' => 'Upload a subscriber file first'];
        }

        return ['result' => 'processed', 'inserted' => $inserted, 'duplicates' => $duplicates, 'failed' => $failed, 'errors' => $errors];
    }
}
