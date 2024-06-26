<?php

declare(strict_types=1);

/*
 * This file is part of the humbug/php-scoper package.
 *
 * Copyright (c) 2017 Théo FIDRY <theo.fidry@gmail.com>,
 *                    Pádraic Brady <padraic.brady@gmail.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

return [
    'meta' => [
        'title' => 'Self and parent keywords as return types',
        // Default values. If not specified will be the one used
        'prefix' => 'Humbug',
        'whitelist' => [],
        'whitelist-global-constants' => true,
        'whitelist-global-classes' => false,
        'whitelist-global-functions' => true,
        'registered-classes' => [],
        'registered-functions' => [],
    ],

    'Usage for classes in the global scope' => <<<'PHP'
<?php

class A {
    protected $name;
    public function __construct(string $name)
    {
        $this->name = $name;
    }
    public function normalize() : self
    {
        $instance = clone $this;
        $instance->name = \strtolower($this->name);
        return $instance;
    }
    public function getName() : string
    {
        return $this->name;
    }
}

class B extends A {
    
    public function normalize() : parent
    {
        $instance = clone $this;
        $instance->name = \strtoupper($this->name);
        return $instance;
    }
}

echo (new B('yo'))->normalize()->getName().PHP_EOL;

----
<?php

namespace Humbug;

class A
{
    protected $name;
    public function __construct(string $name)
    {
        $this->name = $name;
    }
    public function normalize() : self
    {
        $instance = clone $this;
        $instance->name = \strtolower($this->name);
        return $instance;
    }
    public function getName() : string
    {
        return $this->name;
    }
}
class B extends \Humbug\A
{
    public function normalize() : parent
    {
        $instance = clone $this;
        $instance->name = \strtoupper($this->name);
        return $instance;
    }
}
echo (new \Humbug\B('yo'))->normalize()->getName() . \PHP_EOL;

PHP
    ,

    'Usage for classes in a namespaced' => <<<'PHP'
<?php

namespace Foo {
    class A {
        protected $name;
        public function __construct(string $name)
        {
            $this->name = $name;
        }
        public function normalize() : self
        {
            $instance = clone $this;
            $instance->name = \strtolower($this->name);
            return $instance;
        }
        public function getName() : string
        {
            return $this->name;
        }
    }
        
    class B extends A {
        public function normalize() : parent
        {
            $instance = clone $this;
            $instance->name = strtoupper($this->name);
            return $instance;
        }
    }
}

namespace {
    use Foo\B;

    echo (new B('yo'))->normalize()->getName().PHP_EOL;
}

----
<?php

namespace Humbug\Foo;

class A
{
    protected $name;
    public function __construct(string $name)
    {
        $this->name = $name;
    }
    public function normalize() : self
    {
        $instance = clone $this;
        $instance->name = \strtolower($this->name);
        return $instance;
    }
    public function getName() : string
    {
        return $this->name;
    }
}
class B extends \Humbug\Foo\A
{
    public function normalize() : parent
    {
        $instance = clone $this;
        $instance->name = \strtoupper($this->name);
        return $instance;
    }
}
namespace Humbug;

use Humbug\Foo\B;
echo (new \Humbug\Foo\B('yo'))->normalize()->getName() . \PHP_EOL;

PHP
    ,
];
