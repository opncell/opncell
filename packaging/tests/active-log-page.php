<?php
namespace OPNsense\Diagnostics {
    class LogController {
        public $view;
        public $response;
        public function renderPage($module, $scope) {}
    }
}
namespace OPNsense\Core {
    class Backend {
        public static bool $available = true;
        public function configdpRun($action, $params) {
            if ($action === 'opncell activeLogs') return json_encode(self::$available
                ? ['status'=>'ok','rows'=>[['scope'=>'mme']]] : ['status'=>'failed']);
            return json_encode(['path'=>'/var/log/opncell/mme.log']);
        }
    }
}
namespace {
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/models/OPNsense/OPNCell/ServiceNames.php';
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/controllers/OPNsense/OPNCell/LogController.php';
    #[\AllowDynamicProperties]
    class View {
        public $template;
        public function pick($name) { $this->template = $name; }
    }
    class Response {
        public $code;
        public $location;
        public function setStatusCode($code, $message) { $this->code = $code; return $this; }
        public function redirect($url) { $this->location = $url; return $this; }
    }
    function controller() {
        $controller = new OPNsense\OPNCell\LogController();
        $controller->view = new View(); $controller->response = new Response();
        return $controller;
    }
    $c=controller(); $c->indexAction();
    if ($c->view->template !== 'OPNsense/OPNCell/diagnostics') throw new RuntimeException('Active log landing page missing');
    $c=controller(); $c->indexAction('open5gs-mmed');
    if ($c->view->template !== 'OPNsense/OPNCell/log' || $c->view->opncell_log_path !== '/var/log/opncell/mme.log') throw new RuntimeException('Active log did not open');
    $c=controller(); $c->indexAction('open5gs-amfd');
    if ($c->response->location !== '/ui/opncell/log') throw new RuntimeException('Inactive link not redirected');
    $c=controller(); $c->indexAction('../etc/passwd');
    if ($c->response->code !== 404) throw new RuntimeException('Unknown scope accepted');
    OPNsense\Core\Backend::$available=false;
    $c=controller(); $c->indexAction('mme');
    if ($c->response->code !== 503) throw new RuntimeException('Backend error misreported as stopped');
    echo "SUCCESS: 5 active log page routing checks passed\n";
}
