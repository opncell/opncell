<?php

/**
 * This file is part of the Cop package.
 *
 * (c) Phalcon Team <team@phalconphp.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

return [
    [
        'params' => [
            'key' => 'key1',
            'default' => false,
            'argv' => [
                '/usr/bin/phalcon',
                '--key1',
                '1',
            ],
        ],
        'expect' => true,
    ],
    [
        'params' => [
            'key' => 'key2',
            'default' => true,
            'argv' => [
                '/usr/bin/phalcon',
                '--key2',
                '0',
            ],
        ],
        'expect' => false,
    ],
    [
        'params' => [
            'key' => 'key3',
            'default' => false,
            'argv' => [
                '/usr/bin/phalcon',
                '--key3',
                'y',
            ],
        ],
        'expect' => true,
    ],
    [
        'params' => [
            'key' => 'key4',
            'default' => true,
            'argv' => [
                '/usr/bin/phalcon',
                '--key4',
                'n',
            ],
        ],
        'expect' => false,
    ],
    [
        'params' => [
            'key' => 'key5',
            'default' => false,
            'argv' => [
                '/usr/bin/phalcon',
                '--key5',
                'yes',
            ],
        ],
        'expect' => true,
    ],
    [
        'params' => [
            'key' => 'key6',
            'default' => true,
            'argv' => [
                '/usr/bin/phalcon',
                '--key6',
                'no',
            ],
        ],
        'expect' => false,
    ],
    [
        'params' => [
            'key' => 'key7',
            'default' => false,
            'argv' => [
                '/usr/bin/phalcon',
                '--key7',
                'true',
            ],
        ],
        'expect' => true,
    ],
    [
        'params' => [
            'key' => 'key8',
            'default' => true,
            'argv' => [
                '/usr/bin/phalcon',
                '--key8',
                'false',
            ],
        ],
        'expect' => false,
    ],
    [
        'params' => [
            'key' => 'key9',
            'default' => false,
            'argv' => [
                '/usr/bin/phalcon',
                '--key9',
                'on',
            ],
        ],
        'expect' => true,
    ],
    [
        'params' => [
            'key' => 'key10',
            'default' => true,
            'argv' => [
                '/usr/bin/phalcon',
                '--key10',
                'off',
            ],
        ],
        'expect' => false,
    ],
    [
        'params' => [
            'key' => 'key11',
            'default' => false,
            'argv' => [
                '/usr/bin/phalcon',
                '--key11',
            ],
        ],
        'expect' => true,
    ],
    [//test default param
        'params' => [
            'key' => 'key13',
            'default' => false,
            'argv' => [
                '/usr/bin/phalcon',
                '--key12',
            ],
        ],
        'expect' => false,
    ],
];
