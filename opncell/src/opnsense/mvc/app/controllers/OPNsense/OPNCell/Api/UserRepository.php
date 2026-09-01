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
        $response = $this->backend->configdpRun("opncell showUsers");
        return json_decode((string)$response, true);
    }
//    public function getUsers()
//    {
//        $response = $this->backend->configdpRun("opncell showUsers", [$searchPhrase, $itemsPerPage,
//                ($currentPage - 1) * $itemsPerPage, $ruleId, $sortBy]);
//        return json_decode((string)$response, true);
//    }

    public function getUser($imsi)
    {
        $response = $this->backend->configdpRun("opncell getUser", [json_encode(['imsi' => $imsi])]);
        return json_decode((string)$response, true);
    }

    public function saveUser($userDetails)
    {
        $val_encoded = base64_encode(json_encode($userDetails));
        $response = $this->backend->configdpRun("opncell saveUsers", $val_encoded);
        return json_decode((string)$response, true);

    }

    public function deleteUser($imsi)
    {
        $response = $this->backend->configdpRun("opncell deleteUser", [json_encode(['imsi' => $imsi])]);
        return json_decode((string)$response, true);
    }
}