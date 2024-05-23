<?php

/*
 * Copyright (C) 2023 Deciso B.V.
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

namespace OPNsense\OpenVPN;

use Phalcon\Messages\Message;
use OPNsense\Base\BaseModel;
use OPNsense\Trust\Store;
use OPNsense\Core\Config;
use OPNsense\Firewall\Util;

/**
 * Class OpenVPN
 * @package OPNsense\OpenVPN
 */
class OpenVPN extends BaseModel
{
    /**
     * {@inheritdoc}
     */
    public function performValidation($validateFullModel = false)
    {
        $messages = parent::performValidation($validateFullModel);
        $instances = [];
        foreach ($this->getFlatNodes() as $key => $node) {
            if ($validateFullModel || $node->isFieldChanged()) {
                $tagName = $node->getInternalXMLTagName();
                $parentNode = $node->getParentNode();
                $parentKey = $parentNode->__reference;
                $parentTagName = $parentNode->getInternalXMLTagName();
                if ($parentTagName === 'Instance') {
                    $instances[$parentKey] = $parentNode;
                }
            }
        }

        // validate changed instances
        foreach ($instances as $key => $instance) {
            if ($instance->role == 'client') {
                if (empty((string)$instance->remote)) {
                    $messages->appendMessage(new Message(gettext("Remote required"), $key . ".remote"));
                }
                if (empty((string)$instance->username) xor empty((string)$instance->password)) {
                    $messages->appendMessage(
                        new Message(
                            gettext("When ussing password authentication, both username and password are required"),
                            $key . ".username"
                        )
                    );
                }
            }
            if (!empty((string)$instance->cert)) {
                if ($instance->cert->isFieldChanged() || $validateFullModel) {
                    $tmp = Store::getCertificate((string)$instance->cert);
                    if (empty($tmp) || !isset($tmp['ca'])) {
                        $messages->appendMessage(new Message(
                            gettext("Unable to locate a Certificate Authority for this certificate"),
                            $key . ".cert"
                        ));
                    }
                }
            } else {
                if (
                    $instance->cert->isFieldChanged() ||
                    $instance->verify_client_cert->isFieldChanged() ||
                    $validateFullModel
                ) {
                    if ((string)$instance->verify_client_cert != 'none') {
                        $messages->appendMessage(new Message(
                            gettext("To validate a certificate, one has to be provided "),
                            $key . ".verify_client_cert"
                        ));
                    }
                }
            }
            if (
                (
                $instance->keepalive_interval->isFieldChanged() ||
                $instance->keepalive_timeout->isFieldChanged() ||
                $validateFullModel
                ) && (int)(string)$instance->keepalive_timeout < (int)(string)$instance->keepalive_interval
            ) {
                $messages->appendMessage(new Message(
                    gettext("Timeout should be larger than interval"),
                    $key . ".keepalive_timeout"
                ));
            }
        }
        return $messages;
    }

