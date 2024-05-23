<?php
namespace OPNsense\HelloWorld;

class IndexController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        // pick the template to serve to our users.
        $this->view->pick('OPNsense/HelloWorld/index');
        $this->view->generalForm = $this->getForm("general");
    }
}
