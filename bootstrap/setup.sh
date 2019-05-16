#!/bin/bash

# make scripts executable
sudo chmod +x /mnt/flash/bootstrap/interface_monitor.py
sudo chmod +x /mnt/flash/bootstrap/webapp.py

# dhcpd
sudo cp /mnt/flash/bootstrap/dhcpd.conf /etc/dhcp/
sudo service dhcpd restart

cat << EOF | FastCli -M -e -p 15
enable
!
copy flash:bootstrap/dhcpd.rpm extension:
extension dhcpd.rpm
!
configure
!
daemon bootstrap-inft-monitor
  exec /mnt/flash/bootstrap/interface_monitor.py
  shutdown
  no shutdown
  exit

daemon bootstrap-app
  exec /mnt/flash/bootstrap/webapp.py
  shutdown
  no shutdown
  exit
!
EOF
