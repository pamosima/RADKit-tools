"""
Copyright (c) 2024 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import click
import os
import meraki
import json
import yaml
import csv
from getpass import getpass
from radkit_common.types import DeviceType
from radkit_service.control_api import ControlAPI
from radkit_service.webserver.models.devices import NewDevice, NewTerminal
from radkit_common.utils.formatting import to_canonical_name
from netutils.interface import canonical_interface_name
from dnacentersdk import api

# Modify API URL's
RADkit_URL = "https://localhost:8081/api/v1"
MERAKI_URL = "https://api.meraki.com/api/v1/"
DNAC_URL = "https://sandboxdnac.cisco.com"

# Initialize Meraki Dashboard API
def initialize_dashboard():
    print("Step 1 - Initialize Meraki Dashboard")
    return meraki.DashboardAPI(
        api_key=getpass(" Enter Meraki API key: "),
        base_url=MERAKI_URL,
        output_log=False,
        log_file_prefix=os.path.basename(__file__)[:-3],
        log_path='',
        print_console=False
    )

# Get devices from Meraki Dashboard
def get_devices_from_meraki(dashboard, network_id):
    devices = dashboard.networks.getNetworkDevices(network_id)
    return devices

def get_network_id_from_meraki():
    dashboard = initialize_dashboard()
    organizations = dashboard.organizations.getOrganizations()
    org_choice = select_organization(dashboard, organizations)
    if org_choice is not None:
        org_id, networks = org_choice
        network_choice = select_network(networks)
        if network_choice is not None:
            return dashboard, org_id, network_choice

# Select organization
def select_organization(dashboard, organizations):
    click.echo("Step 2 - Select Organization:")
    for i, org in enumerate(organizations):
        click.echo(f"  {i + 1}. Name: {org['name']}")
    org_index = click.prompt(f"Enter Organization index (1 - {len(organizations)})")
    try:
        org_id = organizations[int(org_index) - 1]['id']
        networks = dashboard.organizations.getOrganizationNetworks(org_id, total_pages='all')
        return org_id, networks
    except (ValueError, IndexError):
        click.echo("Invalid selection. Please select by index.")
        return None

# Select network
def select_network(networks):
    click.echo("Step 3 - Select Network:")
    for i, network in enumerate(networks):
        click.echo(f"  {i + 1}. Name: {network['name']}")
    network_index = click.prompt(f"Enter Network index (1 - {len(networks)})")
    try:
        network_id = networks[int(network_index) - 1]['id']
        return network_id
    except (ValueError, IndexError):
        click.echo("Invalid selection. Please select by index.")
        return None

# Prepare data from Meraki for JSON and write to file
def meraki_prepare_and_write_json(devices):
    click.echo("Step 4 - Getting Devices...")
    click.echo("Step 5 - Prepare data for JSON")
    sshUsername = input("  SSH Username: ")
    sshPassword = getpass("  SSH Password: ")
    enableSecret = getpass("  Enable Secret: ")
    output_file = input("  Enter Output JSON file: ") 
    json_data = []
    for device in devices:
        if device['model'].startswith('C9'):
            json_data.append({
                "deviceType": "IOS_XE",
                "enabled": True,
                "host": device['lanIp'],
                "name": to_canonical_name(device['name']),
                "description": "meraki",
                "terminal": {
                    "port": 22,
                    "connectionMethod": "SSH",
                    "username": sshUsername,
                    "enableSet": True,
                    "useInsecureAlgorithms": False,
                    "useTunnelingIfJumphost": True,
                    "password": sshPassword,
                    "enable": enableSecret
                }
            })
    with open(output_file, 'w') as file:
        json.dump(json_data, file, indent=4)
    click.echo(f"Devices written to {output_file}")
    
# Get devices from DNAC
def get_devices_from_dnac():
    username = input("  Enter DNAC username: ")
    dnac = api.DNACenterAPI(username=username,
                        password=getpass("  Enter DNAC password: "),
                        base_url=DNAC_URL,
                        version='2.3.5.3',
                        verify=False)

    # Get all devices with Software Type 'IOS-XE'
    click.echo("Step 4 - Getting Devices...")
    devices = dnac.devices.get_device_list(softwareType='IOS-XE')
    dnac_prepare_and_write_json(devices)
    
# Prepare data from DNAC for JSON and write to file
def dnac_prepare_and_write_json(devices):
    click.echo("Step 5 - Prepare data for JSON")
    sshUsername = input("  SSH Username: ")
    sshPassword = getpass("  SSH Password: ")
    enableSecret = getpass("  Enable Secret: ")
    output_file = input("  Enter Output JSON file: ") 
    json_data = []
    for device in devices['response']:
        json_data.append({
            "deviceType": "IOS_XE",
            "enabled": True,
            "host": device['managementIpAddress'],
            "name": to_canonical_name(device['hostname']),
            "description": "dnac",
            "terminal": {
                "port": 22,
                "connectionMethod": "SSH",
                "username": sshUsername,
                "enableSet": True,
                "useInsecureAlgorithms": False,
                "useTunnelingIfJumphost": True,
                "password": sshPassword,
                "enable": enableSecret
            }
        })
    with open(output_file, 'w') as file:
        json.dump(json_data, file, indent=4)
    click.echo(f"Devices written to {output_file}")
    

# Upload devices from JSON file to RADkit service
def upload_devices_to_radkit_service_from_json():
    json_file = input("  Enter Input JSON file: ")
    devices = []
    with open(json_file, 'r') as file:
        data = json.load(file)
        for entry in data:
            terminal = NewTerminal(
                port=entry['terminal']['port'],
                connectionMethod=entry['terminal']['connectionMethod'],
                username=entry['terminal']['username'],
                enableSet=entry['terminal']['enableSet'],
                useInsecureAlgorithms=entry['terminal']['useInsecureAlgorithms'],
                useTunnelingIfJumphost=entry['terminal']['useTunnelingIfJumphost'],
                password=entry['terminal']['password'],
                enable=entry['terminal']['enable']
            )
            device = NewDevice(
                name=to_canonical_name(entry['name']),
                host=entry['host'],
                description=entry['description'],
                deviceType=DeviceType[entry['deviceType']],
                terminal=terminal,
                enabled=entry['enabled']
            )
            devices.append(device)
    try:
        with ControlAPI.create(base_url=RADkit_URL, admin_name="superadmin", admin_password=getpass("  Enter RADkit superadmin password: ")) as service:
            print(f"Imported {len(devices)} devices from JSON file.")

            if devices:
                print("Creating devices...")
                result = service.create_devices(devices)
                if result is not None:
                    print("Successfully created devices.")
                else:
                    print("No devices created.")
            else:
                print("No devices imported from JSON.")
    except Exception as e:
        print(f"Error while connecting to RADkit service or creating devices: {e}")
        
# Upload devices from CSV file to RADkit service
def upload_devices_to_radkit_service_from_csv():
    csv_file = input("  Enter Input CSV file: ")
    devices = []
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            terminal = NewTerminal(
                username=row['terminal.username'],
                enableSet=row['terminal.enableSet'],
                password=row['terminal.password'],
                enable=row['terminal.enable']
            )
            device = NewDevice(
                name=to_canonical_name(row['name(mandatory)']),
                host=row['host(mandatory)'],
                deviceType=DeviceType[row['deviceType(mandatory)']],
                terminal=terminal,
                enabled=row['enabled']
            )
            devices.append(device)
    try:
        with ControlAPI.create(base_url=RADkit_URL, admin_name="superadmin", admin_password=getpass("  Enter RADkit superadmin password: ")) as service:
            print(f"Imported {len(devices)} devices from CSV file.")

            if devices:
                print("Creating devices...")
                result = service.create_devices(devices)
                if result is not None:
                    print("Successfully created devices.")
                else:
                    print("No devices created.")
            else:
                print("No devices imported from CSV.")
    except Exception as e:
        print(f"Error while connecting to RADkit service or creating devices: {e}")

def get_organization_switch_ports(dashboard, organization_id, network_id):
    response = dashboard.switch.getOrganizationSwitchPortsBySwitch(organization_id, networkIds=network_id, total_pages='all')
    return response


def create_yaml(json_data, output_dir):
    # Construct filename with device name
    hostname = json_data['name']
    filename = os.path.join(output_dir, f"{hostname.lower()}.yaml")

    # Initialize YAML structure
    yaml_data = []

    # Iterate over ports in JSON data
    for port in json_data['ports']:
        interface_name = port['name']
        description = None

        # Check if the interface name is not None and contains a "-"
        if interface_name:
            if '-' in interface_name:
                interface_name, description = interface_name.split('-', 1)
                interface_name = interface_name.strip()
                description = description.strip()

        # Skip if interface_name is None after processing
        if interface_name is None:
            continue

        port_dict = {
            'interface': {
                'name': canonical_interface_name(interface_name),
                'description': description,
                'enabled': port['enabled'],
                'mode': port['type']
            }
        }

        # Check port mode
        if port['type'] == 'trunk':
            port_dict['interface']['trunk'] = {
                'allowed_vlans': port['allowedVlans'],
                'native_vlan': port['vlan']
            }
        elif port['type'] == 'access':
            port_dict['interface']['access'] = {
                'vlan': port['vlan']
            }
            if port['voiceVlan'] is not None:
                port_dict['interface']['voice'] = {
                    'vlan': port['voiceVlan']
                }

        # Append port_dict to yaml_data list
        yaml_data.append(port_dict)

    # Generate YAML output
    output = yaml.dump({'system': [{'device_name': json_data['name']}], 'interfaces': yaml_data}, default_flow_style=False, sort_keys=False)

    # Write YAML output to file
    with open(filename, 'w') as yaml_file:
        yaml_file.write(output)
    click.echo(f"Device configuration written to {filename}")


@click.command()
@click.option('--output_dir', default='../ansible/device_vars', help='Output directory for YAML files')
def main(output_dir):
    print("Welcome to the RADkit Devices Tool")
    print("----------------------------------")
    while True:
        click.echo("Choose an action:")
        click.echo("  a) Get devices from Meraki Dashboard and write to JSON file")
        click.echo("  b) Get devices from Catalyst Center and write to JSON file")
        click.echo("  c) Upload devices to RADkit service from JSON file")
        click.echo("  d) Upload devices to RADkit service from CSV file")
        click.echo("  e) Get VLAN list per device from Meraki Dashboard and write to YAML file(s)")
        click.echo("  x) Exit")
        choice = click.prompt("Enter your choice (a - e, or x)")

        if choice == 'a':
            # Option to get devices from Meraki Dashboard and write to JSON file
            dashboard, org_id, network_id = get_network_id_from_meraki()
            devices = get_devices_from_meraki(dashboard, network_id)
            meraki_prepare_and_write_json(devices)
       
        elif choice == 'b':
            # Option to get devices from DNAC and write to JSON file
            get_devices_from_dnac()            

        elif choice == 'c':
            # Option to upload devices from JSON file
            upload_devices_to_radkit_service_from_json()

        elif choice == 'd':
            # Option to upload devices from CSV file
            upload_devices_to_radkit_service_from_csv()

        elif choice == 'e':
            # Option to get VLAN list per device from Meraki Dashboard and write to YAML file(s)
            dashboard, org_id, network_id = get_network_id_from_meraki()
            devices = get_organization_switch_ports(dashboard, org_id, network_id)
            for device in devices:
                create_yaml(device, output_dir)

        elif choice == 'x':
            # Option to exit
            break
        
        else:
            click.echo("Invalid choice. Please choose a valid option.")

        # Check if user wants to continue or exit
        continue_choice = click.prompt("Do you want to perform another action? (yes/no)")
        if continue_choice.lower() != 'yes':
            break


if __name__ == '__main__':
    main()
