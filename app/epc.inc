<?php

/*
 * Copyright (C) 2023 Digital Solutions
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

function fourG_enabled(): bool
{
    $model = new \OPNsense\OPNCore\General();
    return (string)$model->enablefour == '1';
}

function fiveGSA_enabled(): bool
{
    $model = new \OPNsense\OPNCore\General();
    return (string)$model->enablefiveSA == '1';
}

function fiveGNSA_enabled(): bool
{
    $model = new \OPNsense\OPNCore\General();
    return (string)$model->enablefiveNSA == '1';
}

function epc_services(): array
{
    $services = array();

    if (fourG_enabled()) {
        $services[] = array(
            'description' => gettext('Mobility Management Entity'),
            'configd' => array(
                'restart' => array('mmed restart'),
                'start' => array('mmed start'),
                'stop' => array('mmed stop'),
            ),
            'name' => 'opncore-mme',
            'pidfile' => '/var/run/epc/epcmmed.pid'
        );
        $services[] = array(
            'description' => gettext('Home Subscriber System'),
            'configd' => array(
                'restart' => array('hssd restart'),
                'start' => array('hssd start'),
                'stop' => array('hssd stop'),
            ),
            'name' => 'opncore-hss',
            'pidfile' => '/var/run/epc/epchssd.pid'
        );

        $services[] = array(
            'description' => gettext('PCRF'),
            'configd' => array(
                'restart' => array('pcrfd restart'),
                'start' => array('pcrfd start'),
                'stop' => array('pcrfd stop'),
            ),
            'name' => 'opncore-pcrf',
            'pidfile' => '/var/run/epc/epcpcrfd.pid'
        );

        $services[] = array(
            'description' => gettext('Serving Gateway User Plane Daemon'),
            'configd' => array(
                'restart' => array('sgwud restart'),
                'start' => array('sgwud start'),
                'stop' => array('sgwud stop'),
            ),
            'name' => 'opncore-sgwud',
            'pidfile' => '/var/run/epc/epcsgwud.pid'
        );
    }

    if (fiveGSA_enabled()) {
        $services[] = array(
            'description' => gettext('Authentication Server Function'),
            'configd' => array(
                'restart' => array('ausfd restart'),
                'start' => array('ausfd start'),
                'stop' => array('ausfd stop'),
            ),
            'name' => 'opncore-ausf',
            'pidfile' => '/var/run/epc/epcausfd.pid'
        );
        $services[] = array(
            'description' => gettext('Access and Mobility Function'),
            'configd' => array(
                'restart' => array('amfd restart'),
                'start' => array('amfd start'),
                'stop' => array('amfd stop'),
            ),
            'name' => 'opncore-amf',
            'pidfile' => '/var/run/epc/epcamfd.pid'
        );
        $services[] = array(
            'description' => gettext('Unified Data Management'),
            'configd' => array(
                'restart' => array('udmd restart'),
                'start' => array('udmd start'),
                'stop' => array('udmd stop'),
            ),
            'name' => 'opncore-udmd',
            'pidfile' => '/var/run/epc/epcudmd.pid'
        );

        $services[] = array(
            'description' => gettext('Session Management Function'),
            'configd' => array(
                'restart' => array('smfd restart'),
                'start' => array('smfd start'),
                'stop' => array('smfd stop'),
            ),
            'name' => 'opncore-smfd',
            'pidfile' => '/var/run/epc/epcsmfd.pid'
        );

        $services[] = array(
            'description' => gettext('Policy and Charging Function'),
            'configd' => array(
                'restart' => array('pcfd restart'),
                'start' => array('pcfd start'),
                'stop' => array('pcfd stop'),
            ),
            'name' => 'opncore-pcf',
            'pidfile' => '/var/run/epc/epcpcfd.pid'
        );

        $services[] = array(
            'description' => gettext('User Plane Function'),
            'configd' => array(
                'restart' => array('upfd restart'),
                'start' => array('upfd start'),
                'stop' => array('upfd stop'),
            ),
            'name' => 'opncore-upf',
            'pidfile' => '/var/run/epc/epcupfd.pid'
        );

        $services[] = array(
            'description' => gettext('Network Slice Selection Function'),
            'configd' => array(
                'restart' => array('nssfd restart'),
                'start' => array('nssfd start'),
                'stop' => array('nssfd stop'),
            ),
            'name' => 'opncore-nssf',
            'pidfile' => '/var/run/epc/epcnssfd.pid'
        );

        $services[] = array(
            'description' => gettext('Network Repository Function'),
            'configd' => array(
                'restart' => array('nrfd restart'),
                'start' => array('nrfd start'),
                'stop' => array('nrfd stop'),
            ),
            'name' => 'opncore-nrfd',
            'pidfile' => '/var/run/epc/epcnrfd.pid'
        );
        $services[] = array(
            'description' => gettext('Mobility Management Entity'),
            'configd' => array(
                'restart' => array('mmed restart'),
                'start' => array('mmed start'),
                'stop' => array('mmed stop'),
            ),
            'name' => 'opncore-mme',
            'pidfile' => '/var/run/epc/epcmmed.pid'
        );

        $services[] = array(
            'description' => gettext('Serving Gateway Control Plane'),
            'configd' => array(
                'restart' => array('sgwcd restart'),
                'start' => array('sgwcd start'),
                'stop' => array('sgwcd stop'),
            ),
            'name' => 'opncore-sgwc',
            'pidfile' => '/var/run/epc/epcsgwcd.pid'
        );

        $services[] = array(
            'description' => gettext('Serving Gateway User Plane'),
            'configd' => array(
                'restart' => array('sgwud restart'),
                'start' => array('sgwud start'),
                'stop' => array('sgwud stop'),
            ),
            'name' => 'opncore-sgwup',
            'pidfile' => '/var/run/epc/epcsgwud.pid'
        );
    }

    if (fiveGNSA_enabled()) {
        $services[] = array(
            'description' => gettext('Authentication Server Function'),
            'configd' => array(
                'restart' => array('ausfd restart'),
                'start' => array('ausfd start'),
                'stop' => array('ausfd stop'),
            ),
            'name' => 'opncore-ausf',
            'pidfile' => '/var/run/epc/epcausfd.pid'
        );
        $services[] = array(
            'description' => gettext('Access and Mobility Function'),
            'configd' => array(
                'restart' => array('amfd restart'),
                'start' => array('amfd start'),
                'stop' => array('amfd stop'),
            ),
            'name' => 'opncore-amf',
            'pidfile' => '/var/run/epc/epcamfd.pid'
        );
        $services[] = array(
            'description' => gettext('Unified Data Management'),
            'configd' => array(
                'restart' => array('udmd restart'),
                'start' => array('udmd start'),
                'stop' => array('udmd stop'),
            ),
            'name' => 'opncore-udmd',
            'pidfile' => '/var/run/epc/epcudmd.pid'
        );
        $services[] = array(
            'description' => gettext('Session Management Function'),
            'configd' => array(
                'restart' => array('smfd restart'),
                'start' => array('smfd start'),
                'stop' => array('smfd stop'),
            ),
            'name' => 'opncore-smfd',
            'pidfile' => '/var/run/epc/epcsmfd.pid'
        );
        $services[] = array(
            'description' => gettext('Policy and Charging Function'),
            'configd' => array(
                'restart' => array('pcfd restart'),
                'start' => array('pcfd start'),
                'stop' => array('pcfd stop'),
            ),
            'name' => 'opncore-pcf',
            'pidfile' => '/var/run/epc/epcpcfd.pid'
        );
        $services[] = array(
            'description' => gettext('User Plane Function'),
            'configd' => array(
                'restart' => array('upfd restart'),
                'start' => array('upfd start'),
                'stop' => array('upfd stop'),
            ),
            'name' => 'opncore-upf',
            'pidfile' => '/var/run/epc/epcupfd.pid'
        );
        $services[] = array(
            'description' => gettext('Network Slice Selection Function'),
            'configd' => array(
                'restart' => array('nssfd restart'),
                'start' => array('nssfd start'),
                'stop' => array('nssfd stop'),
            ),
            'name' => 'opncore-nssf',
            'pidfile' => '/var/run/epc/epcnssfd.pid'
        );
        $services[] = array(
            'description' => gettext('Network Repository Function'),
            'configd' => array(
                'restart' => array('nrfd restart'),
                'start' => array('nrfd start'),
                'stop' => array('nrfd stop'),
            ),
            'name' => 'opncore-nrfd',
            'pidfile' => '/var/run/epc/epcnrfd.pid'
        );
        $services[] = array(
            'description' => gettext('Mobility Management Entity'),
            'configd' => array(
                'restart' => array('mmed restart'),
                'start' => array('mmed start'),
                'stop' => array('mmed stop'),
            ),
            'name' => 'opncore-mme',
            'pidfile' => '/var/run/epc/epcmmed.pid'
        );

        $services[] = array(
            'description' => gettext('Serving Gateway Control Plane'),
            'configd' => array(
                'restart' => array('sgwcd restart'),
                'start' => array('sgwcd start'),
                'stop' => array('sgwcd stop'),
            ),
            'name' => 'opncore-sgwc',
            'pidfile' => '/var/run/epc/epcsgwcd.pid'
        );

        $services[] = array(
            'description' => gettext('Serving Gateway User Plane'),
            'configd' => array(
                'restart' => array('sgwud restart'),
                'start' => array('sgwud start'),
                'stop' => array('sgwud stop'),
            ),
            'name' => 'opncore-sgwup',
            'pidfile' => '/var/run/epc/epcsgwud.pid'
        );
    }

    return $services;
}
