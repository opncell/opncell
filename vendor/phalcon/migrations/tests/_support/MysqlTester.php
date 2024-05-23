<?php

/**
 * Inherited Methods
 * @method void wantToTest($text)
 * @method void wantTo($text)
 * @method void execute($callable)
 * @method void expectTo($prediction)
 * @method void expect($prediction)
 * @method void amGoingTo($argumentation)
 * @method void am($role)
 * @method void lookForwardTo($achieveValue)
 * @method void comment($description)
 * @method void pause()
 *
 * @SuppressWarnings(PHPMD)
*/
class MysqlTester extends \Codeception\Actor
{
    use _generated\MysqlTesterActions;

   /**
    * Define custom actions here
    */
    public function seeExceptionThrown($exception, $function): ?bool
    {
        try {
            $function();

            return false;
        } catch (\Throwable $throwable) {
            return get_class($throwable) === $exception;
        }
    }
}
