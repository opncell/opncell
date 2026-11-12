<?php
namespace OPNsense\Base { class ApiMutableModelControllerBase {public $response;} }
namespace OPNsense\Mvc {
    class Request {
        public static bool $post = true;
        public static string $payload = '';
        public function isPost() { return self::$post; }
        public function getPost($name, $filter = null, $default = null) { return self::$payload; }
    }
}
namespace OPNsense\Core {
    class Backend {
        public static $requestFile;
        public function configdpRun($action, $args) {
            if ($action !== 'opncell manageHnet' || count($args) !== 1) throw new \RuntimeException('Unsafe dispatch');
            $path = $args[0];
            if (!str_starts_with($path, '/tmp/opncell-hnet-') || (fileperms($path) & 077) !== 0) throw new \RuntimeException('Unsafe request file');
            $data = json_decode(file_get_contents($path), true);
            if ($data['passphrase'] !== 'fixture <secret> phrase') throw new \RuntimeException('Passphrase changed');
            self::$requestFile = $path;
            return json_encode(['result'=>'ok']);
        }
    }
}
namespace {
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/controllers/OPNsense/OPNCell/Api/HnetController.php';
    $controller = new OPNsense\OPNCell\Api\HnetController();
    $controller->response = new class {
        public $headers=[];
        public function setHeader($key,$value) {$this->headers[$key]=$value;}
    };
    OPNsense\Mvc\Request::$payload = json_encode(['operation'=>'plan','passphrase'=>'fixture <secret> phrase']);
    if ($controller->manageAction()['result'] !== 'ok') throw new RuntimeException('Dispatch failed');
    if (file_exists(OPNsense\Core\Backend::$requestFile)) throw new RuntimeException('Private request file retained');
    if ($controller->response->headers['Cache-Control'] !== 'no-store') throw new RuntimeException('Caching allowed');
    OPNsense\Mvc\Request::$payload = str_repeat('x',2097153);
    if ($controller->manageAction()['result'] !== 'failed') throw new RuntimeException('Oversize accepted');
    OPNsense\Mvc\Request::$payload = 'null';
    if ($controller->manageAction()['result'] !== 'failed') throw new RuntimeException('Invalid payload accepted');
    OPNsense\Mvc\Request::$post = false;
    if ($controller->manageAction()['result'] !== 'failed') throw new RuntimeException('GET accepted');
    echo "PASS: Hnet private-file dispatch, cleanup, exact passphrase, no-cache, size and method checks\n";
}
