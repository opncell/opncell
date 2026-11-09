<?php
require __DIR__ . '/../../opncell/src/opnsense/mvc/app/models/OPNsense/OPNCell/SubscriberCsv.php';
use OPNsense\OPNCell\SubscriberCsv;
function readCsv($csv) {
    $stream = fopen('php://temp', 'w+');
    fwrite($stream, $csv);
    rewind($stream);
    $rows = [];
    while (($row = fgetcsv($stream, 0, ',', '"', '')) !== false) $rows[] = $row;
    fclose($stream);
    return $rows;
}
$template = readCsv(SubscriberCsv::encode());
if ($template !== [SubscriberCsv::FIELDS]) throw new RuntimeException('Template must contain only supported headers');
$row = ['imsi'=>'001010000000001', 'msisdn'=>'12345,67890', 'profiles'=>'["1/internet","2/ims"]',
        'session_addresses'=>'{"1/internet":{"ue":{"ipv4":"10.0.0.1"}}}', 'pcc_rules'=>'{}'];
$export = readCsv(SubscriberCsv::encode([$row]));
if ($export[0] !== $template[0]) throw new RuntimeException('Export and template headers differ');
$decoded = array_combine($export[0], $export[1]);
foreach ($row as $key => $value) {
    if ($decoded[$key] !== $value) throw new RuntimeException('CSV quoting or leading zeros lost: '.$key);
}
echo "SUCCESS: header-only template and subscriber CSV round-trip passed\n";
