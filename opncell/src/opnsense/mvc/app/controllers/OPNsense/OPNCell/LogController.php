<?php

namespace OPNsense\OPNCell;

class LogController extends \OPNsense\Diagnostics\LogController
{
    public function indexAction($scope = '')
    {
        if ($scope === '') {
            $this->renderPage('opncell', '');
            $this->view->pick('OPNsense/OPNCell/diagnostics');
            return;
        }
        $scope = ServiceNames::logScope($scope);
        if ($scope === null) {
            return $this->response->setStatusCode(404, 'Not Found');
        }

        $backend = new \OPNsense\Core\Backend();
        $active = json_decode($backend->configdpRun('opncell activeLogs', []), true);
        if (!is_array($active) || ($active['status'] ?? '') !== 'ok') {
            return $this->response->setStatusCode(503, 'Unable to inspect active daemons');
        }
        if (!in_array($scope, array_column($active['rows'], 'scope'), true)) {
            return $this->response->redirect('/ui/opncell/log');
        }
        $this->renderPage('opncell', $scope);
        $source = json_decode((new \OPNsense\Core\Backend())->configdpRun('opncell logSource', [$scope]), true);
        $this->view->opncell_log_path = $source['path'] ?? gettext('Log destination unavailable');
        $this->view->pick('OPNsense/OPNCell/log');
    }
}
