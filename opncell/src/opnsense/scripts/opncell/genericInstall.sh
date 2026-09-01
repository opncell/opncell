#!/bin/bash

# This script installs the generic requirements of the network ie, mongodb and open5gs along with its dependencies
# Also starts the services required
#Further install may be required.

# Check if the script is run as root (or with sudo)
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root or with sudo."
   exit 1
fi

echo "#############################################################"
echo "The following packages are going to be Installed on your system."
echo "-->> MongoDB plus all its dependencies"
echo "-->> Open5GS plus all its dependencies"
echo "##############################################################"
printf "\n"
echo "=====> Enabling SCTP support ............ Started"
printf "\n"

echo "=====> Activating custom repository ............ Started"
printf "\n"

touch /boot/loader.conf.local
# shellcheck disable=SC2129
echo sctp_load="YES" >>  /boot/loader.conf.local
echo if_ix_updated_load="YES" >> /boot/loader.conf.local
echo hw.if_ix_updated.unsupported_sfp=1 >> /boot/loader.conf.local
echo hw.ix.unsupported_sfp=1 >> /boot/loader.conf.local
echo hw.ixgbe.unsupported_sfp=1 >> /boot/loader.conf.local
kldload sctp.ko

printf '%b\n' "\033[1m"=====> Enabling SCTP support................................................... Done"\033[0m"

echo DEVELOPER=yes >> /etc/make.conf

printf '%b\n' "\033[1m"=====> Installing Nano ................................................... Starting"\033[0m"
#if  ! pkg info -l nano; then
  pkg install -y nano
#fi
#
#if pkg info -l nano ; then
#
#printf '%b\n' "\033[1m"=====> Installing Nano ................................................... Done"\033[0m"
#fi
#printf "\n"

#printf '%b\n' "\033[1m"=====> Updating OPNsense ports ................................................... Starting"\033[0m"
#if opnsense-code tools ports src; then
#  printf '%b\n' "\033[1m"=====> Updating OPNsense ports ................................................... Done"\033[0m"
#else
#  printf '%b\n' "\033[1m"=====> Updating OPNsense ports  ................................................... Done"\033[0m"
#fi
#printf "\n"

printf '%b\n' "\033[1m"=====> Installing dependencies for Open5GS ................................................... Starting"\033[0m"

printf "\n"
echo "=====> installing cmake ............ Started"
pkg install -y cmake
printf "\n"
echo "=====> installing ninja ............ Started"
pkg install -y ninja
printf "\n"
echo "=====> installing bison ............ Started"
pkg install -y bison
printf "\n"
echo "=====> installing pkgconf ............ Started"
pkg install -y pkgconf
printf "\n"
echo "=====> installing git ............ Started"
pkg install -y git
printf "\n"
echo "=====> installing gnutls ............ Started"
pkg install -y gnutls
printf "\n"
echo "=====> installing libgcrypt ............ Started"
pkg install -y libgcrypt
printf "\n"
echo "=====> installing libidn ............ Started"
pkg install -y libidn
printf "\n"
echo "=====> installing libyaml ............ Started"
pkg install -y libyaml
printf "\n"
echo "=====> installing talloc ............ Started"
pkg install -y talloc
printf "\n"
echo "=====> installing gmake ............ Started"
pkg install -y gmake
printf "\n"
echo "=====> installing texinfo ............ Started"
pkg install -y texinfo

printf '%b\n' "\033[1m"=====> Installing libmicrohttpd, nghttp2, mongo-c-driver, gsed, gcc ................................................... Starting"\033[0m"
printf "\n"
echo "=====> installing libmicrohttpd ............ Started"
pkg install -y libmicrohttpd
printf "\n"
echo "=====> installing nghttp2 ............ Started"
pkg install -y nghttp2
printf "\n"
echo "=====> installing mongo-c-driver ............ Started"
pkg install -y mongo-c-driver
printf "\n"
echo "=====> installing gsed ............ Started"
pkg install -y gsed
printf "\n"
echo "=====> installing gcc ............ Started"
pkg install -y gcc

printf '%b\n' "\033[1m"=====> Installing meson dependencies................................................... Starting"\033[0m"
printf "\n"
echo "=====> installing python39 ............ Started"
pkg install -y python39
printf "\n"
echo "=====> installing py-setuptools ............ Started"
pkg install -y py-setuptools
printf "\n"
echo "=====> installing py-wheel ............ Started"
pkg install -y py-wheel
printf "\n"
echo "=====> installing py-build ............ Started"
pkg install -y py-build
printf "\n"
echo "=====> installing py-installer ............ Started"
pkg install -y py-installer
printf "\n"
echo "=====> installing py-pytest-xdist ............ Started"
pkg install -y py-pytest-xdist
printf "\n"
echo "=====> installing py-setuptools_scm ............ Started"
pkg install -y py-setuptools_scm
printf "\n"
echo "=====> installing meson ............ Started"
pkg install -y meson

wget -r -np -nH --cut-dirs=1 -P /root/ http://192.168.100.19/mongo/

setenv LIBRARY_PATH /usr/local/lib
setenv C_INCLUDE_PATH /usr/local/include

# Download and compile Open5GS (example)
printf '%b\n' "\033[1m"=====> Downloading and compiling Open5GS ................................................... Starting"\033[0m"
printf "\n"

mkdir -p /usr/ports

cd /usr/ports/ || exit 1
wget -r -np -nH --cut-dirs=1 -P /root/ http://192.168.100.19/open5gs/

#git clone https://github.com/open5gs/open5gs.git

cd /usr/ports/open5gs/subprojects/freeDiameter/include/freeDiameter || exit 1

