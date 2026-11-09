<?php

namespace OPNsense\OPNCell\Menu;

use OPNsense\Base\Menu\MenuContainer;
use OPNsense\Core\Backend;
use OPNsense\OPNCell\ServiceNames;

class Menu extends MenuContainer
{
    public function collect()
    {
        $snapshot = json_decode((new Backend())->configdpRun('opncell activeLogs', []), true);
        if (!is_array($snapshot) || ($snapshot['status'] ?? '') !== 'ok' || !is_array($snapshot['rows'] ?? null)) {
            return;
        }
        $seen = [];
        foreach ($snapshot['rows'] as $row) {
            $name = $row['name'] ?? null;
            if (!is_string($name) || ServiceNames::topic($name) === null) {
                continue;
            }
            $name = ServiceNames::canonical(ServiceNames::topic($name));
            if (isset($seen[$name])) {
                continue;
            }
            $seen[$name] = true;
            $this->appendItem('Cellular.FourG', str_replace('-', '_', $name), [
                'VisibleName' => $name,
                'url' => '/ui/opncell/log/index/' . $name,
            ]);
        }
    }
}
