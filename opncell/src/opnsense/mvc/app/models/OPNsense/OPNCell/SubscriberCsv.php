<?php

namespace OPNsense\OPNCell;

final class SubscriberCsv
{
    public const FIELDS = [
        'imsi',
        'ki',
        'opc',
        'op',
        'amf',
        'msisdn',
        'profiles',
        'ue_ambr_downlink',
        'ue_ambr_downlink_unit',
        'ue_ambr_uplink',
        'ue_ambr_uplink_unit',
        'subscriber_status',
        'operator_determined_barring',
        'default_slice',
        'session_addresses',
        'pcc_rules'
    ];

    public static function encode(array $rows = []): string
    {
        $stream = fopen('php://temp', 'w+');
        fputcsv($stream, self::FIELDS, ',', '"', '');
        foreach ($rows as $row) {
            fputcsv($stream, array_map(fn($field) => $row[$field] ?? '', self::FIELDS), ',', '"', '');
        }
        rewind($stream);
        $csv = stream_get_contents($stream);
        fclose($stream);
        return $csv;
    }
}
