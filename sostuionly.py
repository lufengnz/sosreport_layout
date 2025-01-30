#!/usr/bin/python3
import os
import subprocess
from rich.console import Console
from rich.table import Table

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return "\n".join(result.stdout.splitlines()) if result.stdout else "N/A"

def collect_data():
    console = Console()
    sections = {
        "SYSTEM INFO": [
            'egrep -hs "^NAME|^VERSION_ID" etc/*release', 
            'cat sos_commands/kernel/uname_-a', 
            'cat sos_commands/host/uptime', 
            'cat sos_commands/systemd/timedatectl'
        ],
        "CPU & MEMORY INFORMATION": [
            'grep -v Flags sos_commands/processor/lscpu', 
            'grep -s ^Total sos_commands/memory/lsmem_-a_-o_RANGE_SIZE_STATE_REMOVABLE_ZONES_NODE_BLOCK', 
            'egrep -s "Ethernet|Fibre|InfiniBand" sos_commands/pci/lspci_-nnvv'
        ],
        "NETWORK INFORMATION": [
            'ls etc/sysconfig/network-scripts/ifcfg-*', 
            'grep -H -s BONDING_OPTS etc/sysconfig/network-scripts/ifcfg-*', 
            'egrep "bridge|ethernet" sos_commands/networkmanager/nmcli_con'
        ],
        "OVIRT SPECIFIC INFORMATION": [
            'egrep -s -h "ovirt-engine.service|vdsmd.service" sos_commands/systemd/systemctl_list-units | tr -s \" \"', 
            'egrep -s -h "^ovirt-engine-4|^vdsm|kvm|qemu|libvirt" sos_commands/rpm/* | awk \'{print $1}\''
        ],
        "MISCELLANEOUS INFORMATION": [
            'egrep -s . sos_commands/selinux/sestatus', 
            'grep -s vm.min_free_kbytes sos_commands/kernel/sysctl_-a', 
            'grep -s sysrq sos_commands/kernel/sysctl_-a', 
            'grep -s panic sos_commands/kernel/sysctl_-a'
        ]
    }
    
    results = {}
    for section, commands in sections.items():
        results[section] = {cmd: run_command(cmd) for cmd in commands}
    
    display_tui(results, console)

def display_tui(data, console):
    for section, commands in data.items():
        table = Table(title=section)
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Output", style="magenta")
        
        for cmd, output in commands.items():
            first_row = True
            for line in output.split("\n"):
                if first_row:
                    table.add_row(cmd, line)
                    first_row = False
                else:
                    table.add_row("", line)
        
        console.print(table)

if __name__ == "__main__":
    collect_data()
