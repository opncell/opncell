## Table of Content

[1\. Introduction to OPNcell](#introduction-to-opncell)

[1.1 Open5GS ](#11-open5gs)

[1.1.1 4G/ 5G NSA Core ](#111-4g-5g-nsa-core)

[1.1.2 5G SA Core ](#112-5g-sa-core)

[1.2 OPNsense ](#12-opnsense)

[1.3 OPNcell ](#13-opncell)

[2\. Installing OPNcell ](#2-installing-opncell)

[3\. Next Steps ](#3-next-steps)

[4\. Register Subscriber Information ](#register-subscriber-information)

[5\. Logging ](#logging)

[6\. Uninstalling OPNcell ](#uninstalling-opncell)

## Introduction to OPNcell

Before we get started, we’ll spend a moment to understand the basic architecture of the pieces of software OPNcell leverages: [Open5gs](https://open5gs.org/open5gs/docs/) and [OPNsense](https://opnsense.org/).

## 1.1 Open5GS

Open5GS is a series of software components and network functions that implement the 4G/5G non-standalone (NSA) and 5G standalone (SA) core functions.

The main components of the 4G/5G NSA architecture are:

- User Equipment (UE): The mobile device used by the end user.
- Evolved NodeB (eNB): The base station that connects the UE to the core network
- Evolved Packet Core (EPC): The core network in the 4G/5G NS architecture, which has several services like SGW, PGW, MME, etc.

## 1.1.1 4G/ 5G NSA Core

The Open5GS 4G/ 5G NSA Core contains the following components:

- MME - Mobility Management Entity
- HSS - Home Subscriber Server
- PCRF - Policy and Charging Rules Function
- SGWC - Serving Gateway Control Plane
- SGWU - Serving Gateway User Plane
- PGWC/SMF - Packet Gateway Control Plane / (component contained in Open5GS SMF)
- PGWU/UPF - Packet Gateway User Plane / (component contained in Open5GS UPF)

The core has two main planes: the control plane and the user plane.

The MME is the main **control plane** hub of the core. It primarily manages sessions, mobility, paging and bearers. A bearer typically provides a logical channel between the UE and the PDN (Public Data Network) for transporting IP traffic.

It links to the HSS, which generates SIM authentication vectors and holds the subscriber profile and to the SGWC and PGWC/SMF, which are the control planes of the gateway servers.

All the eNB in the mobile network (4G base stations) connect to the MME. The final element of the control plane is the PCRF, which sits in-between the PGWC/SMF and the HSS, and handles charging and enforces subscriber policies.

The **user plane** carries user data packets between the eNB/gNB (5G NSA base stations) and the external WAN. The two user plane core components are the SGWU and PGWU/UPF. Each of these connect back to their control plane counterparts. eNBs/gNBs connect to the SGWU, which connects to the PGWU/UPF, and on to the WAN. By having the control and user planes physically separated like this, it means you can deploy multiple user plane servers in the field (e.g. somewhere with a high speed Internet connection), whilst keeping control functionality centralized. This enables support of MEC use cases.

All of these Open5GS components have configuration files. Each file contains the component’s IP bind addresses/ local Interface names **and** the IP addresses/ DNS names of the other components it needs to connect to.

## 1.1.2 5G SA Core

The main components of the 4G/5G NSA architecture are:

- User Equipment (UE): The mobile device used by the end user, enhanced to support 5g speeds and features.
- gNodeB (gNB): The equivalent of eNB in 5G.
- 5G Core (5GC): The core network in the 5G SA architecture, which has several services like AMF , UDM , NRF , etc.

The Open5GS 5G SA Core contains the following functions:

- NRF - NF Repository Function
- SCP - Service Communication Proxy
- SEPP - Security Edge Protection Proxy
- AMF - Access and Mobility Management Function
- SMF - Session Management Function
- UPF - User Plane Function
- AUSF - Authentication Server Function
- UDM - Unified Data Management
- UDR - Unified Data Repository
- PCF - Policy and Charging Function
- NSSF - Network Slice Selection Function
- BSF - Binding Support Function

The 5G SA core **user plane** is much simpler, as it only contains a single function. The UPF carries user data packets between the gNB and the WAN and it connects back to the SMF. The 5G SA core works in a different way to the 4G core - it uses a **Service Based Architecture** (SBA). **Control plane** functions are configured to register with the NRF, and the NRF then helps them discover the other core functions.

Brief run through of the other functions:

The AMF handles connection and mobility management ( a subset of what the 4G MME is tasked with) , gNBs connect to the AMF.

The UDM, AUSF and UDR carry out similar operations as the 4G HSS, generating SIM authentication vectors and holding the subscriber profile.

SMF handles session management (previously the responsibility of the 4G MME/ SGWC/ PGWC).

The NSSF provides a way to select the network slice, and PCF is used for charging and enforcing subscriber policies, and SEPP is part of the roaming security architecture. Finally, there is the SCP that enable indirect communication.

The 5G SA core user plane is much simpler, as it only contains a single function. The UPF carries user data packets between the gNB and the external WAN. It connects back to the SMF too.

Except the SMF and UPF, all configuration files for the 5G SA core functions only contain the function’s IP bind addresses/ local Interface names and the IP address/ DNS name of the NRF.

## 1.2 OPNsense

[OPNsense](https://opnsense.org/) is a mature open source, Free-BSD-based firewall, intrusion-detection, routing and web-filtering system. OPNsense offers a variety of pros which compelled the decision to build OPNcell behind the firewall. These include;

1. It is free to use with no licensing fees, reducing overall cost for network set up.
2. Intuitive and easy-to-use web-based interface which simplifies management and configuration.
3. The firewall is highly configurable with a wide range of plugins to tailor it to specific needs.
4. Built-in VPN support (IPsec, OpenVPN) for secure remote access.
5. Features such as failover and load balancing ensure continuous network availability and performance.

## 1.3 OPNcell  
OPNcell is an out-of-box OPNsense plugin that adds Private 5G & LTE network capability.  
The package adds 5G/LTE services to OPNsense using the Open Source Open5Gs software.  
By combining advanced packet filtering & management with 4G/5G capability, OPNcell offers a low-cost complete solution for private LTE deployments.

## 2\. Installing OPNcell

Run the below command in the console of the machine running the OPNsense firewall.

**_fetch -o /usr/local/etc/pkg/repos/opncell.conf <http://repo.opncell.io/cellular.conf> && pkg update_**

This establishes the repository holding the cellular package installer, including other necessary pieces of the service.

Once the repo is in place, then run \`**_pkg install os-cellular-devel_**\`.

## 3\. Next Steps

In the OPNsense, SCTP traffic is blocked by default, therefore add a floating rule to explicitly allow it to pass.

To do this, go to opnsense GUI, under the **Firewall** sub menu > **Rules** > **Floating**

<img width="1680" alt="floating_rule" src="https://github.com/opncell/opncell/assets/170442159/bebc03e3-e7c5-436d-9c23-0e8d6e571b73">
Figure 1 Floating Rule

All Open5GS components are set to communicate with each other using the local

loopback address space (127.0.0.X). This allows a user to have all services necessary to set up any given network core on a single computer without the need to have multiple computers to accommodate all the different components.The default addresses for each of the bind interfaces for these components and functions are as follows:

MongoDB = 127.0.0.1 (subscriber database) - <http://localhost:9999>

MME-s1ap = 127.0.0.2 :36412 for S1-MME

MME-gtpc = 127.0.0.2 :2123 for S11

MME-frDi = 127.0.0.2 :3868 for S6a

SGWC-gtpc = 127.0.0.3 :2123 for S11

SGWC-pfcp = 127.0.0.3 :8805 for Sxa

SMF-gtpc = 127.0.0.4 :2123 for S5c

SMF-gtpu = 127.0.0.4 :2152 for N4u (Sxu)

SMF-pfcp = 127.0.0.4 :8805 for N4 (Sxb)

SMF-frDi = 127.0.0.4 :3868 for Gx auth

SMF-sbi = 127.0.0.4 :7777 for 5G SBI (N7,N10,N11)

AMF-ngap = 127.0.0.5 :38412 for N2

AMF-sbi = 127.0.0.5 :7777 for 5G SBI (N8,N12,N11)

SGWU-pfcp = 127.0.0.6 :8805 for Sxa

SGWU-gtpu = 127.0.0.6 :2152 for S1-U, S5u

UPF-pfcp = 127.0.0.7 :8805 for N4 (Sxb)

UPF-gtpu = 127.0.0.7 :2152 for S5u, N3, N4u (Sxu)

HSS-frDi = 127.0.0.8 :3868 for S6a, Cx

PCRF-frDi = 127.0.0.9 :3868 for Gx

NRF-sbi = 127.0.0.10:7777 for 5G SBI

SCP-sbi = 127.0.0.200:7777 for 5G SBI

SEPP-sbi = 127.0.0.250:7777 for 5G SBI

SEPP-n32 = 127.0.0.251:7777 for 5G N32

SEPP-n32f = 127.0.0.252:7777 for 5G N32-f

AUSF-sbi = 127.0.0.11:7777 for 5G SBI

UDM-sbi = 127.0.0.12:7777 for 5G SBI

PCF-sbi = 127.0.0.13:7777 for 5G SBI

NSSF-sbi = 127.0.0.14:7777 for 5G SBI

BSF-sbi = 127.0.0.15:7777 for 5G SBI

UDR-sbi = 127.0.0.20:7777 for 5G SBI

Add these Virtual IPs to the Lo0 interface.

In the GUI, go to the **Interfaces** sub menu > **Virtual IPs** \> **Settings**

<img width="852" alt="loopback addresses" src="https://github.com/opncell/opncell/assets/170442159/c941bc65-91df-49f0-8e76-f73c22523605">

Figure 2 Add Virtual IP

## Register Subscriber Information

To add subscriber information, first you need to create a profile. APN, QoS as well as AMBR-speed details all consist of a profile.

<img width="902" alt="add_profile" src="https://github.com/opncell/opncell/assets/170442159/b04f61ab-c004-4b10-943d-11ecd1442b7d">

Figure 3 Add Profile

When a profile is linked to an IMSI during subscriber addition, the profile details are automatically associated with that IMSI and saved in the database.

Therefore, to add subscriber information, you can do that in the following order:

Navigate to **Users** Menu.

Navigate to **Profile List** tab

Click **+** Button to add a new profile

Navigate to **Subscriber List** tab

Click **+** Button to add a new Subscriber

Fill the IMSI, security context(K, OPc), and attach a profile to that subscriber.

Click SAVE Button.


Figure 4 Add subscriber

OPNcell offers the option of adding multiple user at a go through the bulk insertion functionality. Both .csv and .inc file formats are accepted. It should follow the below template.

| imsi | ki  | opc |
| --- | --- | --- |
| 9997080930195106 | EF84CE78D9C47D64A6765B87972119F7 | 4723E4872557013C4F39A1D8E4D59CE4 |

Table 1 File template

To add multiple subscribers at a go, you can do that in the following order:

Go to Users Menu.

Go to Bulk Insertion tab

Choose and upload the file. If successfully uploaded, Attach a profile(s)

Click SAVE Button.

## Logging

All log files in OPNcell for the different services can be found under the **Diagnostics** sub menu.

## Uninstalling OPNcell

To uninstall the package, run pkg install os-cellular-devel in the console.