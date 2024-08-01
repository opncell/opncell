<?php

namespace OPNsense\Base;

namespace OPNsense\OPNCore\Api;

trait UserControllerTrait
{
    private $userRepository;
    private $fileUploadService;

    protected function initializeServices()
    {
        $this->userRepository = $this->di->get('userRepository');
        $this->fileUploadService = $this->di->get('fileUploadService');
    }
}
