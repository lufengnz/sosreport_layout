#!/usr/bin/python3
import sys
import os
import re

#######################################################################################
#printout with color
BLACK, BLUE, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#following from Python cookbook, #475186
def has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False
has_colours = has_colours(sys.stdout)


def printout(text, colour=WHITE):
        if has_colours:
                seq = "\x1b[1;%dm" % (30+colour) + text + "\x1b[0m"
                sys.stdout.write(seq)
        else:
                sys.stdout.write(text)

#######################################################################################

def get_lines(cmd):
    lines_popen = os.popen(cmd)
    lines_read = lines_popen.read()
    return lines_read

#######################################################################################
printout("#*" * 10 + " SYSTEM INFO " + "*#" * 10, BLUE)
print("\n")

systeminfo_list = ['egrep -hs \"^NAME|^VERSION_ID\" etc/*release', 'cat sos_commands/kernel/uname_-a', 'cat sos_commands/host/uptime', 'cat sos_commands/systemd/timedatectl']
list(map(lambda cmd: (print(cmd), os.system(cmd), print()), systeminfo_list))

#######################################################################################
printout("#*" * 10 + " CPU&MEMORY INFORMATION " + "*#" * 10, BLUE)
print("\n")

cpumeminfo_list = ['cat sos_commands/processor/lscpu', 'grep -s ^Total sos_commands/memory/lsmem_-a_-o_RANGE_SIZE_STATE_REMOVABLE_ZONES_NODE_BLOCK', 'egrep -s \"Ethernet|Fibre|InfiniBand\" sos_commands/pci/lspci_-nnvv']
list(map(lambda cmd: (print(cmd), os.system(cmd), print()), cpumeminfo_list))

#######################################################################################
printout("#*" * 10 + " NETWORK INFORMATION " + "*#" * 10, BLUE)
print("\n")

networkinfo_list = ['ls etc/sysconfig/network-scripts/ifcfg-*', 'grep -H -s BONDING_OPTS etc/sysconfig/network-scripts/ifcfg-*', 'egrep \"bridge|ethernet\" sos_commands/networkmanager/nmcli_con']
list(map(lambda cmd: (print(cmd), os.system(cmd), print()), networkinfo_list))

#######################################################################################
# ovirt Sepecified

ovirtinfo_list = ['egrep -s -h \"^ovirt-engine.service|^vdsmd.service\" sos_commands/systemd/systemctl_list-units', 'egrep -s -h \"^ovirt-engine-4|^vdsm|kvm|qemu|libvirt\" sos_commands/rpm/* | awk \'{print $1}\'']
list(map(lambda cmd: (print(cmd), os.system(cmd), print()), ovirtinfo_list))


#######################################################################################
printout("#*" * 10 + " MISCELLANEOUS INFORMATION " + "*#" * 10, BLUE)
print("\n")
miscellaneous_list = ['egrep -s $ sos_commands/selinux/sestatus', 'grep -s vm.min_free_kbytes sos_commands/kernel/sysctl_-a', 'grep -s sysrq sos_commands/kernel/sysctl_-a', 'grep -s panic sos_commands/kernel/sysctl_-a']
list(map(lambda cmd: (print(cmd), os.system(cmd), print()), miscellaneous_list))

