## Getting Started
This is OPNcell, an out of box OPNsense plugin that incorporates all the native FreeBSD services to deploying a 3GPP Release 17 cellular core network.  It natively supports  4G SA, 5G SA, as well as NSA (both 4G and 5G.) <br>
To ensure network security, OPNcell is deployed within a highly configurable [OPNsense](https://opnsense.org/) firewall. You can check out the OPNsense repo [here](https://github.com/opnsense).<br>

OPNcell utilizes [Open5gs](https://open5gs.org/open5gs/docs/) a C-language implementation of a cellular core network. You can fork the repo [here](https://github.com/open5gs/open5gs)

## Installation
Run the below command in the console of the machine running the OPNsense firewall.<br><br>
`fetch -o /usr/local/etc/pkg/repos/opncell.conf http://repo.opncell.io/cellular.conf && pkg update` <br><br>
This establishes the repository holding the cellular package installer, including other necessary pieces of the service.

## Getting into it
Once you have the repo set up on your machine, you can proceed to install the package by simply running pkg install os-cellular-devel <br>
In the GUI, set up the loop back addresses for each of the open5gs services.<br> 
Add the virtual addresses under; <br>

'Interfaces > Virtual IPs'

## Sponsers
If you find OPNcell useful please consider supporting this Open Source project by becoming a sponsor.