    /**
     * Retrieve overwrite content in legacy format
     * @param string $server_id vpnid
     * @param string $common_name certificate common name (or username when specified)
     * @return array legacy overwrite data
     */
    public function getOverwrite($server_id, $common_name)
    {
        $result = [];
        foreach ($this->Overwrites->Overwrite->iterateItems() as $cso) {
            if (empty((string)$cso->enabled)) {
                continue;
            }
            $servers = !empty((string)$cso->servers) ? explode(',', (string)$cso->servers) : [];
            if (!empty($servers) && !in_array($server_id, $servers)) {
                continue;
            }
            if ((string)$cso->common_name != $common_name) {
                continue;
            }
            // translate content to legacy format so this may easily inject into the existing codebase
            $result['ovpn_servers'] = (string)$cso->servers;
            $result['common_name'] = (string)$cso->common_name;
            $result['description'] = (string)$cso->description;
            $result['redirect_gateway'] = (string)$cso->redirect_gateway;

            $result['tunnel_network'] = (string)$cso->tunnel_network;
            $result['tunnel_networkv6'] = (string)$cso->tunnel_networkv6;
            foreach (['local', 'remote'] as $type) {
                $f1 = $type . '_network';
                $f2 = $type . '_networkv6';
                foreach (explode(',', (string)$cso->{$type . '_networks'}) as $item) {
                    if (strpos($item, ":") === false) {
                        $target_fieldname = $f1;
                    } else {
                        $target_fieldname = $f2;
                    }
                    if (!isset($result[$target_fieldname])) {
                        $result[$target_fieldname] = $item;
                    } else {
                        $result[$target_fieldname] .=  "," . $item;
                    }
                }
            }
            if (!empty((string)$cso->push_reset)) {
                $result['push_reset'] = '1';
            }
            if (!empty((string)$cso->block)) {
                $result['block'] = '1';
            }
            $result['dns_domain'] = (string)$cso->dns_domain;
            $result['dns_domain_search'] = (string)$cso->dns_domain_search;
            foreach (['dns_server', 'ntp_server', 'wins_server'] as $fieldname) {
                if (!empty((string)$cso->$fieldname . 's')) {
                    foreach (explode(',', (string)$cso->{$fieldname . 's'}) as $idx => $item) {
                        $result[$fieldname . (string)($idx + 1)] = $item;
                    }
                }
            }
        }
        return $result;
    }

    /**
     * The VPNid sequence is used for device creation, in which case we can't use uuid's due to their size
     * @return list of vpn id's used by legacy or mvc instances
     */
    public function usedVPNIds()
    {
        $result = [];
        $cfg = Config::getInstance()->object();
        foreach (['openvpn-server', 'openvpn-client'] as $ref) {
            if (isset($cfg->openvpn) && isset($cfg->openvpn->$ref)) {
                foreach ($cfg->openvpn->$ref as $item) {
                    if (isset($item->vpnid)) {
                        $result[] = (string)$item->vpnid;
                    }
                }
            }
        }
        foreach ($this->Instances->Instance->iterateItems() as $node_uuid => $node) {
            if ((string)$node->vpnid != '') {
                $result[$node_uuid] = (string)$node->vpnid;
            }
        }
        return $result;
    }

