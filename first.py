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
printout("#*" * 10 + " SYSTEM TYPE " + "*#" * 10, BLUE)
print("\n")

# Check OVS or Linux
def hyper_check_result():
    hyper_check = os.popen('grep -s VM etc/*-release || echo 0')
    hyper_read = hyper_check.read()
    hyper_split = hyper_read.split(" ")
    hyper_check.close()
    if hyper_read[0] == "0":
        return "Oracle Linux"
    else:
        return "Oracle VM Server"
os_type = hyper_check_result()
print("This is an " + os_type + ". \n")

vm_check = os.popen('egrep -s "xen_netfront|xen_blkfront" lsmod || echo 0')
vm_read = vm_check.read()
vm_split = vm_read.split(" ")
vm_check.close()
isVM = 0
if vm_read[0] != "0":
    print("xen PV drivers found, lsmod xen:\n" + "*" * 40)
    print(vm_read)
    isVM = 1

ovirtnode_check = os.popen('grep -s "Manufacturer: oVirt" sos_commands/hardware/dmidecode || echo 0')
ovirtnode_read = ovirtnode_check.read()
ovirtnode_split = ovirtnode_read.split(" ")
ovirtnode_check.close()
isOVIRTNODE = 0
if ovirtnode_read[0] != "0":
	print("This is a VM on oVirt node.\n")
	isOVIRTNODE = 1

ovirtengine_check = os.popen('grep -s ^ovirt-engine.service sos_commands/systemd/systemctl_list-units || echo 0')
ovirtengine_read = ovirtengine_check.read()
ovirtengine_split = ovirtengine_read.split(" ")
ovirtengine_check.close()
isOVIRTENGINE = 0
if ovirtengine_read[0] != "0":
	print("This is an oVirt Engine.\n")
	isOVIRTENGINE = 1

ovirtkvm_check = os.popen('grep -s ^vdsmd.service sos_commands/systemd/systemctl_list-units || echo 0')
ovirtkvm_read = ovirtkvm_check.read()
ovirtkvm_split = ovirtkvm_read.split(" ")
ovirtkvm_check.close()
isovirtKVM = 0
if ovirtkvm_read[0] != "0":
	print("This is an oVirt KVM.\n")
	isovirtKVM = 1

isSHE = 0
if isOVIRTENGINE == 1:
	if isOVIRTNODE == 1:
		print("This is a Self Hosted Engine.\n")
		isSHE = 1

#######################################################################################
printout("#*" * 10 + " BASIC INFORMATION " + "*#" * 10, BLUE)
print("\n")

# release information
print("release information\n" + "*" * 40)
release_check = os.popen('grep -Hi -s server etc/*release')
release_read = release_check.read()
print(release_read)
release_check.close()
# basic information of uname, uptime and date
def print_basic(cmd):
    cmdout_open = open(cmd)
    cmdout = cmdout_open.read()
    print(cmd + "\n" + "*" * 40)
    print(cmdout)
    cmdout_open.close()
basic_cmd_grp = ("uname", "uptime", "date")
mapping_cmd_grp = map(print_basic, basic_cmd_grp)
# dmidecode
print("dmidecode\n" + "*" * 40)
dmide = os.popen('grep -s -A 2 "System Information" dmidecode')
dmide_sysinfo = dmide.read()
print(dmide_sysinfo)
dmide.close()



#######################################################################################
printout("#*" * 10 + " CPU&MEMORY INFORMATION " + "*#" * 10, BLUE)
print("\n")

# meminfo
if os_type == "Oracle Linux":
    print("meminfo\n" + "*" * 40)
else:
    print("dom0 meminfo\n" + "*" * 40)
mem = os.popen('head -n 4 proc/meminfo; egrep -s "SwapTotal|SwapFree" proc/meminfo')
mem_info = mem.read()
print(mem_info)
mem.close()
# total memory and HugePages
def get_float_num(cmd):
    para_open = os.popen(cmd)
    para_read = para_open.read()
    para_num = re.findall(r'\d+', para_read)
    para_open.close()
    return float(para_num[0])
def GB_or_TB(mem_cmd):
    mem_GB = round(get_float_num(mem_cmd) / 1024 / 1024, 2)
    if mem_GB >= 1024:
        mem_TB = round(float(mem_GB) / 1024, 2)
        print(str(mem_TB) + " TB \n")
    else:
        print(str(mem_GB) + " GB \n")
mem_cmd = "head -n 1 proc/meminfo"
if os_type == "Oracle Linux":
    print("total memory\n" + "*" * 40)
    GB_or_TB(mem_cmd)
else:
    print("dom0 memory\n" + "*" * 40)
    GB_or_TB(mem_cmd)
    ovs_mem_cmd = "grep -s total_memory sos_commands/xen/xm_info || grep -s total_memory sos_commands/ovm3/xm.info"
    ovs_mem_GB = round(get_float_num(ovs_mem_cmd) / 1024, 2)
    print("OVS total memory\n" + "*" * 40)
    if ovs_mem_GB >= 1024:
        ovs_mem_TB = round(float(ovs_mem_GB) / 1024, 2)
        print(str(ovs_mem_TB) + " TB \n")
    else:
        print(str(ovs_mem_GB) + " GB \n")
