## What is OPNCell
  OPNCcell is an out-of-box <a href="https://opnsense.org/">OPNsense</a> plugin that adds Private 5G & LTE network capability.
  The plugin adds 5G/LTE services to OPNSense using the Open Source <a href="https://open5gs.org/open5gs/docs/>Open5Gs</a> software. By
  combining advanced packet filtering &amp; management with 4G/5G capability, OPNcell offers a low-cost complete solution for private LTE deployments.

## What is Open5Gs

 
<a href="https://open5gs.org/open5gs/docs/>Open5Gs</a>  is a C-language Open Source implementation of 5GC and EPC, i.e. the core network of NR/LTE network. Open5GS natively supports  4G/5G Standalone mode as well as non-standalone (both 4G and 5G.)


## What is OPNsense

<a href="https://opnsense.org/">OPNsense</a> is a mature open source, FreeBSD-based firewall, intrusion-detection, routing & web-filtering system.


## Installation

Run the below command in the console of the machine running the OPNsense firewall.<br><br>
`fetch -o /usr/local/etc/pkg/repos/opncell.conf http://repo.opncell.io/cellular.conf && pkg update` <br><br>
This establishes the repository holding the cellular package installer, including other necessary pieces of the service.

## Getting into it

Once you have the repo set up on your machine, you can proceed to install the package by simply running<br><br> `pkg install os-cellular-devel` <br>

In the GUI, set up the loop back addresses for each of the open5gs services.<br> 
Add the virtual addresses under; <br>

'Interfaces > Virtual IPs'
  >>> Include screenshots <<<

## Sponsors

If you find OPNcell useful please consider supporting this Open Source project by becoming a sponsor.



