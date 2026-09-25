<?php

/**
 *    Copyright (C) 2023 Digital Solutions <support@ds.co.ug>
 *     Copyright (C) 2023 Wire labs Technologies <wirelabs@ds.co.ug>
 *
 *    All rights reserved.
 *
 *    Redistribution and use in source and binary forms, with or without
 *    modification, are permitted provided that the following conditions are met:
 *
 *    1. Redistributions of source code must retain the above copyright notice,
 *       this list of conditions and the following disclaimer.
 *
 *    2. Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *
 *    THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 *    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 *    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *    AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 *    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 *    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 *    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 *    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 *    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *    POSSIBILITY OF SUCH DAMAGE.
 *
 */

namespace OPNsense\Base;

namespace OPNsense\OPNCell\Api;

use OPNsense\Base\ApiMutableModelControllerBase;
use OPNsense\Base\UIModelGrid;
use OPNsense\Base\UserException;
use OPNsense\Core\Config;
use OPNsense\Core\Backend;
use OPNsense\Mvc\Request;
use ReflectionException;
use OPNsense\OPNCell\Hnet;
use OPNsense\OPNCell\General;
use OPNsense\Phalcon\Filter\Filter;


class HnetController extends ApiMutableModelControllerBase
{

    protected static $internalModelName = 'hnet';
    protected static $internalModelClass = '\OPNsense\OPNCell\Hnet';

     public \OPNsense\Mvc\Request $request;

   public function getAction()
     {
         $result = array();
             $mdlHnet = new Hnet();
             $result['hnet'] = $mdlHnet->getNodes();
             return $result;
     }

   public function addAction(): array
     {
       $result = array("result" => "failed");

               $mdlHnet = new Hnet();
               $this->request = new Request();
               $mdlHnet->setNodes($this->request->getPost("hnet"));

               $valMsgs = $mdlHnet->performValidation();

               if ($valMsgs->count() > 0) {
                   foreach ($valMsgs as $msg) {
                       if (!isset($result["validations"])) {
                           $result["validations"] = array();
                       }
                       $result["validations"]["hnet." . $msg->getField()] = $msg->getMessage();
                   }
                   return $result;
               }

               //serialize model to config and save
               $mdlHnet->serializeToConfig();
               $result = Config::getInstance()->save();
               $result["result"] = "saved";

               return $result;
     }

   public function generateAction(): array
     {
         $backend = new Backend();

         $mdlHnet = new Hnet();
         $hnet_values = $mdlHnet->getNodes();
         $val = $this->prepareHnetForKeyGeneration($hnet_values);

         $val_encoded = base64_encode(json_encode($val));
         $raw = $backend->configdpRun("opncell showHnet", $val_encoded);
         $decoded = json_decode((string)$raw, true);

         return [
             "result" => "ok",
             "data" => $decoded
         ];
     }

   public function listAction(): array
     {
         $backend = new Backend();

         $raw = $backend->configdRun("opncell listHnet");
         $decoded = json_decode((string)$raw, true);

         return [
             "result" => "ok",
             "data" => $decoded
         ];
     }
private function prepareHnetForKeyGeneration($hnetData)
{
    $scheme = 2; // default to Profile B

    if (isset($hnetData['scheme'])) {
        foreach ($hnetData['scheme'] as $key => $option) {
            if (!empty($option['selected'])) {
                $scheme = ($key === 'profileA') ? 1 : 2;
                break;
            }
        }
    }

   $pubkeyPath = rtrim($hnetData['filepath'], '/').'/hnet_pubkey_';

    // Ensure directory exists
    $dir = dirname($pubkeyPath);
    if (!is_dir($dir)) {
        mkdir($dir, 0755, true);
    }


    return [ 'id'   => (int)$hnetData['id'],
        'scheme'      => $scheme,
        'pubkey_path' => $pubkeyPath
    ];
}
     }

