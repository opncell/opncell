<?php
namespace OPNsense\Base {
    class ApiControllerBase {
        public $request;
        public function configdStream($action, $params, ...$options) { return $params; }
    }
}
namespace OPNsense\Core {
    class Backend {
        public static array $params;
        public static array $active = [['scope'=>'mme']];
        public function configdpRun($action, $params) {
            if ($action === 'opncell activeLogs') return json_encode(['status'=>'ok','rows'=>self::$active]);
            self::$params = $params;
            return '{"rows":[],"total_rows":0}';
        }
    }
}
namespace {
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/models/OPNsense/OPNCell/ServiceNames.php';
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/controllers/OPNsense/OPNCell/Api/LogController.php';
    class Request {
        public function __construct(private $cutoff, private bool $post, private int $rowCount = 50) {}
        public function get($key, $filter = null, $default = null) {
            $value = $key === 'validFrom' ? $this->cutoff : $default;
            return $filter === 'int' ? filter_var($value, FILTER_SANITIZE_NUMBER_INT) : $value;
        }
        public function getPost($key, $filter = null, $default = null) { return $key === 'rowCount' ? $this->rowCount : ($key === 'current' ? 3 : $default); }
        public function isPost() { return $this->post; }
        public function isGet() { return !$this->post; }
    }
    foreach (['1794222512.222'=>1794222512, '1794222512'=>1794222512, '0'=>0, '-1'=>0, 'invalid'=>0] as $input=>$expected) {
        $controller = new OPNsense\OPNCell\Api\LogController();
        $controller->request = new Request($input, true);
        $controller->queryAction('mme');
        if (OPNsense\Core\Backend::$params[5] !== $expected) {
            throw new RuntimeException('Incorrect query cutoff: '.$input);
        }
        $controller->request = new Request($input, false);
        $params = $controller->queryAction('mme', 'export');
        if ($params[3] !== $expected) throw new RuntimeException('Incorrect download cutoff');
    }
    $controller->request = new Request('1794222512.222', true, -1);
    $controller->queryAction('mme');
    if (OPNsense\Core\Backend::$params[0] !== 0 || OPNsense\Core\Backend::$params[1] !== 0) {
        throw new RuntimeException('All must remove the limit and reset the offset');
    }
    if (OPNsense\Core\Backend::$params[5] !== 1794222512) throw new RuntimeException('All lost date filter');
    $controller->request = new Request(0, true, 5000);
    $controller->queryAction('mme');
    if (OPNsense\Core\Backend::$params[0] !== 5000 || OPNsense\Core\Backend::$params[1] !== 10000) {
        throw new RuntimeException('Normal paging changed');
    }
    OPNsense\Core\Backend::$active = [];
    $result = $controller->queryAction('mme');
    if ($result['active'] !== false || $result['rows'] !== []) throw new RuntimeException('Inactive log data was returned');
    $result = $controller->clearAction('mme');
    if ($result['status'] !== 'failed') throw new RuntimeException('Inactive log clear was allowed');
    echo "SUCCESS: date filters, All/normal paging and inactive log checks passed\n";
}
