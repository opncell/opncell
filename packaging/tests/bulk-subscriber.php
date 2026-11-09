<?php
namespace OPNsense\Base { class ApiMutableModelControllerBase {} }
namespace OPNsense\Mvc { class Request { public function isPost() { return true; } } }
namespace OPNsense\Core { class Backend {} }
namespace OPNsense\OPNCell {
    class Profile {
        public $profiles;
        public function __construct() { $this->profiles = (object)['profile'=>new Nodes()]; }
    }
    class Nodes { public function iterateItems() { return ['profile-1'=>new \stdClass()]; } }
}
namespace OPNsense\OPNCell\Api {
    class ProfileController {
        public function getProfileAction($id) {
            return ['profile'=>['sst'=>'1', 'sd'=>'000001', 'apn'=>'internet', 'dl'=>'100', 'ul'=>'50',
                'QoS'=>'9', 'arp_priority'=>'8']];
        }
    }
    class UserController { public function getUserDetails($profile, $details) { return array_merge($details, $profile); } }
    class UserRepository {
        public static array $saved = [];
        public function __construct($backend) {}
        public function saveUser($details) { self::$saved[]=$details; return 'Success'; }
    }
}
namespace {
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/controllers/OPNsense/OPNCell/Api/BulkController.php';
    class Bulk extends OPNsense\OPNCell\Api\BulkController {
        public function getAction($uuid=null): array { return ['bulk'=>['profile'=>[]]]; }
    }
    session_start();
    $row = ['imsi'=>'001010000000001', 'ki'=>str_repeat('11',16), 'opc'=>str_repeat('22',16),
        'profiles'=>'["1:000001/internet"]', 'ue_ambr_downlink'=>'123', 'ue_ambr_downlink_unit'=>'2',
        'ue_ambr_uplink'=>'45', 'ue_ambr_uplink_unit'=>'2', 'subscriber_status'=>'1',
        'operator_determined_barring'=>'8', 'default_slice'=>'1:000001',
        'session_addresses'=>'{"1:000001/internet":{"ue":{"ipv4":"10.0.0.5"}}}', 'pcc_rules'=>'{}'];
    $_SESSION['fileValues']=[$row];
    $result=(new Bulk())->saveBulkUsersAction('bulk-1');
    if ($result['inserted'] !== 1 || $result['failed']) throw new RuntimeException('Exported profile not resolved');
    $saved=OPNsense\OPNCell\Api\UserRepository::$saved[0];
    foreach ($row as $key=>$value) {
        if ($key !== 'profiles' && $saved[1][$key] !== $value) throw new RuntimeException('Bulk lost field '.$key);
    }
    $_SESSION['fileValues']=[array_merge($row,['profiles'=>'["1/missing"]'])];
    $result=(new Bulk())->saveBulkUsersAction('bulk-1');
    if ($result['inserted'] || $result['failed'] !== [1] || !$result['errors']) throw new RuntimeException('Missing profile not reported');
    $_SESSION['fileValues']=[array_merge($row,['profiles'=>'not JSON'])];
    $result=(new Bulk())->saveBulkUsersAction('bulk-1');
    if ($result['inserted'] || $result['failed'] !== [1]) throw new RuntimeException('Malformed profiles accepted');
    echo "SUCCESS: bulk new fields, exported profile resolution and invalid-row reporting passed\n";
}
