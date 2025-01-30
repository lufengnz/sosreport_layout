import os
import subprocess
import json

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip() if result.stdout else "N/A"

def collect_data():
    sections = {
        "SYSTEM INFO": [
            'egrep -hs "^NAME|^VERSION_ID" /etc/*release', 
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
    
    with open("system_info.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print("System information saved to system_info.json")

    generate_html(results)

def generate_html(data):
    uname_output = data.get("SYSTEM INFO", {}).get('cat sos_commands/kernel/uname_-a', "System Information")
    uname_title = uname_output.split()[1] if len(uname_output.split()) > 1 else uname_output
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Information</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>{uname_title}</h1>
    """
    for section, commands in data.items():
        html_content += f"<h2>{section}</h2><table><tr><th>Command</th><th>Output</th></tr>"
        for cmd, output in commands.items():
            html_content += f"<tr><td>{cmd}</td><td><pre>{output}</pre></td></tr>"
        html_content += "</table>"
    
    html_content += "</body></html>"
    
    with open("system_info.html", "w") as f:
        f.write(html_content)
    
    print("System information saved to system_info.html")

if __name__ == "__main__":
    collect_data()
