<?php

/**
 * This file is part of the Phalcon Migrations.
 *
 * (c) Phalcon Team <team@phalcon.io>
 *
 * For the full copyright and license information, please view
 * the LICENSE file that was distributed with this source code.
 */

declare(strict_types=1);

namespace Phalcon\Migrations\Db\Dialect;

use Phalcon\Db\Dialect\Postgresql;

class DialectPostgresql extends Postgresql
{
    /**
     * Generates SQL to query foreign keys on a table
     *
     * @param string $table
     * @param string $schema
     * @return string
     */
    public function describeReferences(string $table, string $schema = null): string
    {
        $sql = "
            SELECT DISTINCT
              tc.table_name as TABLE_NAME,
              kcu.column_name as COLUMN_NAME,
              tc.constraint_name as CONSTRAINT_NAME,
              tc.table_schema as REFERENCED_TABLE_SCHEMA,
              ccu.table_name AS REFERENCED_TABLE_NAME,
              ccu.column_name AS REFERENCED_COLUMN_NAME,
              rc.update_rule AS UPDATE_RULE,
              rc.delete_rule AS DELETE_RULE
            FROM information_schema.table_constraints AS tc
              JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
              JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
              JOIN information_schema.referential_constraints rc
                ON tc.constraint_catalog = rc.constraint_catalog
                AND tc.constraint_schema = rc.constraint_schema
                AND tc.constraint_name = rc.constraint_name
                AND  tc.constraint_type = 'FOREIGN KEY'
            WHERE constraint_type = 'FOREIGN KEY'
                AND ";

        if ($schema) {
            $sql .= "tc.table_schema = '" . $schema . "' AND tc.table_name='" . $table . "'";
        } else {
            $sql .= "tc.table_schema = 'public' AND tc.table_name='" . $table . "'";
        }

        return $sql;
    }
    public function describeIndexes(string $table, string $schema = null): string
    {
        return "
            SELECT 
                t.relname as table_name, 
                NOT ix.indisunique AS non_unique, 
                i.relname as key_name, 
                ix.indisprimary AS is_primary, 
                a.attname as column_name 
            FROM pg_class t, pg_class i, pg_index ix, pg_attribute a 
            WHERE 
                t.oid = ix.indrelid 
                AND i.oid = ix.indexrelid 
                AND a.attrelid = t.oid 
                AND a.attnum = ANY(ix.indkey) 
                AND t.relkind = 'r' 
                AND t.relname = '" . $table . "' 
            ORDER BY t.relname, i.relname;
        ";
    }
}
