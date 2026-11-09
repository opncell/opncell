<?php
require __DIR__ . '/../../opncell/src/opnsense/mvc/app/models/OPNsense/OPNCell/SubscriberGrid.php';
use OPNsense\OPNCell\SubscriberGrid;
function expect($actual, $expected, $message) {
    if ($actual !== $expected) {
        throw new RuntimeException($message . ': ' . json_encode($actual));
    }
}
$rows = [
    ['imsi' => '9999999999999999', 'profile' => 'profile10'],
    ['imsi' => '001010000000002', 'profile' => 'Profile2'],
    ['imsi' => '001010000000001', 'profile' => 'profile2'],
];
expect(array_column(SubscriberGrid::page($rows, ['imsi' => 'asc'], 1, 2)['rows'], 'imsi'),
       ['001010000000002'], 'Sorting must precede pagination');
expect(array_column(SubscriberGrid::page($rows, ['imsi' => 'desc'], -1, 1)['rows'], 'imsi'),
       ['9999999999999999', '001010000000002', '001010000000001'], 'Descending IMSI preserves digits');
expect(array_column(SubscriberGrid::page($rows, ['profile' => 'asc'], -1, 1)['rows'], 'imsi'),
       ['001010000000001', '001010000000002', '9999999999999999'], 'Natural profile ordering and stable tie break');
expect(SubscriberGrid::page($rows, ['commands' => 'desc'], 1, 1)['rows'][0]['imsi'],
       '001010000000001', 'Unknown columns use safe default');
expect(count(SubscriberGrid::page($rows, null, -1, 3)['rows']), 3, 'All rows works');
expect(SubscriberGrid::page([], [], 0, -1)['rows'], [], 'Empty and invalid pagination');
echo "SUCCESS: 6 subscriber sorting/pagination checks passed\n";