    /**
     * @return bool true when there is any enabled tunnel (legacy and/or mvc)
     */
    public function isEnabled()
    {
        $cfg = Config::getInstance()->object();
        foreach (['openvpn-server', 'openvpn-client'] as $ref) {
            if (isset($cfg->openvpn) && isset($cfg->openvpn->$ref)) {
                foreach ($cfg->openvpn->$ref as $item) {
                    if (empty((string)$item->disable)) {
                        return true;
                    }
                }
            }
        }
        foreach ($this->Instances->Instance->iterateItems() as $node_uuid => $node) {
            if (!empty((string)$node->enabled)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Find unique instance properties, either from legacy or mvc model
     * Offers glue between both worlds.
     * @param string $server_id vpnid (either numerical or uuid)
     * @param string $role the node role
     * @return array selection of relevant fields for downstream processes
     */
    public function getInstanceById($server_id, $role = null)
    {
        // travers model first, two key types are valid, the id used in the device (numeric) or the uuid
        foreach ($this->Instances->Instance->iterateItems() as $node_uuid => $node) {
            if (
                !empty((string)$node->enabled) &&
                ((string)$node->vpnid == $server_id || $server_id == $node_uuid) &&
                ($role == null || $role == (string)$node->role)
            ) {
                // find static key
                $this_tls = null;
                $this_mode = null;
                if (!empty((string)$node->tls_key)) {
                    $tlsnode = $this->getNodeByReference("StaticKeys.StaticKey.{$node->tls_key}");
                    if (!empty($node->tls_key)) {
                        $this_mode = (string)$tlsnode->mode;
                        $this_tls = base64_encode((string)$tlsnode->key);
                    }
                }
                // find caref
                $this_caref = null;
                if (isset(Config::getInstance()->object()->cert)) {
                    foreach (Config::getInstance()->object()->cert as $cert) {
                        if (isset($cert->refid) && (string)$node->cert == $cert->refid) {
                            $this_caref = (string)$cert->caref;
                        }
                    }
                }
                return [
                    'role' => (string)$node->role,
                    'vpnid' => $server_id,
                    'authmode' => (string)$node->authmode,
                    'local_group' => (string)$node->local_group,
                    'strictusercn' => (string)$node->strictusercn,
                    'dev_mode' => (string)$node->dev_type,
                    'topology_subnet' => $node->topology == 'subnet' ? '1' : '0',
                    'local_port' =>  (string)$node->port,
                    'protocol' => (string)$node->proto,
                    'mode' => !empty((string)$node->authmode) ? 'server_tls_user' : '',
                    'reneg-sec' => (string)$node->{'reneg-sec'},
                    'tls' => $this_tls,
                    'tlsmode' => $this_mode,
                    'certref' => (string)$node->cert,
                    'caref' => $this_caref,
                    'cert_depth' => (string)$node->cert_depth,
                    'description' => (string)$node->description
                ];
            }
        }
        // when not found, try to locate the server in our legacy pool
        $cfg = Config::getInstance()->object();
        foreach (['openvpn-server', 'openvpn-client'] as $section) {
            if (!isset($cfg->openvpn) || !isset($cfg->openvpn->$section)) {
                continue;
            }
            foreach ($cfg->openvpn->$section as $item) {
                $this_role =  explode('-', $section)[1];
                // XXX: previous legacy code did not check if the instance is enabled, we might want to revise that
                if (
                    isset($item->vpnid) &&
                    $item->vpnid == $server_id &&
                    ($role == null || $role == $this_role)
                ) {
                    return [
                        'role' => $this_role,
                        'vpnid' => (string)$item->vpnid,
                        'authmode' => (string)$item->authmode,
                        'local_group' => (string)$item->local_group,
                        'cso_login_matching' => (string)$item->username_as_common_name,
                        'strictusercn' => (string)$item->strictusercn,
                        'dev_mode' => (string)$item->dev_mode,
                        'topology_subnet' => (string)$item->topology_subnet,
                        'local_port' =>  (string)$item->local_port,
                        'protocol' => (string)$item->protocol,
                        'mode' => (string)$item->local_port,
                        'reneg-sec' => (string)$item->{'reneg-sec'},
                        'tls' => (string)$item->tls,
                        'tlsmode' => (string)$item->tlsmode,
                        'certref' => (string)$item->certref,
                        'caref'  => (string)$item->caref,
                        'cert_depth' => (string)$item->cert_depth,
                        'description' => (string)$item->description,
                        // legacy only (backwards compatibility)
                        'compression' => (string)$item->compression,
                        'crypto' => (string)$item->crypto,
                        'digest' => (string)$item->digest,
                        'interface' => (string)$item->interface,
                    ];
                }
            }
        }
        return null;
    }

    /**
     * Convert options into a openvpn config file on disk
     * @param string $filename target filename
     * @return null
     */
    private function writeConfig($filename, $options)
    {
        $output = '';
        foreach ($options as $key => $value) {
            if ($value === null) {
                $output .= $key . "\n";
            } elseif (str_starts_with($key, '<')) {
                $output .= $key . "\n";
                $output .= trim($value) . "\n";
                $output .= "</" . substr($key, 1) . "\n";
            } elseif (is_array($value)) {
                if ($key == 'auth-user-pass') {
                    // user/passwords need to be feed using a file
                    $output .= $key . " " . $value['filename'] . "\n";
                    @touch($value['filename']);
                    @chmod($value['filename'], 0600);
                    file_put_contents($value['filename'], $value['content']);
                } else {
                    foreach ($value as $item) {
                        $output .= $key . " " . $item . "\n";
                    }
                }
            } else {
                $output .= $key . " " . $value . "\n";
            }
        }
        @touch($filename);
        @chmod($filename, 0600);
        file_put_contents($filename, $output);
    }

    /**
     * generate OpenVPN instance config files.
     * Ideally we would like to use our standard template system, but due to the complexity of the output
     * and the need for multiple files and a cleanup, this would add more unwanted complexity.
     */
    public function generateInstanceConfig($uuid = null)
    {
        foreach ($this->Instances->Instance->iterateItems() as $node_uuid => $node) {
            if (!empty((string)$node->enabled) && ($uuid == null || $node_uuid == $uuid)) {
                $options = ['push' => [], 'route' => [], 'route-ipv6' => []];
                // mode specific settings
                if ($node->role == 'client') {
                    $options['client'] = null;
                    $options['dev'] = "ovpnc{$node->vpnid}";
                    $options['remote'] = [];
                    foreach (explode(',', (string)$node->remote) as $this_remote) {
                        $parts = [];
                        if (substr_count($this_remote, ':') > 1) {
                            foreach (explode(']', $this_remote) as $part) {
                                $parts[] = ltrim($part, '[:');
                            }
                        } else {
                            $parts = explode(':', $this_remote);
                        }
                        $options['remote'][] = implode(' ', $parts);
                    }
                    if (empty((string)$node->port) && empty((string)$node->local)) {
                        $options['nobind'] = null;
                    }
                    if (!empty((string)$node->username) && !empty((string)$node->password)) {
                        $options['auth-user-pass'] = [
                            "filename" => "/var/etc/openvpn/instance-{$node_uuid}.up",
                            "content" => "{$node->username}\n{$node->password}\n"
                        ];
                    }
                    // XXX: In some cases it might be practical to drop privileges, for server mode this will be
                    //      more difficult due to the associated script actions (and their requirements).
                    //$options['user'] = 'openvpn';
                    //$options['group'] = 'openvpn';
                } else {
                    $event_script = '/usr/local/opnsense/scripts/openvpn/ovpn_event.py';
                    $options['dev'] = "ovpns{$node->vpnid}";
                    $options['ping-timer-rem'] = null;
                    $options['topology'] = (string)$node->topology;
                    $options['dh'] = '/usr/local/etc/inc/plugins.inc.d/openvpn/dh.rfc7919';
                    if (!empty((string)$node->crl) && !empty((string)$node->cert)) {
                        // updated via plugins_configure('crl');
                        $options['crl-verify'] = "/var/etc/openvpn/server-{$node_uuid}.crl-verify";
                    }
                    if (!empty((string)$node->server)) {
                        $parts = explode('/', (string)$node->server);
                        $options['server'] = $parts[0] . " " . Util::CIDRToMask($parts[1]);
                    }
                    if (!empty((string)$node->server_ipv6)) {
                        $options['server-ipv6'] = (string)$node->server_ipv6;
                    }
                    if (!empty((string)$node->username_as_common_name)) {
                        $options['username-as-common-name'] = null;
                    }
                    // server only setttings
                    if (!empty((string)$node->server) || !empty((string)$node->server_ipv6)) {
                        $options['client-config-dir'] = "/var/etc/openvpn-csc/{$node->vpnid}";
                        // hook event handlers
                        if (!empty((string)$node->authmode)) {
                            $options['auth-user-pass-verify'] = "\"{$event_script} --defer '{$node->vpnid}'\" via-env";
                            $options['learn-address'] =  "\"{$event_script} '{$node->vpnid}'\"";
                        } else {
                            // client specific profiles are being deployed using the connect event when no auth is used
                            $options['client-connect'] = "\"{$event_script} '{$node->vpnid}'\"";
                        }
                        $options['client-disconnect'] = "\"{$event_script} '{$node->vpnid}'\"";
                        $options['tls-verify'] = "\"{$event_script} '{$node->vpnid}'\"";
                    }

                    if (!empty((string)$node->maxclients)) {
                        $options['max-clients'] = (string)$node->maxclients;
                    }
                    if (empty((string)$node->local) && str_starts_with((string)$node->proto, 'udp')) {
                        // assume multihome when no bind address is specified for udp
                        $options['multihome'] = null;
                    }

                    // push options
                    if (!empty((string)$node->redirect_gateway)) {
                        $options['push'][] = "\"redirect-gateway {$node->redirect_gateway}\"";
                    }
                    if (!empty((string)$node->register_dns)) {
                        $options['push'][] = "\"register-dns\"";
                    }
                    if (!empty((string)$node->dns_domain)) {
                        $options['push'][] = "\"dhcp-option DOMAIN {$node->dns_domain}\"";
                    }
                    if (!empty((string)$node->dns_domain_search)) {
                        foreach (explode(',', (string)$node->dns_domain_search) as $opt) {
                            $options['push'][] = "\"dhcp-option DOMAIN-SEARCH {$opt}\"";
                        }
                    }
                    if (!empty((string)$node->dns_servers)) {
                        foreach (explode(',', (string)$node->dns_servers) as $opt) {
                            $options['push'][] = "\"dhcp-option DNS {$opt}\"";
                        }
                    }
                    if (!empty((string)$node->ntp_servers)) {
                        foreach (explode(',', (string)$node->ntp_servers) as $opt) {
                            $options['push'][] = "\"dhcp-option NTP {$opt}\"";
                        }
                    }
                }
                $options['persist-tun'] = null;
                $options['persist-key'] = null;
                if (!empty((string)$node->keepalive_interval) && !empty((string)$node->keepalive_timeout)) {
                    $options['keepalive'] = "{$node->keepalive_interval} {$node->keepalive_timeout}";
                }

                $options['dev-type'] = (string)$node->dev_type;
                $options['dev-node'] = "/dev/{$node->dev_type}{$node->vpnid}";
                $options['script-security'] = '3';
                $options['writepid'] = $node->pidFilename;
                $options['daemon'] = "openvpn_{$node->role}{$node->vpnid}";
                $options['management'] = "{$node->sockFilename} unix";
                $options['proto'] = (string)$node->proto;
                $options['verb'] = (string)$node->verb;
                $options['verify-client-cert'] = (string)$node->verify_client_cert;

                foreach (
                    [
                    'reneg-sec', 'auth-gen-token', 'port', 'local', 'data-ciphers', 'data-ciphers-fallback', 'auth'
                    ] as $opt
                ) {
                    if ((string)$node->$opt != '') {
                        $options[$opt] = str_replace(',', ':', (string)$node->$opt);
                    }
                }
                if (!empty((string)$node->various_flags)) {
                    foreach (explode(',', (string)$node->various_flags) as $opt) {
                        $options[$opt] = null;
                    }
                }

                // routes (ipv4, ipv6 local or push)
                foreach (['route', 'push_route'] as $type) {
                    foreach (explode(',', (string)$node->$type) as $item) {
                        if (empty($item)) {
                            continue;
                        } elseif (strpos($item, ":") === false) {
                            $parts = explode('/', (string)$item);
                            $item = $parts[0] . " " . Util::CIDRToMask($parts[1] ?? '32');
                            $target_fieldname = "route";
                        } else {
                            $target_fieldname = "route-ipv6";
                        }
                        if ($type == 'push_route') {
                            $options['push'][] = "\"{$target_fieldname} $item\"";
                        } else {
                            $options[$target_fieldname][] = $item;
                        }
                    }
                }

                if (!empty((string)$node->tls_key)) {
                    $tlsnode = $this->getNodeByReference("StaticKeys.StaticKey.{$node->tls_key}");
                    if ($tlsnode) {
                        $options["<tls-{$tlsnode->mode}>"] = (string)$tlsnode->key;
                        if ($tlsnode->mode == 'auth') {
                            $options['key-direction'] = $node->role == 'server' ? '0' : '1';
                        }
                    }
                }

                if (!empty((string)$node->cert)) {
                    $tmp = Store::getCertificate((string)$node->cert);
                    if ($tmp && isset($tmp['prv'])) {
                        $options['<key>'] = $tmp['prv'];
                        $options['<cert>'] = $tmp['crt'];
                        if (isset($tmp['ca'])) {
                            $options['<ca>'] = $tmp['ca']['crt'];
                        }
                    }
                }
                // dump to file
                $this->writeConfig($node->cnfFilename, $options);
            }
        }
    }
}
