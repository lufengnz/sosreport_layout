#!/usr/bin/python3

import os
import subprocess
from tabulate import tabulate

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip() if result.stdout else "N/A"

def print_section(title, commands):
    print("\n" + "#" * 80)
    print(f"{title.center(80)}")
    print("#" * 80 + "\n")
    
    results = [[cmd, run_command(cmd)] for cmd in commands]
    print(tabulate(results, headers=["Command", "Output"], tablefmt="grid"))
    print("\n")

systeminfo_list = [
    'egrep -hs "^NAME|^VERSION_ID" /etc/*release', 
    'cat sos_commands/kernel/uname_-a', 
    'cat sos_commands/host/uptime', 
    'cat sos_commands/systemd/timedatectl'
]
print_section("SYSTEM INFO", systeminfo_list)

cpumeminfo_list = [
    'grep -v Flags sos_commands/processor/lscpu', 
    'grep -s ^Total sos_commands/memory/lsmem_-a_-o_RANGE_SIZE_STATE_REMOVABLE_ZONES_NODE_BLOCK', 
    'egrep -s "Ethernet|Fibre|InfiniBand" sos_commands/pci/lspci_-nnvv'
]
print_section("CPU & MEMORY INFORMATION", cpumeminfo_list)

networkinfo_list = [
    'ls /etc/sysconfig/network-scripts/ifcfg-*', 
    'grep -H -s BONDING_OPTS /etc/sysconfig/network-scripts/ifcfg-*', 
    'egrep "bridge|ethernet" sos_commands/networkmanager/nmcli_con'
]
print_section("NETWORK INFORMATION", networkinfo_list)

ovirtinfo_list = [
    'egrep -s -h "^ovirt-engine.service|^vdsmd.service" sos_commands/systemd/systemctl_list-units', 
    'egrep -s -h "^ovirt-engine-4|^vdsm|kvm|qemu|libvirt" sos_commands/rpm/* | awk \'{print $1}\''
]
print_section("OVIRT SPECIFIC INFORMATION", ovirtinfo_list)

miscellaneous_list = [
    'egrep -s . sos_commands/selinux/sestatus', 
    'grep -s vm.min_free_kbytes sos_commands/kernel/sysctl_-a', 
    'grep -s sysrq sos_commands/kernel/sysctl_-a', 
    'grep -s panic sos_commands/kernel/sysctl_-a'
]
print_section("MISCELLANEOUS INFORMATION", miscellaneous_list)
