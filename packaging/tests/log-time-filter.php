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
        public function configdpRun($action, $params) {
            self::$params = $params;
            return '{"rows":[],"total_rows":0}';
        }
    }
}
namespace {
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/models/OPNsense/OPNCell/ServiceNames.php';
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/controllers/OPNsense/OPNCell/Api/LogController.php';
    class Request {
        public function __construct(private $cutoff, private bool $post) {}
        public function get($key, $filter = null, $default = null) {
            $value = $key === 'validFrom' ? $this->cutoff : $default;
            return $filter === 'int' ? filter_var($value, FILTER_SANITIZE_NUMBER_INT) : $value;
        }
        public function getPost($key, $filter = null, $default = null) { return $default; }
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
    echo "SUCCESS: 10 query/download date filter checks passed\n";
}
