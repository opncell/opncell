<?php
namespace OPNsense\HelloWorld;

class FourGSAController extends \OPNsense\Base\IndexController
{
    public function fourGSAAction()
    {
        // pick the template to serve to our users.
        $this->view->pick('OPNsense/HelloWorld/fourGSA');
        $this->view->dialog4GSAForm = $this->getForm("dialog4GSA");
    }
}
