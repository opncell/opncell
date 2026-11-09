<?php

require_once 'config.inc';

use OPNsense\Core\Backend;
use OPNsense\Core\Config;

$services = [
    '127.0.0.2' => 'MME',
    '127.0.0.3' => 'SGW-C',
    '127.0.0.4' => 'SMF',
    '127.0.0.5' => 'AMF',
    '127.0.0.6' => 'SGW-U',
    '127.0.0.7' => 'UPF',
    '127.0.0.8' => 'HSS',
    '127.0.0.9' => 'PCRF',
    '127.0.0.10' => 'NRF',
    '127.0.0.11' => 'AUSF',
    '127.0.0.12' => 'UDM',
    '127.0.0.13' => 'PCF',
    '127.0.0.14' => 'NSSF',
    '127.0.0.15' => 'BSF',
    '127.0.0.16' => 'SBI',
    '127.0.0.17' => 'SBI',
    '127.0.0.18' => 'SBI',
    '127.0.0.19' => 'SBI',
    '127.0.0.20' => 'UDR',
    '127.0.1.10' => 'SCP',
    '127.0.0.200' => 'SBI',
    '127.0.0.250' => 'SBI',
    '127.0.0.251' => 'N32',
    '127.0.0.252' => 'N32-f',
];

$config = Config::getInstance();
$added = 0;
try {
    $config->lock();
    $root = $config->object();
    $existing = [];
    foreach ($root->virtualip->vip ?? [] as $vip) {
        $existing[(string)$vip->subnet] = true;
    }
    foreach ($root->interfaces->children() ?? [] as $interface) {
        $existing[(string)$interface->ipaddr] = true;
    }

    foreach ($services as $address => $service) {
        if (isset($existing[$address])) {
            continue;
        }
        if (!isset($root->virtualip)) {
            $root->addChild('virtualip');
        }
        // UUIDv4, as used for entries created through the Virtual IPs UI.
        $bytes = random_bytes(16);
        $bytes[6] = chr((ord($bytes[6]) & 0x0f) | 0x40);
        $bytes[8] = chr((ord($bytes[8]) & 0x3f) | 0x80);
        $uuid = vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($bytes), 4));

        $vip = $root->virtualip->addChild('vip');
        $vip->addAttribute('uuid', $uuid);
        $vip->addChild('mode', 'ipalias');
        $vip->addChild('interface', 'lo0');
        $vip->addChild('subnet', $address);
        $vip->addChild('subnet_bits', '8');
        $vip->addChild('noexpand', '0');
        $vip->addChild('nobind', '0');
        $vip->addChild('advbase', '1');
        $vip->addChild('advskew', '0');
        $vip->addChild('nosync', '0');
        $vip->addChild('descr', $service);
        $added++;
    }

    if ($added > 0) {
        $config->save();
    }
} finally {
    $config->unlock();
}

if ($added > 0) {
    $result = trim((string)(new Backend())->configdRun('interface vip configure'));
    if ($result !== 'OK') {
        fwrite(STDERR, "Loopback VIPs were saved. Apply them in Interfaces > Virtual IPs.\n");
        exit(1);
    }
}
echo "=====> Added {$added} OPNcell loopback virtual IPs\n";
