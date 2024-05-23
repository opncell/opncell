# Cop


[![Software License](https://img.shields.io/badge/license-BSD--3-brightgreen.svg)](https://github.com/phalcon/cli-options-parser/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/phalcon/cli-options-parser.svg?branch=master)](https://travis-ci.org/phalcon/cli-options-parser)
[![Code Coverage](https://codecov.io/gh/phalcon/cli-options-parser/branch/master/graph/badge.svg)](https://codecov.io/gh/phalcon/cli-options-parser)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/phalcon/cli-options-parser/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/phalcon/cli-options-parser/?branch=master)
[![Scrutinizer Build Status](https://scrutinizer-ci.com/g/phalcon/cli-options-parser/badges/build.png?b=master)](https://scrutinizer-ci.com/g/phalcon/cli-options-parser/build-status/master)

Command line arguments/options parser.

## Requirements

* PHP >= 7.0

## Installing via [Composer](https://getcomposer.org)

Install composer in a common location or in your project:

```bash
composer require phalcon/cli-options-parser
```

## Usage

```php
use Phalcon\Cop\Parser;

$parser = new Parser();

// Parse params from the $argv
$params = $parser->parse($argv);

// Parse params from the $_SERVER['argv']
$params = $parser->parse();

// After parsing input, Parser provides a way to gets booleans:
$parser->getBoolean('foo');

// Get param `foo` or return TRUE as a default value
$parser->getBoolean('foo', true);
```

### Examples

```
php test.php -az value1 -abc value2
[
    'a' => 'value2',
    'z' => 'value1',
    'b' => 'value2',
    'c' => 'value2',
]

php test.php -a value1 -abc value2
[
    'a'  => 'value2',
    'b'  => 'value2',
    'c'  => 'value2',
]

php test.php --az value1 --abc value2
[
    'az'  => 'value1',
    'abc' => 'value2',
]

php test.php --foo --bar=baz --spam eggs
[
    'foo'  => true,
    'bar'  => 'baz',
    'spam' => 'eggs',
]

php test.php -abc foo
[
    'a' => 'foo',
    'b' => 'foo',
    'c' => 'foo',
]

php test.php arg1 arg2 arg3
[
    0 => 'arg1',
    1 => 'arg2',
    2 => 'arg3',
]

php test.php \
    plain-arg \
    --foo \
    --bar=baz \
    --funny="spam=eggs" \
    --also-funny=spam=eggs \
    'plain arg 2'
    -abc \
    -k=value \
    "plain arg 3" \
    --s="original" \
    --s='overwrite' \
    --s
[
    0            => 'plain-arg',
    'foo'        => true,
    'bar'        => 'baz',
    'funny'      => 'spam=eggs',
    'also-funny' => 'spam=eggs',
    1            => 'plain arg 2',
    'a'          => true,
    'b'          => true,
    'c'          => true,
    'k'          => 'value',
    2            => 'plain arg 3',
    's'          => 'overwrite',
]
```

## License

The Cop is open source software licensed under the [New BSD License](https://github.com/phalcon/cli-options-parser/blob/master/LICENSE.txt).<br>
© Phalcon Team