if os_type == "Oracle Linux":
    hugepage_exist_check = os.popen('grep -s HugePages_Total proc/meminfo || echo 0')
    hugepage_exist_read = hugepage_exist_check.read()
    hugepage_exist_split = hugepage_exist_read.split(" ")
    hugepage_exist_check.close()
    if hugepage_exist_read[0] == "0":
        print("No HugePages found in proc/meminfo! \n")
    else:
        hugepage_cmd = "grep -s HugePages_Total proc/meminfo"
        hugepage_KB = get_float_num(hugepage_cmd) * 2048
        hugepage_pct = round(hugepage_KB / get_float_num(mem_cmd), 4)
        if hugepage_KB == 0:
            print("No HugePages configured. \n")
        else:
            print("HugePages\n" + "*" * 40)
            print(str(int(hugepage_KB)) + " KB")
            print("HugePages used " + str(hugepage_pct * 100) + "% of total memory \n")


#######################################################################################
# cpuinfo
if os_type == "Oracle Linux":
    print("cpuinfo\n" + "*" * 40)
else:
    print("dom0 cpuinfo\n" + "*" * 40)
print("--Total logical CPU:")
cinfo = os.popen('grep -s processor proc/cpuinfo | wc -l')
cinfo_read = cinfo.read()
cinfo.close()
print(cinfo_read)
def get_int_num(cmd):
    para_open = os.popen(cmd)
    para_read = para_open.read()
    para_num = re.findall(r'\d+', para_read)
    para_open.close()
    return int(para_num[0])
if os_type == "Oracle Linux":
    siblings_exist_check = os.popen(' grep -s siblings proc/cpuinfo')
    siblings_exist_read = siblings_exist_check.read()
    siblings_exist_check.close()
    if siblings_exist_read == "":
        print("No CPU core information. \n")
    else:
        siblings_num = get_int_num('grep -s siblings proc/cpuinfo | uniq')
        cores_num = get_int_num('grep -s cores proc/cpuinfo | uniq')
        if siblings_num / cores_num == 1:
            print("CPU HyperThreading is not enabled. \n")
        else:
            print("CPU HyperThreading is enabled: \n" + " CPU cores: " + str(cores_num) + "\n CPU threads: " + cinfo_read)
else:
 # grep C-states sos_commands/ovm3/xenpm.get-cpuidle-states | uniq
    print("--C-states")
    cpuc_check = os.popen('grep -s C-states sos_commands/ovm3/xenpm.get-cpuidle-states | uniq')
    cpuc_read = cpuc_check.read()
    print(cpuc_read)
    cpuc_check.close()

#######################################################################################
printout("#*" * 10 + " PCI INFORMATION " + "*#" * 10, BLUE)
print("\n")

#lspci
def get_lspci(pci_type):
    print(pci_type + ": ")
    count = 0
    for line in os.popen('grep -s -i ' + pci_type + ' lspci | grep -s rev'):
        if line[0] == " ":
            continue;
        else:
            sys.stdout.write(line)
            count += 1
    print("Totally " + str(count) + " " + pci_type + " device(s) found \n")
pci_list = ("Ethernet", "Fibre", "InfiniBand")
print("lspci\n" + "*" * 40)
mapping_pci = map(get_lspci, pci_list)

#######################################################################################
printout("#*" * 10 + " NETWORK INFORMATION " + "*#" * 10, BLUE)
print("\n")

#network
print("Network\n" + "*" * 40)
def get_lines(cmd):
    lines_popen = os.popen(cmd)
    lines_read = lines_popen.read()
    print("# " + cmd)
    print(lines_read)
    lines_popen.close()
net_list = ("ls etc/sysconfig/network-scripts/ifcfg-*", "grep -H -s MTU etc/sysconfig/network-scripts/ifcfg-*bond*", "grep -H -s BONDING_OPTS etc/sysconfig/network-scripts/ifcfg-*bond*", "grep -s $ route")
net_get_lines = map(get_lines, net_list)

#######################################################################################
# ovirt Sepecified
if isOVIRTENGINE == 1 or isovirtKVM == 1:
	printout("#*" * 10 + " oVirt Information " + "*#" * 10, BLUE)
	print("\n")

	if isOVIRTENGINE == 1:
		ovirtcli_list = ("grep -s ^ovirt-engine.service sos_commands/systemd/systemctl_list-units", "grep -s -h ^ovirt-engine-4 sos_commands/rpm/* | awk \'{print $1}\'")
		ovirtcli_get_lines = map(get_lines, ovirtcli_list)
	if isovirtKVM == 1:
		kvmcli_list = ("grep -s ^vdsmd.service sos_commands/systemd/systemctl_list-units", "grep -s -h ^vdsm-4 sos_commands/rpm/* | awk \'{print $1}\'")
		kvmcli_get_lines = map(get_lines, kvmcli_list)