printf '%b\n' "\033[1m"=====> Editing Free diameter ................................................... Starting"\033[0m"

filename="libfdproto.h"
line_to_replace="static char * file_bname_init(char * full) { file_bname = basename(full); return file_bname; }"
replacement_line="static char * file_bname_init(char * full) { file_bname = __old_basename(full); return file_bname; }"

# Temporary file for storing modified content
touch temp.txt
tempfile=temp.txt
#
## Read the input file line by line
while IFS= read -r line; do
    # Check if the current line matches the line to replace
    if [[ "$line" == "$line_to_replace" ]]; then
        # Replace the line with the replacement line
        echo "$replacement_line" >> "$tempfile"
    else
        # Keep the original line
        echo "$line" >> "$tempfile"
    fi
done < "$filename"

## Overwrite the original file with the modified content
mv "$tempfile" "$filename"
printf "\n"
echo "=====> Editing Free diameter .................................................... Done"

cd /usr/ports/open5gs || exit 1
meson build --prefix=/usr/ports/open5gs/install
ninja -C build
cd build || exit 1
meson test -v
ninja install

run_service() {
    local service_name="$1"
    local service_command="$2"

    echo "Starting $service_name..."
    cd "$service_command" || {
        echo "Error: Failed to change directory to $service_name."
        return 1
    }

    ./install/bin/"$service_name"

    if [ $? -eq 0 ]; then
        echo "$service_name started successfully."
    else
        echo "Error: Failed to start $service_name."
    fi

    cd /usr/ports/open5gs || exit 1 # Return to the previous directory
}

checkMongo() {

    command="ps aux | grep mongod | awk '\$8 == \"I+\" || \$8 == \"Is\" || \$8 == \"T\" {print \$8}'"
    status=$(eval "$command")
    if test "$status" == "T"; then
       pid_command="ps aux | grep mongod | awk '\$8 == \"T\" {print \$2}'"
       pid=$(eval "$pid_command")
       kill -9 "$pid"
      mongo_binary_path=$(which mongod)
      directory_path=$(dirname "$mongo_binary_path")
      cd "$directory_path" || exit 1
      mongod --dbpath ./data/db &
  sleep 2
    fi

   if test -z  "$status" ; then
      mongo_binary_path=$(which mongod)
      directory_path=$(dirname "$mongo_binary_path")
      cd "$directory_path" || exit 1
      mkdir -p ./data/db
      mongod --dbpath ./data/db &
sleep 2
 fi
}

checkMongo

# Change to the directory where the services are located
#cd /usr/ports/open5gs || exit 1

# Start the services one by one
#run_service "open5gs-nrfd" "./install/bin/open5gs-nrfd"
#run_service "open5gs-scpd" "./install/bin/open5gs-scpd"
#run_service "open5gs-amfd" "open5gs-amfd"
#run_service "open5gs-smfd" "open5gs-smfd"
#run_service "open5gs-upfd" "open5gs-upfd"
#run_service "open5gs-ausfd" "./install/bin/open5gs-ausfd"

echo "All services started."


  echo "Installation complete."
  echo "/n"
  echo "The below loopback addresses should be enabled on the GUI"
  echo "MongoDB   = 127.0.0.1 (subscriber data) - http://localhost:3000"
  echo "MME-s1ap  = 127.0.0.2 :36412 for S1-MME"
  echo "MME-gtpc  = 127.0.0.2 :2123 for S11"
  echo "MME-frDi  = 127.0.0.2 :3868 for S6a"
  echo "SGWC-gtpc = 127.0.0.3 :2123 for S11"
  echo "SGWC-pfcp = 127.0.0.3 :8805 for Sxa"
  echo "SMF-gtpc  = 127.0.0.4 :2123 for S5c, N11"
  echo "SMF-gtpu  = 127.0.0.4 :2152 for N4u (Sxu)"
  echo "SMF-pfcp  = 127.0.0.4 :8805 for N4 (Sxb)"
 echo "SMF-frDi  = 127.0.0.4 :3868 for Gx auth"
 echo "SMF-sbi   = 127.0.0.4 :7777 for 5G SBI (N7,N10,N11)"
  echo "AMF-ngap  = 127.0.0.5 :38412 for N2"
  echo "AMF-sbi   = 127.0.0.5 :7777 for 5G SBI (N8,N12,N11)"
  echo "SGWU-pfcp = 127.0.0.6 :8805 for Sxa"
  echo "SGWU-gtpu = 127.0.0.6 :2152 for S1-U, S5u"
  echo "UPF-pfcp  = 127.0.0.7 :8805 for N4 (Sxb)"
 echo "UPF-gtpu  = 127.0.0.7 :2152 for S5u, N3, N4u (Sxu) (needs to be changed to the interface hosting the xNBs)"
  echo "HSS-frDi  = 127.0.0.8 :3868 for S6a, Cx"
 echo  "PCRF-frDi = 127.0.0.9 :3868 for Gx"
 echo  "NRF-sbi   = 127.0.0.10:7777 for 5G SBI"
  echo "SCP-sbi   = 127.0.1.10:7777 for 5G SBI"
 echo "AUSF-sbi  = 127.0.0.11:7777 for 5G SBI"
 echo "UDM-sbi   = 127.0.0.12:7777 for 5G SBI"
 echo "PCF-sbi   = 127.0.0.13:7777 for 5G SBI"
echo   "NSSF-sbi  = 127.0.0.14:7777 for 5G SBI"
echo "BSF-sbi   = 127.0.0.15:7777 for 5G SBI"
  echo "UDR-sbi   = 127.0.0.20:7777 for 5G SBI"



# Clean up (optional)
# rm -rf /tmp/open5gs

exit 0
