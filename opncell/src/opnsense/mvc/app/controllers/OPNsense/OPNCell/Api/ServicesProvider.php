<?php

namespace OPNsense\Base;

use Phalcon\Di\DiInterface;
use Phalcon\Di\ServiceProviderInterface;
use OPNsense\Core\Backend;

class ServicesProvider implements ServiceProviderInterface
{

    public function register(DiInterface $di)
    {
        $backend = new Backend();
        $di->setShared('fileUploadService', function () {
            return new FileUploadService();
        });

        $di->setShared('userRepository', function () use ($backend) {
            return new UserRepository($backend);
        });
    }
}