#######################################################################################
# OVM Sepecified
if os_type == "Oracle VM Server":
    printout("#*" * 10 + " ORACLE VM INFORMATION " + "*#" * 10, BLUE)
    print("\n")
# xm info
    print("xm info\n" + "*" * 40)
    xminfo_check = os.popen('grep -s $ sos_commands/xen/xm_info || grep -s $ sos_commands/ovm3/xm.info')
    xminfo_read = xminfo_check.read()
    print(xminfo_read)
    xminfo_check.close()
# OCFS2
    print("OCFS2\n" + "*" * 40)
    nodecount_check = os.popen('grep -s node_count sos_commands/ocfs2/ocfs2.cluster.conf || echo 0')
    nodecount_read = nodecount_check.read()
    nodecount_num = re.findall(r'\d+', nodecount_read)
    print("there are " + str(nodecount_num[0]) + " OCFS2 node(s) in cluster:")
    if nodecount_num[0] != "0":
#        nodename_check = os.popen('grep -s name sos_commands/ocfs2/ocfs2.cluster.conf | head -n ' + nodecount_num[0] + ' || echo 0')
#        for line in nodename_check:
#            nodename_strip = line.strip()
#            print(nodename_strip)
#        nodename_check.close()
         ocfs2cluster_check = os.popen('cat sos_commands/ocfs2/ocfs2.cluster.conf')
         ocfs2cluster_read = ocfs2cluster_check.read()
         print(ocfs2cluster_read)
         ocfs2cluster_check.close()
    print("\n" + "--o2cb service status:")
    o2cbout_open = os.popen('egrep -s -v "#|^$" etc/sysconfig/o2cb')
    o2cbout = o2cbout_open.read()
    print(o2cbout)
    print("--OCFS2 mount points:")
    ocfs2mount_check = os.popen('grep -s ocfs2 mount')
    ocfs2mount_read = ocfs2mount_check.read()
    print(ocfs2mount_read)
    ocfs2mount_check.close()
    nodecount_check.close()
    o2cbout_open.close()
# management network
    print("Management Network:\n" + "*" * 40)
    xenmgt_check = os.popen('grep -Hi -s MANAGEMENT etc/sysconfig/network-scripts/meta-* | awk \'BEGIN {FS="/"}{print $4}\' | awk \'BEGIN {FS=":"}{print $1}\' | awk \'BEGIN {FS="-"} {print $2}\'')
    xenmgt_read = xenmgt_check.read()
    print(xenmgt_read)
    xenmgt_check.close()

    xenmgtrole_check = os.popen('grep -Hi -s MANAGEMENT etc/sysconfig/network-scripts/meta-* |awk \'BEGIN {FS="/"}{print $4}\'')
    xenmgtrole_read = xenmgtrole_check.read()
    print(xenmgtrole_read)
    xenmgtrole_check.close()
# dump OVS
    print("Dump ovs-agent:\n" + "*" * 40)
    ovsdump_list = ("grep -s $ sos_commands/ovm3/dump_db_server | grep -v parameter", "grep -s $ sos_commands/ovm3/dump_db_serverpool | grep -v parameter", "grep -s $ sos_commands/ovm3/dump_db_server_pool_servers | grep -v parameter", "grep -s $ sos_commands/ovm3/dump_db_repository | grep -v parameter", "grep -s $ sos_commands/ovm3/ovspoolfs", "grep -s $ sos_commands/ovm3/ovsrepo")
    ovsdump_get_lines = map(get_lines, ovsdump_list)
# services  status
    print("Services:\n" + "*" * 40)
    servicesovs_list = ("grep -s -A6 ^log sos_commands/startup/service_--status-all", "grep -s ^ovm-consoled sos_commands/startup/service_--status-all")
    servicesovs_get_lines = map(get_lines, servicesovs_list)

#######################################################################################
printout("#*" * 10 + " KDUMP INFORMATION " + "*#" * 10, BLUE)
print("\n")

#kdump
kdump_list = ("egrep -s \"kexec-tools|busybox\" installed-rpms", "grep -s kdump chkconfig", "egrep -v -s \"#|^$\" etc/sysconfig/kdump", "egrep -v -s \"#|^$\" etc/kdump.conf", "egrep -v -s \"#|^$\" etc/default/grub", "grep -s $ proc/cmdline", "grep -s -i crashkernel sos_commands/ovm3/xm.dmesg")
kdump_get_lines = map(get_lines, kdump_list)

#######################################################################################
printout("#*" * 10 + " MISCELLANEOUS INFORMATION " + "*#" * 10, BLUE)
print("\n")

miscellaneous_list =("egrep -s $ sos_commands/selinux/sestatus", "grep -s vm.min_free_kbytes sos_commands/kernel/sysctl_-a", "grep -s sysrq sos_commands/kernel/sysctl_-a", "grep -s panic sos_commands/kernel/sysctl_-a", "grep -s oracleasm installed-rpms", "grep -s $ etc/modprobe.conf")
miscellaneous_get_lines = map(get_lines, miscellaneous_list)