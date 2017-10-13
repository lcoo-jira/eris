
import json
import os
import sys

from eris.inventory.inventory_base import ErisInventoryBase


class ErisFileInventory(ErisInventoryBase):

    def __init__(self, config_path):
        """
        Create the Eris File Inventory from various parameters
        for rally and a deployment map.
        :param eris_inv_config: The JSON for the inventory config
        :type eris_inv_config: str
        :raises ValueError: If config_path is None
        :raises IOError: If config_path cannot be read \
                or if the path is not a file
        """
        
        super(ErisFileInventory, self).__init__()
        if config_path is None:
            raise ValueError('config_path should not be None')

        if os.access(config_path, os.R_OK) is False:
            raise IOError('%s file not found' % config_path)

        if os.path.isfile(config_path) is False:
            raise IOError('%s is not a file' % config_path)

        self.config_path = config_path

    def _load_config_file(self):
        """
        Load the configuration JSON from
        the location specified in the
        constructor
        :returns: The Eris config
        :rtype: dict
        :raises IOError: If the config can't be read
        :raises ValueError: If the JSON can't be parsed
        :raises TypeError: If the JSON can't be parsed
        """

        eris_config = None
        with open(self.config_path, 'r') as fid:
            eris_config = json.load(fid)

        return eris_config

    def _load_deployment_map(self, map_loc):
        """
        Load a site deployment map. The site deployment is
        in the following configuration
        {
            "name": "host_alias",
            "groups": ["group1", "group2",...],
            "ip": "actual.ip.addr.here",
            "mac": "mac:for:the:ip:addr:here",
            "type": "vm" or "bare-metal" or "rack" or "switch" or "router"
            "bare-metal": "bare-metal-name-if-type-is-vm",
            "rack": "rack-name-if-type-is-metal"
            "ansible_ssh_variables": {
                Look at Ansible inventory documentation
                Provide these if you want to override defaults
                in the eris_inv_config
            }
        }

        :param map_loc: Fully qualified path of where \
                to find the deployment map
        :type map_loc: str
        :returns: List of dict objects
        :rtype: list
        :raises ValueError: Thrown when parsing JSON
        :raises TypeError: Thrown when parsing JSON
        :raises IOError: Thrown for error reading file
        """

        deployment_map = None
        with open(map_loc, 'r') as fid:
            deployment_map = json.load(fid)

        return deployment_map

    def create_inventory(self):
        """
        Create the entire inventory from the config
        and the deployment map.
        """

        # Load the configuration and the deployment map
        eris_config = self._load_config_file()
        dep_map_file = eris_config['openstack_deployment']['deployment_map']
        deployment_map = self._load_deployment_map(dep_map_file)

        # Add in the root group
        # Everything is a part of the root group - or the deployment
        dep_name = eris_config['openstack_deployment']['name']
        self.add_group(dep_name)

        # Add in the ssh parameters as a part of the root group
        # !!! Important !!!
        # The ssh parameters have to be Ansible inventory compliant
        # TODO: Test this
        # TODO: Refactor when aggregate modifications are implemented
        # in ErisInventoryBase
        dep_ssh = eris_config['openstack_deployment']['deployment_ssh']
        for ansible_inv_ssh_var, ansible_inv_ssh_val in dep_ssh.iteritems():
            self.add_var_to_group(dep_name,
                                  ansible_inv_ssh_var,
                                  ansible_inv_ssh_val)

        groups_and_hosts = self._add_hosts_to_inventory(deployment_map)
        group_expansion = eris_config['openstack_deployment']['groups']
        self._create_group_hierarchy(dep_name,
                                     group_expansion,
                                     groups_and_hosts)

    def _create_group_hierarchy(self, dep_name,
                                group_expansion,
                                groups_and_hosts):
        """
        Private method
        DO NOT CALL EXTERNALLY

        Create a group hierarchy and add the hosts to the inventory.

        :param dep_name: The root group
        :param group_expansion: Aggregate group expansions
        :param groups_and_hosts: Groups and hosts from deployment map
        :type dep_name: str
        :type group_expansion: dict
        :type groups_and_hosts: dict
        :returns: None
        """

        # Add in all the children from the service expansion pieces
        # These are the groups that you want to logically club
        # together
        # FIXME: Yuck - an O(n^3) algorithm. Look for efficiency
        for group, hlist in groups_and_hosts.iteritems():
            if group in group_expansion:
                # A whole bunch of processing

                group_list = group_expansion[group]

                # Add the parent group
                self.add_group(group)
                self.add_child_to_group(dep_name, group)

                # Add the group_list
                for l_group in group_list:
                    self.add_group(l_group)
                    self.add_child_to_group(group, l_group)

                    # Add all the hosts to l_group
                    for l_host in hlist:
                        self.add_host_to_group(l_group, l_host)
            else:
                # A standalong group with a bunch of hosts

                # Add in the group
                self.add_group(group)
                self.add_child_to_group(dep_name, group)

                # Then add the hosts
                for host in hlist:
                    self.add_host_to_group(group, host)

    def _add_hosts_to_inventory(self, deployment_map):
        """
        Private method
        DO NOT CALL EXTERNALLY

        Add hosts to the inventory from the deployment map

        :param deployment_map: The deployment map from the config
        :type deployment_map: list
        :returns: A dictionary of hosts and group from the deployment
        :rtype: dict
        """

        # TODO: Add code for auto creating groups for racks and bare metal
        # Process the deployment map
        groups_and_hosts = dict()
        for node in deployment_map:
            # First add to the hosts
            hostname = node['name']
            self.add_host(hostname)

            # Then keep a track of the groups and hosts
            for group in node['groups']:
                if group in groups_and_hosts:
                    groups_and_hosts[group].append(hostname)
                else:
                    groups_and_hosts[group] = list([hostname, ])

            # Then add in the ansible ssh variables
            # ip maps to ansible_host
            # mac doesn't map to anything - it's just a variable
            # The rest of the variables are in ansible_ssh_variables
            self.add_var_to_host(hostname, 'ansible_host', node['ip'])
            self.add_var_to_host(hostname, 'mac', node['mac'])
            if 'ansible_ssh_variables' in node:
                ansible_ssh_vars = node['ansible_ssh_vars']
                for ansible_ssh_var, ansible_ssh_val in ansible_ssh_vars:
                    self.add_var_to_host(hostname,
                                         ansible_ssh_var,
                                         ansible_ssh_val)

        return groups_and_hosts


# The main program for the dynamic inventory
def main():
    """
    The main function takes an argument --list
    and returns the serialized json of the ansible
    file inventory
    """

    config_file = os.getenv('ERIS_CONFIG_FILE')
    eris_file_inv = ErisFileInventory(config_file)

    eris_file_inv.create_inventory()

    json_inv = eris_file_inv.serialize_to_json()

    return json_inv


# The start of the script
if __name__ == "__main__":

    if len(sys.argv) != 2 and sys.argv[1] != '--list':
        raise ValueError('sys.argv len should be 2 with value --list')

    inv_json = main()

    print inv_json
