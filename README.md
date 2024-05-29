## Getting Started
This is Cellular. An out of box way of deploying private cellular networks.i.e 4G, 5G, as well as 5G NSA. <br>
To ensure a secure network, Cellular is built behind a firewall, i.e. [OPNsense](https://opnsense.org/) firewall. You can check out the OPNsense repo [Here](https://github.com/opnsense).<br>
Cellular utilizes [Open5gs](https://open5gs.org/open5gs/docs/) which is a C-language implementation for 5G Core and EPC. You can fork the repo [Here](https://github.com/open5gs/open5gs)

## Installation
Run the below command in the commandline of the machine running the OPNsense firewall.<br>
`fetch -o /usr/local/etc/pkg/repos/opncell.conf http://repo.opncell.io/cellular.conf && pkg update` <br>
This establishes the repository holding the cellular package installer, plus other necessary pieces of the puzzle

## Getting into it
Once you have the repo set up on your machine, you can proceed to install the package by running **pkg install os-cellular-devel** <br>
In the GUI, set up the loop back addresses for each of the open5gs services.<br> To add the addresses; Interfaces ----->Virtual IPs

## Sponsers
If you find Cellular useful for work, please consider supporting this Open Source project by Becoming a sponsor.


