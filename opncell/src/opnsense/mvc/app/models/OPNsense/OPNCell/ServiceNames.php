<?php

namespace OPNsense\OPNCell;

final class ServiceNames
{
    private const OPEN5GS_TOPICS = [
        'amfd', 'ausfd', 'bsfd', 'hssd', 'mmed', 'nrfd', 'nssfd', 'pcfd',
        'pcrfd', 'scpd', 'sgwcd', 'sgwud', 'smfd', 'udmd', 'udrd', 'upfd',
    ];

    public static function topic(string $name): ?string
    {
        if ($name === 'mongod' || $name === 'mongodd') {
            return 'mongod';
        }

        $topic = str_starts_with($name, 'open5gs-') ? substr($name, 8) : $name;
        return in_array($topic, self::OPEN5GS_TOPICS, true) ? $topic : null;
    }

    public static function canonical(string $topic): string
    {
        return $topic === 'mongod' ? $topic : 'open5gs-' . $topic;
    }

    public static function logScope(string $name): ?string
    {
        $topic = self::topic($name) ?? self::topic($name . 'd');
        if ($topic === null) {
            return null;
        }
        return $topic === 'mongod' ? $topic : substr($topic, 0, -1);
    }
}
