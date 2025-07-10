<?php

namespace OPNsense\Base;

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