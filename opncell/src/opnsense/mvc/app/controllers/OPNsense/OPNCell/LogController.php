<?php

namespace OPNsense\OPNCell;

class LogController extends \OPNsense\Diagnostics\LogController
{
    public function indexAction($scope = '')
    {
        $scope = ServiceNames::logScope($scope);
        if ($scope === null) {
            return $this->response->setStatusCode(404, 'Not Found');
        }

        $this->renderPage('opncell', $scope);
        $source = json_decode((new \OPNsense\Core\Backend())->configdpRun('opncell logSource', [$scope]), true);
        $this->view->opncell_log_path = $source['path'] ?? gettext('Log destination unavailable');
        $this->view->pick('OPNsense/OPNCell/log');
    }
}
