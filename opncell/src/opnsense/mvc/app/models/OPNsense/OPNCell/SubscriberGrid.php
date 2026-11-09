<?php
namespace OPNsense\OPNCell;

/** Sorting must precede pagination; IMSIs remain string identifiers. */
class SubscriberGrid
{
    public static function page(array $rows, $sort, int $rowCount, int $current): array
    {
        $sort = is_array($sort) ? array_intersect_key($sort, array_flip(['imsi', 'profile'])) : [];
        $field = array_key_first($sort) ?? 'imsi';
        $direction = ($sort[$field] ?? 'asc') === 'desc' ? -1 : 1;
        usort($rows, static function (array $a, array $b) use ($field, $direction): int {
            $left = (string)($a[$field] ?? '');
            $right = (string)($b[$field] ?? '');
            $comparison = $field === 'profile' ? strnatcasecmp($left, $right) : strcmp($left, $right);
            if ($comparison !== 0) {
                return $direction * $comparison;
            }
            // Stable page boundaries when many subscribers share one profile.
            return strcmp((string)$a['imsi'], (string)$b['imsi']);
        });
        $total = count($rows);
        $current = max(1, $current);
        if ($rowCount === -1) {
            $current = 1;
            $page = $rows;
        } else {
            $rowCount = max(1, min(10000, $rowCount));
            $page = array_slice($rows, ($current - 1) * $rowCount, $rowCount);
        }
        return ['total' => $total, 'rowCount' => $rowCount, 'current' => $current, 'rows' => $page];
    }
}
