## What is OPNcell
  OPNcell is a native plugin for [OPNsense](https://opnsense.org/) that adds standalone 4G LTE or 5G NR core signalling network capabilities.
  The plugin offers 4G or 5G SA (Stand Alone) interoperability, NSA (Non Stand Alone supporting both 4G gNB and 5G gNB radios) as well as UPF (PGW) deployment (where strategicaly necessary) services to OPNsense using open5gs's 3GPP Release 17 open source [Open5Gs](https://open5gs.org/open5gs/docs/) core software. By
  combining advanced deep packet filtering &amp; management with 4G/5G capability, OPNcell offers a complete FOSS solution for Enterprise, Government, Community and Private Cellular network deployments.  The entire code base is feeely available for audit with a certified compliant distribution as an available option.

## What is Open5Gs
 
[Open5Gs](href="https://open5gs.org/open5gs/docs) is a C-language Open Source implementation of 5GC and EPC, i.e. the core network of NR/LTE network. Open5GS natively supports 4G/5G Standalone mode as well as non-standalone (supporting both 4G and 5G).
## 4G/5G NSA
The Open5GS 4G/ 5G NSA Core contains the following components:<br>
* MME - Mobility Management Entity
* HSS - Home Subscriber Server
* PCRF - Policy and Charging Rules Function
* SGWC - Serving Gateway Control Plane<br>
* SGWU - Serving Gateway User Plane<br>
* PGWC/SMF - Packet Gateway Control Plane / (component contained in Open5GS SMF)<br>
* PGWU/UPF - Packet Gateway User Plane / (component contained in Open5GS UPF) <br>

All of these Open5GS components have configuration files. Each file contains the component’s IP bind addresses/ local Interface names and the IP addresses/ DNS names of the other components it needs to connect to.
## 5G SA Core
The Open5GS 5G SA Core contains the following functions: <br>
* NRF - NF Repository Function 
* SCP - Service Communication Proxy
* SEPP - Security Edge Protection Proxy
* AMF - Access and Mobility Management Function
* SMF - Session Management Function
* UPF - User Plane Function
* AUSF - Authentication Server Function
* UDM - Unified Data Management
* UDR - Unified Data Repository
* PCF - Policy and Charging Function
* NSSF - Network Slice Selection Function
* BSF - Binding Support Function <br>

With the exception of the SMF and UPF, all configuration files for the 5G SA core functions only contain the function’s IP bind addresses/ local Interface names and the IP address/ DNS name of the NRF.
> [!TIP]
> TL;DR.
> A more in depth run through of roles of each function within a core can be found [here](docs.md)

## What is OPNsense

[OPNsense](https://opnsense.org/) is a mature popular open source, FreeBSD-based firewall, intrusion-detection, routing & packet filtering system.<br>
OPNsense offers a variety of pros which compelled the decision to build OPNcell behind the firewall. These include;<br>
* It is free to use with no licensing fees, reducing overall cost for network set up.
* Intuitive and easy-to-use web-based interface which simplifies management and configuration.
* The firewall is highly configurable with a wide range of plugins to tailor it to specific needs.
* Built-in VPN support (IPsec, OpenVPN) for secure remote access.
* Features such as failover and load balancing ensure continuous network availability and performance.

## Installing OPNcell

Run the below command in the console of the machine running the OPNsense firewall.<br><br>
`fetch -o /usr/local/etc/pkg/repos/OPNcell.conf http://repo.opncell.io/cellular.conf && pkg update` <br><br>
This establishes the repository holding the cellular package installer, including other necessary pieces of the service.

## Getting into it

Once you have the repo set up on your host instance, you can proceed to install the package by simply running<br><br> `pkg install os-cellular-devel` <br>

All Open5GS services are set to communicate with each other using the local loopback address space (127.0.0.X). This allows a user to have all services necessary to set up any given network core on a single computer without the need to have multiple computers to accommodate all the different components.The default addresses for each of the bind interfaces for these components and functions are as follows:

* MongoDB   = 127.0.0.1 (subscriber database) - http://localhost:9999
* MME-s1ap  = 127.0.0.2 :36412 for S1-MME
* MME-gtpc  = 127.0.0.2 :2123 for S11
* MME-frDi  = 127.0.0.2 :3868 for S6a
* SGWC-gtpc = 127.0.0.3 :2123 for S11
* SGWC-pfcp = 127.0.0.3 :8805 for Sxa
* SMF-gtpc  = 127.0.0.4 :2123 for S5c
* SMF-gtpu  = 127.0.0.4 :2152 for N4u (Sxu)
* SMF-pfcp  = 127.0.0.4 :8805 for N4 (Sxb)
* SMF-frDi  = 127.0.0.4 :3868 for Gx auth
* SMF-sbi   = 127.0.0.4 :7777 for 5G SBI (N7,N10,N11)
* AMF-ngap  = 127.0.0.5 :38412 for N2
* AMF-sbi   = 127.0.0.5 :7777 for 5G SBI (N8,N12,N11)
* SGWU-pfcp = 127.0.0.6 :8805 for Sxa
* SGWU-gtpu = 127.0.0.6 :2152 for S1-U, S5u <br>
  
A full list of all the services with their loopback addresses is [here](docs.md)<br>

In the GUI, set up the loop back addresses for each of the open5gs services.<br>
Add the virtual addresses under; <br>

'Interfaces > Virtual IPs > settings'

<img width="852" alt="loopback addresses" src="https://github.com/opncell/opncell/assets/170442159/c941bc65-91df-49f0-8e76-f73c22523605">

In the OPNsense, SCTP traffic is blocked by default, therefore add a floating rule to explicitly allow it to pass.
Add the rule under; <br>

'Firewall > Rules > Floating'

<img width="1680" alt="floating_rule" src="https://github.com/opncell/opncell/assets/170442159/bebc03e3-e7c5-436d-9c23-0e8d6e571b73">

## OPNcell functionality.
## Register Subscriber Information.

To add subscriber information, first you need to create a profile.A profile consists of APN, QoS values as well as AMBR-speed details. <br>
When a profile is linked to an IMSI during subscriber addition, the profile details are automatically associated with that IMSI and saved in the database.<br>

<img width="902" alt="add_profile" src="https://github.com/opncell/opncell/assets/170442159/b04f61ab-c004-4b10-943d-11ecd1442b7d">

When a profile is linked to an IMSI during subscriber addition, the profile details are automatically associated with that IMSI and saved in the database. <br>

Therefore, to add subscriber information, you can do that in the following order: <br>
1. Navigate to Users Menu.
2. Navigate to Profile List tab
3. Click + Button to add a new profile
4. Navigate to Subscriber List tab
5. Click + Button to add a new Subscriber
6. Fill the IMSI, security context(K, OPc), and attach a profile to that subscriber.
7. Click SAVE Button
utton.

## Bulk insertion

OPNcell offers the option of adding multiple user at a go through the bulk insertion functionality. Both .csv and .inc file formats are accepted. It should follow the below template.<br>

[//]: # (<img width="1329" alt="template" src="https://github.com/opncell/opncell/assets/170442159/2f6a1b00-db09-45c6-9bb5-3287cc3a4147">)

| imsi, | ki,  | opc, |
| --- | --- | --- |
| 9997080930195106, | EF84CE78D9C47D64A6765B87972119F7, | 4723E4872557013C4F39A1D8E4D59CE4 |

1. To add multiple subscribers at a go, you can do that in the following order: <br>
2. Go to Users Menu.
3. Go to Bulk Insertion tab
4. Choose and upload the file. If successfully uploaded, Attach a profile(s)
5. Click SAVE Button.

## Logging

All log files in OPNcell for the different services can be found under the Diagnostics sub menu.

All the logs are viewable under; <br>

'Cellular > Diagnostics'

Log files are located in /var/log/opncell and can be easily tailed "tail -fn 200 /var/log/opncell/XXXXX.log"

## Uninstalling OPNcell.

To uninstall the package, run "pkg remove os-cellular-devel" in the console.

## Sponsors

If you find OPNcell useful please consider supporting this Open Source project by becoming a sponsor.

## Documentation

More in depth documentation is available [Here.](docs.md)



