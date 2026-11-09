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
        $rows = json_decode((string)$response, true);
        if (!is_array($rows) || !array_is_list($rows)) {
            throw new \RuntimeException('Could not load subscribers. Check MongoDB and its diagnostic log.');
        }
        return $rows;
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
        return $this->runProvisioningAction('opncell saveUsers', $userDetails) ?? 'Failed';
    }

    public function getSubscriberForEdit(string $imsi): array
    {
        return $this->editSubscriber(['imsi' => $imsi, 'read' => true]);
    }

    public function editSubscriber(array $details): array
    {
        $result = $this->runProvisioningAction('opncell updateSubscriberProfiles', $details);
        return is_array($result) ? $result : ['result' => 'failed', 'message' => 'Subscriber request failed'];
    }

    private function runProvisioningAction(string $action, array $details): mixed
    {
        $payload = json_encode($details);
        if ($payload === false || strlen($payload) > 49152) {
            return null;
        }
        // Configd requests have a bounded command size. Keep subscriber data out of the command.
        $file = tempnam('/tmp', 'opncell-subscriber-');
        if ($file === false) {
            return null;
        }
        try {
            if (file_put_contents($file, $payload) !== strlen($payload)) {
                return null;
            }
            return json_decode((string)$this->backend->configdpRun($action, ['file:' . $file]), true);
        } finally {
            unlink($file);
        }
    }

    public function deleteUser($imsi)
    {
        $response = $this->backend->configdpRun("opncell deleteUser", [json_encode(['imsi' => $imsi])]);
        return json_decode((string)$response, true);
    }
}
