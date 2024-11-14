<?php

namespace OPNsense\OPNCell\Api;

use OPNsense\Core\Backend;

class UserRepository
{
    private $backend;

    public function __construct(Backend $backend)
    {
        $this->backend = $backend;
    }
    public function getUsers()
    {
        $response = $this->backend->configdpRun("opncore showUsers");
        return json_decode((string)$response, true);
    }
//    public function getUsers()
//    {
//        $response = $this->backend->configdpRun("opncore showUsers", [$searchPhrase, $itemsPerPage,
//                ($currentPage - 1) * $itemsPerPage, $ruleId, $sortBy]);
//        return json_decode((string)$response, true);
//    }

    public function getUser($imsi)
    {
        $response = $this->backend->configdpRun("opncore getUser", [json_encode(['imsi' => $imsi])]);
        return json_decode((string)$response, true);
    }

    public function saveUser($userDetails)
    {
        $response = $this->backend->configdpRun("opncore saveUsers", [json_encode($userDetails)]);
        return json_decode((string)$response, true);
    }

    public function deleteUser($imsi)
    {
        $response = $this->backend->configdpRun("opncore deleteUser", [json_encode(['imsi' => $imsi])]);
        return json_decode((string)$response, true);
    }
}