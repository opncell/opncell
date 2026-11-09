<?php

namespace OPNsense\OPNCell\Api;

use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;
use OPNsense\OPNCell\ServiceNames;

class LogController extends ApiControllerBase
{
    private function activeSnapshot(): ?array
    {
        $result = json_decode((new Backend())->configdpRun('opncell activeLogs', []), true);
        return is_array($result) && ($result['status'] ?? '') === 'ok' && is_array($result['rows'] ?? null)
            ? $result['rows'] : null;
    }

    public function activeAction()
    {
        if (!$this->request->isGet()) {
            return $this->response->setStatusCode(405, 'Method Not Allowed');
        }
        $rows = $this->activeSnapshot();
        return $rows === null ? ['status' => 'failed', 'message' => gettext('Unable to inspect active daemons.')]
            : ['status' => 'ok', 'rows' => $rows];
    }

    public function queryAction($scope = '', $action = '')
    {
        $scope = ServiceNames::logScope($scope);
        if ($scope === null) {
            return $this->response->setStatusCode(404, 'Not Found');
        }
        $active = $this->activeSnapshot();
        if ($active === null) {
            return $this->response->setStatusCode(503, 'Unable to inspect active daemons');
        }
        if (!in_array($scope, array_column($active, 'scope'), true)) {
            if ($action === 'export') {
                return $this->response->setStatusCode(409, 'Daemon is not running');
            }
            return ['rows' => [], 'total' => 0, 'rowCount' => 0, 'current' => 1, 'active' => false];
        }
        $search = $this->request->get('searchPhrase', 'string', '');
        $severity = $this->request->get('severity', null, '');
        $severity = is_array($severity) ? implode(',', $severity) : $severity;
        // The browser sends fractional epoch seconds. Integer sanitizing can
        // strip the decimal point and turn seconds into a future timestamp.
        $cutoff = $this->request->get('validFrom', null, 0);
        $since = is_numeric($cutoff) && is_finite((float)$cutoff)
            ? max(0, (int)floor((float)$cutoff)) : 0;
        if ($action === 'export' && $this->request->isGet()) {
            return $this->configdStream('opncell exportLog', [$search, $scope, $severity, $since], [
                'Content-Type: text/plain; charset=utf-8',
                'Content-Disposition: attachment; filename="' . $scope . '.log"',
                'Cache-Control: no-store'
            ], 60, true);
        }
        if (!$this->request->isPost()) {
            return $this->response->setStatusCode(405, 'Method Not Allowed');
        }
        $requested = (int)$this->request->getPost('rowCount', 'int', 50);
        // -1 is the explicit All selection; zero means unlimited to queryLog.
        $limit = $requested === -1 ? 0 : max(1, min(9999, $requested));
        $page = max(1, (int)$this->request->getPost('current', 'int', 1));
        $backend = new Backend();
        $result = json_decode($backend->configdpRun('opncell queryLog', [
            $limit, $limit === 0 ? 0 : ($page - 1) * $limit, $search, $scope, $severity, $since
        ]), true);
        if (!is_array($result) || !isset($result['rows'])) {
            return $this->response->setStatusCode(500, 'Unable to read log');
        }
        $result['rowCount'] = count($result['rows']);
        $result['total'] = $result['total_rows'] ?? count($result['rows']);
        $result['current'] = $page;
        return $result;
    }

    public function clearAction($scope = '')
    {
        if (!$this->request->isPost()) {
            return $this->response->setStatusCode(405, 'Method Not Allowed');
        }
        $scope = ServiceNames::logScope($scope);
        if ($scope === null) {
            return $this->response->setStatusCode(404, 'Not Found');
        }
        $active = $this->activeSnapshot();
        if ($active === null || !in_array($scope, array_column($active, 'scope'), true)) {
            return ['status' => 'failed', 'message' => gettext('This daemon is not running.')];
        }
        $result = json_decode((new Backend())->configdpRun('opncell clearLog', [$scope]), true);
        return is_array($result) ? $result : [
            'status' => 'failed', 'message' => gettext('Unable to clear the log file.')
        ];
    }
}
