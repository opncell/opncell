<?php declare(strict_types=1);

/**
 * This file is part of the Cop package.
 *
 * (c) Phalcon Team <team@phalconphp.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

namespace Phalcon\Cop\Tests;

use Phalcon\Cop\Parser;
use PHPUnit\Framework\TestCase;
use stdClass;

/**
 * Phalcon\Cop\Tests\ParserTest
 *
 * @package Phalcon\Cop\Tests
 */
class ParserTest extends TestCase
{
    /** @var Parser */
    protected $parser;

    /**
     * {@inheritdoc}
     *
     * @return void
     */
    public function setUp():void
    {
        $this->parser = new Parser();
    }

    /**
     * @test
     * @dataProvider parseProvider
     *
     * @param array $params
     * @param array $expect
     */
    public function shouldParseCliCommand($params, $expect)
    {
        $this->assertEquals($expect, $this->parser->parse($params['command']));
    }

    /** @test */
    public function shouldParseCommandFromTheServer()
    {
        $_SERVER['argv'] = ['script.php', 'arg1', 'arg2', 'arg3'];

        $this->assertEquals(['arg1', 'arg2', 'arg3'], $this->parser->parse());
    }

    /**
     * @test
     * @dataProvider booleanProvider
     *
     * @param array $params
     * @param bool  $expect
     */
    public function shouldTransformParamsToBool($params, $expect)
    {
        $this->parser->parse($params['argv']);

        $this->assertEquals($expect, $this->parser->getBoolean($params['key'], $params['default']));
    }

    public function testGetParsedCommandsShouldReturnEmptyArrayOnNewObject()
    {
        $parser = new Parser();
        $this->assertEmpty(
            $parser->getParsedCommands(),
            "It's expected to receive an empty array if no parsing has been done yet."
        );
    }

    /**
     * @test
     * @dataProvider parseProvider
     *
     * @param array $params
     * @param array $expect
     */
    public function testGetParsedCommandsShouldReturnParsedCommand(array $params, array $expect)
    {
        $this->parser->parse($params["command"]);
        $this->assertEquals(
            $expect,
            $this->parser->getParsedCommands(),
            "Parsed commands should be returned."
        );
        $this->parser->parse(["script-with-no-parameters"]);
        $this->assertEmpty(
            $this->parser->getParsedCommands(),
            "Parser state should be modified absolutely, 
            if overridden by another parse call."
        );

        $this->parser->parse($params["command"]);
        $this->assertEquals(
            $expect,
            $this->parser->getParsedCommands(),
            "Parsed commands should be returned after re-parsing original command."
        );
    }

    /**
     * @test
     * @dataProvider parseProvider
     *
     * @param array $params
     * @param array $expect
     */
    public function testGetReturnsBoundDefaultValueIfNotSet(array $params, array $expect)
    {
        $expectedDefaultValues = [
            123,
            "test",
            12.3,
            true,
            new stdClass()
        ];
        
        $nonExistingParameterKey = "non-existing-parameter-key";

        foreach ($expectedDefaultValues as $expectedDefaultValue) {
            $this->assertEquals(
                $expectedDefaultValue,
                $this->parser->get($nonExistingParameterKey, $expectedDefaultValue),
                "Should return the provided default value, 
                if the queried parameter doesn't exist in an empty/fresh object."
            );
        }

        $this->parser->parse($params["command"]);

        foreach ($expectedDefaultValues as $expectedDefaultValue) {
            $this->assertEquals(
                $expectedDefaultValue,
                $this->parser->get($nonExistingParameterKey, $expectedDefaultValue),
                "Should return null, 
                if the queried parameter doesn't exist in a populated/parsed object."
            );
        }
    }

    /**
     * @test
     * @dataProvider parseProvider
     *
     * @param array $params
     * @param array $expect
     */
    public function testGetReturnsNullIfParamDoesNotExist(array $params, array $expect)
    {
        $nonExistingParameterKey = "non-existing-parameter-key";
        $this->assertNull(
            $this->parser->get($nonExistingParameterKey),
            "Should return null,
            if the queried parameter doesn't exist in an empty/fresh object."
        );

        $this->parser->parse($params["command"]);
        $this->assertNull(
            $this->parser->get($nonExistingParameterKey),
            "Should return null,
            if the queried parameter doesn't exist in a populated/parsed object."
        );
    }

    /**
     * @test
     * @dataProvider parseProvider
     *
     * @param array $params
     * @param array $expect
     */
    public function testGetReturnsValueIfParamDoesExist(array $params, array $expect)
    {
        $this->parser->parse($params["command"]);
        foreach ($expect as $parameterKey => $expectedValue) {
            $this->assertEquals(
                $expectedValue,
                $this->parser->get($parameterKey),
                "It's expected to have the value returned untouched."
            );
        }
    }

    public function parseProvider()
    {
        return include __DIR__ . '/fixtures/parse_parameters.php';
    }

    public function booleanProvider()
    {
        return include __DIR__ . '/fixtures/boolean_parameters.php';
    }
}
