<?php
namespace OPNsense\HelloWorld;

class FiveGSAController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        // pick the template to serve to our users.
        $this->view->pick('OPNsense/HelloWorld/fiveGSA');
        $this->view->generalFiveGSAForm = $this->getForm("generalFiveGSA");
    }
}
