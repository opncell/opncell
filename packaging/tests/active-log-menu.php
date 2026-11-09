<?php
namespace OPNsense\Base\Menu {
    class MenuContainer {
        public array $items = [];
        public function appendItem($root, $id, $properties) { $this->items[$root.'.'.$id] = $properties; }
    }
}
namespace OPNsense\Core {
    class Backend {
        public static array $snapshot = ['status'=>'ok','rows'=>[
            ['name'=>'open5gs-mmed'], ['name'=>'mongod'], ['name'=>'open5gs-mmed'], ['name'=>'untrusted']
        ]];
        public function configdpRun($action, $args) { return json_encode(self::$snapshot); }
    }
}
namespace {
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/models/OPNsense/OPNCell/ServiceNames.php';
    require __DIR__.'/../../opncell/src/opnsense/mvc/app/models/OPNsense/OPNCell/Menu/Menu.php';
    $menu = new OPNsense\OPNCell\Menu\Menu(); $menu->collect();
    if (count($menu->items) !== 2 || array_column($menu->items, 'url') !== [
        '/ui/opncell/log/index/open5gs-mmed', '/ui/opncell/log/index/mongod'
    ]) throw new RuntimeException('Menu did not restrict entries to known active daemons');
    OPNsense\Core\Backend::$snapshot=['status'=>'failed'];
    $menu = new OPNsense\OPNCell\Menu\Menu(); $menu->collect();
    if ($menu->items) throw new RuntimeException('Backend failure exposed inactive entries');
    echo "SUCCESS: active daemon submenu checks passed\n";
}
