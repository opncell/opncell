<?php
namespace OPNsense\HelloWorld;

class FiveGNSAController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        // pick the template to serve to our users.
        $this->view->pick('OPNsense/HelloWorld/fiveGNSA');
    }
}
