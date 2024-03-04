# Cisco RADKit Device Provisioning and VLAN Configuration Tool

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/pamosima/RADkit-tools)

The "Cisco RADKit Device Provisioning and VLAN Configuration Tool" automates device provisioning tasks and VLAN configuration for Cisco Catalyst switches using Cisco RADKit, streamlining network management processes.

## Use Case Description

This tool simplifies the process of automating device provisioning and VLAN configuration for Cisco Catalyst switches, enhancing network management efficiency. By leveraging Ansible playbooks, it offers a seamless solution to modify VLAN configurations for Catalyst Switches monitored in the Meraki Dashboard. With the integrated RADKit service, it's possible to execute the Ansible Playbooks without the need to be on the same network as the devices.

![Modify VLAN's with Cloud Monitoring for Catalyst](img/MerakiRADKitDemo.gif)

The tool consists of two components:

### [Python Click Application](#python-click-application)

This component retrieves devices from the Meraki Dashboard and transfers them to the RADKit service, along with retrieving the current VLAN configuration.

### [Ansible Playbooks](#ansible-playbooks)

These playbooks facilitate the configuration of devices through the RADKit service.

## Installation

To install and configure the project:

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Install Python binary packages of RADKit. Please visit the [downloads area](https://radkit.cisco.com/downloads/release/) and get the RADKit wheels archive for your system. This packages can be installed using the pip command. For more details visit [radkit.cisco.com](https://radkit.cisco.com/docs/pages/start_pip_wheels.html)
4. Configure environment variables:
   ```
   export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$(echo -n '' | base64)
   export RADKIT_ANSIBLE_IDENTITY=""
   export RADKIT_ANSIBLE_SERVICE_SERIAL=""
   ```
   Optionally, you can set the environment variable MERAKI_API_KEY to provide your Meraki Dashboard API key:
   ```
   export MERAKI_API_KEY=""
   ```
   > **NOTE**
   > If this variable is not set or is empty, you will be prompted to enter the API key when initializing the Meraki Dashboard API.
5. Install RADKit Service based the follwing guide: https://radkit.cisco.com/docs/pages/start_installer.html
6. Installation of ansible collectionis done with ansible-galaxy using the provided .tar.gz file where X.Y.Z is the ansible collection version (ex. 0.5.0).:
   ```
   ansible-galaxy collection install ansible-cisco-radkit-X.Y.Z.tar.gz --force
   ```

## Configuration

The tool is configurable through environment variables, allowing users to specify RADKit authentication details and Ansible configuration.
Fore more details check https://radkit.cisco.com/

## Usage

### Python Click application

The Python Click application is located in the python subfolder:

To use the Python Click application:

```
cd python
python radkit-device-tool.py
```

### Options

#### `a`: Get devices from Meraki Dashboard and write to JSON file

This option retrieves devices from the Meraki Dashboard and saves the information in a JSON file. This file can be used to upload the devices to the RADKit service. You will be prompted to enter the Meraki API key and select your Meraki organization and network.

#### `b`: Get devices from Catalyst Center and write to JSON file

This option fetches devices from the Catalyst Center and stores the data in a JSON file. This file can be used to upload the devices to the RADKit service. You will be prompted to enter your Catalyst Center credentials.

#### `c`: Upload devices to RADKit service from JSON file

Use this option to upload devices to the RADKit service from a JSON file. The JSON file can be created from the Meraki Dashboard or Catalyst Center. You will be prompted to enter your RADKit superadmin password.

#### `d`: Upload devices to RADKit service from CSV file

With this option, you can upload devices to the RADKit service from a CSV file (e.g., `devices_example.csv`). You will be prompted to enter your RADKit superadmin password.

#### `e`: Get VLAN list per device from Meraki Dashboard and write to YAML file(s)

This option retrieves the VLAN list per device from the Meraki Dashboard and saves it in a YAML file per device. These YAML file(s) can be used as device variables to change L2 interface configurations with the Ansible Playbook `l2_interface_config-playbook.yml`.

### Ansible Playbooks

The Ansible Playbooks are located in the ansible subfolder.

#### RADKit Inventory Plugin

The cisco.radkit.radkit inventory plugin allows you to create a dynamic inventory from a remote RADKit service.

```
ansible-inventory -i radkit_devices.yml --list --yaml
```

#### RADKit Connection Plugin

The connection Plugin allow you to utilize existing Ansible modules, but connect through RADKIT instead of directly via SSH. With connection the plugin, credentials to devices are stored on the remote RADKit service.

#### Show Version Playbook

This Playbook is using the RADKit Plugins and does a "show version".

```
ansible-playbook -i radkit_devices.yml show_version-playbook.yml --limit radkit_device_type_IOS_XE
```

#### L2 Interface Configuration Playbook

This Playbook is using the RADKit Plugins and configures the L2 interfaces of a Catalyst Switch based on the device variable YAML file which can be created by the python click application.

```
ansible-playbook -i radkit_devices.yml l2_interface_config-playbook.yml
```

#### VLAN Configuration Playbook

This Playbook is using the RADKit Plugins and configures VLAN(s) on Catalyst Switches based on vars/vlans.yaml.

```
ansible-playbook -i radkit_devices.yml vlan_config-playbook.yml
```

## Known issues

Currently, there are no known issues. Please report any bugs or problems using the GitHub Issues section.

## Getting help

If you encounter any issues or need assistance, please create an issue in the GitHub repository for support.

## Getting involved

Contributions to this project are welcome! Please refer to the [CONTRIBUTING](./CONTRIBUTING.md) guidelines for instructions on how to contribute.

## Author(s)

This project was written and is maintained by the following individuals:

- Patrick Mosimann <pamosima@cisco.com>
