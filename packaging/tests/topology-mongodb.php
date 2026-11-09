<?php
namespace OPNsense\Base {
    class ApiControllerBase { public $request; }
}
namespace OPNsense\Mvc {
    class Request {
        public function isPost() { return true; }
        public function getPost($name) { return ['mcc'=>'001','mnc'=>'01','tac'=>'1']; }
    }
}
namespace OPNsense\Core {
    class Config {
        public static function getInstance() { return new self(); }
        public function save() {}
    }
    class Backend {
        public static array $calls = [];
        public static array $running = ['mongod'=>true];
        public static bool $boot = true;
        public function configdRun($command) {
            self::$calls[] = $command;
            [$name,$action] = explode(' ', $command);
            if ($action === 'status') {
                return (self::$running[$name] ?? false) ? "$name is running" : "$name is not running";
            }
            self::$running[$name] = $action !== 'stop';
            return 'OK';
        }
        public function configdpRun($command, $parameters) {
            if ($command === 'opncell loadConfiguration') return '{"result":"rendered"}';
            if ($command === 'opncell verifyBoot') return self::$boot ? '{"result":"verified"}' : '{"result":"failed","message":"Boot mismatch"}';
            return 'OK';
        }
    }
}
namespace OPNsense\OPNCell {
    class General {
        public function __get($name) { return new Node(['mcc'=>'001','mnc'=>'01','tac'=>'1'][$name] ?? '0'); }
        public function setNodes($nodes) {}
        public function getNodes() { return []; }
        public function performValidation() { return new \ArrayObject(); }
        public function serializeToConfig() {}
    }
    class Node {
        public function __construct(private string $value) {}
        public function __toString() { return $this->value; }
    }
}
namespace {
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/models/OPNsense/OPNCell/ServiceNames.php';
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/controllers/OPNsense/OPNCell/Api/ServiceController.php';
    use OPNsense\Core\Backend;
    function applyTopology() {
        $controller = new OPNsense\OPNCell\Api\ServiceController();
        $controller->request = new OPNsense\Mvc\Request();
        return $controller->reconfigureActAction('enablefour');
    }
    $result = applyTopology();
    if ($result['result'] !== 'applied') throw new RuntimeException('Topology did not apply');
    foreach (Backend::$calls as $command) {
        if (str_starts_with($command, 'mongod ') && $command !== 'mongod status') {
            throw new RuntimeException('Healthy MongoDB was modified: '.$command);
        }
    }
    Backend::$calls = [];
    Backend::$running = ['mongod'=>false];
    $result = applyTopology();
    if ($result['result'] !== 'applied' || count(array_filter(Backend::$calls, fn($c)=>$c==='mongod start')) !== 1) {
        throw new RuntimeException('Stopped MongoDB was not started exactly once');
    }
    Backend::$boot = false;
    $result = applyTopology();
    if ($result['result'] !== 'failed' || $result['message'] !== 'Boot mismatch') {
        throw new RuntimeException('Boot verification failure was not reported');
    }
    echo "SUCCESS: 3 topology/MongoDB lifecycle checks passed\n";
}
