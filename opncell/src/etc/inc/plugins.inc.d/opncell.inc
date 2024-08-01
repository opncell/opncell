<?php

/*
 * Copyright (C) 2023 Digital Solutions
 * Copyright (C) 2023 Wire Lab
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

use OPNsense\OPNCell\General;

function fourG_enabled(): bool
{
    $model = new General();
    return $model->enablefour->__toString() == "1";
}

function fiveGSA_enabled(): bool
{
    $model = new General();
    return $model->enablefiveSA->__toString() == "1";

}

function fiveGNSA_enabled(): bool
{
    $model = new General();
    return $model->enablefiveNSA->__toString() == "1";
}

function upf_enabled(): bool
{
    $model = new General();
    return $model->enableupf->__toString() == "1";
}

function opncell_services():array
{
    $services = array();

    $commonServiceData = array(
        'configd' => array(
            'restart' => array('%sd restart'),
            'start' => array('%sd start'),
            'stop' => array('%sd stop'),
        ),
        'pidfile' => '/var/run/epc/epc%sd.pid',
    );

    $descriptions = array(
        'mme' => gettext('Mobility Management Entity'),
        'hss' => gettext('Home Subscriber System'),
        'pcrf' => gettext('Policy and Charging Rules Function'),
        'sgwu' => gettext('Serving Gateway User Plane Daemon'),
        'ausf' => gettext('Authentication Server Function'),
        'amf' => gettext('Access and Mobility Function'),
        'udm' => gettext('Unified Data Management'),
        'smf' => gettext('Session Management Function'),
        'pcf' => gettext('Policy and Charging Function'),
        'nssf' => gettext('Network Slice Selection Function'),
        'sgwc' => gettext('Serving Gateway Control Plane'),
        'upf' => gettext('User Plane Function'),
        'nrf' => gettext('Network Repository Function'),
        'scp' => gettext('Service Communication Proxy'),
        'bsf' => gettext('Binding Support Function'),
        'mongod' => gettext('Mongo DB'),
        'udr' => gettext('Unified Data Repository'),

    );

    if (fourG_enabled()) {
        $serviceTypes = array('mme', 'hss', 'pcrf', 'sgwu','sgwc','smf','upf');
    } elseif (fiveGSA_enabled()) {
        $serviceTypes = array('nrf','scp','amf','smf','upf','ausf', 'udm', 'udr', 'pcf',  'nssf', 'bsf');
    } elseif (fiveGNSA_enabled()) {
        $serviceTypes = array('mme', 'hss', 'pcrf', 'sgwu','sgwc','smf','upf');
    } elseif (upf_enabled()) {
        $serviceTypes = array('amf', 'smf', 'upf', 'udm','nssf','udr','pcf', 'ausf');
    } else {
        return $services;
    }

    foreach ($serviceTypes as $type) {
        $service = array(
            'description' => $descriptions[$type],
            'name' => 'opncell-' . $type,
        );

        foreach ($commonServiceData['configd'] as $key => $commands) {
            $service['configd'][$key] = array(sprintf($commands[0], $type));
        }

        $service['pidfile'] = sprintf($commonServiceData['pidfile'], $type);

        $services[] = $service;
    }
    return $services;
}
