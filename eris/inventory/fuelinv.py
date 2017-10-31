
import json
import subprocess
import os

from eris.inventory import fileinv


class ErisAnsibleInventory(fileinv.ErisAnsibleInventory):

    def __init__(self, eris_config):
        """
        Constructor - create the Eris Fuel Ansible Inventory
        """
        super(ErisAnsibleInventory, self).__init__(eris_config)

    def _load_deployment_map(self):
        """
        Override the load deployment map from
        fileinv.ErisAnsibleInventory.
        """

        # 1. Get the fuel node list from fuel
        # 2. Convert that to a file list
        # Use regular file processing to handle

        fuel_node_list = self._get_fuel_node_list()
        deployment_map = self._convert_fuel_to_file_inv(fuel_node_list)

        return deployment_map

    def _get_fuel_node_list(self):
        """
        Get the fuel node list from the fuel server.

        :returns: The list of fuel nodes
        :rtype: list
        :raises subprocess.CalledProcessError: if there are issues \
                calling the subprocess ssh
        :raises ValueError: if the JSON cannot be parsed or if a fuel \
                node is not provided in the config
        :raises TypeError: if the JSON cannot be parsed
        """

        # Create initial fuel inventory file as an ini file in /tmp
        # Use ansible to retrieve the inventory via the raw module
        # ignore the first and last lines of the ansible output
        # the rest is the fuel json

        try:
            fuel_config = self.eris_config['openstack_deployment']['fuel']
            fuel_ansible_ssh = fuel_config['ansible_ssh_variables']
            fuel_inv_str = 'fuel_host '
            fuel_inv_str += 'ansible_host=' + fuel_config['ip'] + ' '
            for fuel_ansible_var, fuel_ansible_val in fuel_ansible_ssh.iteritems():
                quoted_val = fuel_ansible_val
                if fuel_ansible_val.rfind(' ') >= 0:
                    quoted_val = "'" + fuel_ansible_val + "'"
                fuel_inv_str += fuel_ansible_var + '=' + quoted_val + ' '

            fid = open('/tmp/eris_fuel.ini', 'w')
            fid.write(fuel_inv_str)
            fid.close()

            ansible_command = ['ansible',
                               'fuel_host',
                               '-i',
                               '/tmp/eris_fuel.ini',
                               '-m',
                               'raw',
                               '-a',
                               'fuel node list --json']
            command_output = subprocess.check_output(ansible_command)

            # Output is in the following format
            # <Ansible output><json list><Ansible output>\n\n
            # Format the output lines into a valid JSON
            output_lines = command_output.split('\n')

            # Pop all text until we hit the beginning of the json list
            while (output_lines is not None and
                    len(output_lines) > 1 and
                    output_lines[0].strip() != '['):
                output_lines.pop(0)

            # Pop all text from the end until we hit thie end of the json list
            while (output_lines is not None and
                    len(output_lines) > 1 and
                    output_lines[len(output_lines) - 1].strip() != ']'):
                output_lines.pop(len(output_lines) - 1)

            json_str = '\n'.join(output_lines)

            node_list = json.loads(json_str)
            return node_list
        finally:
            try:
                os.remove('/tmp/eris_fuel.ini')
            except:
                pass
            finally:
                pass

    def _convert_fuel_to_file_inv(self, fuel_node_list):
        """
        Take a fuel node list in json/list from the ssh/ansible call
        and convert it into a spec that is good for the file list.
        That way all the fileinv operations can be reused for
        fuelinv

        :param fuel_node_list: A list of fuel managed nodes
        :type fuel_node_list: list
        :returns: A list of nodes in fileinv specification
        :rtype: list
        """

        new_node_list = list()
        for node in fuel_node_list:
            # Pop values we don't need
            if node['status'] == 'discover' or node['online'] is False:
                continue

            node.pop('status')
            node.pop('cluster')
            node.pop('online')
            node.pop('group_id')
            node.pop('id')
            node.pop('pending_roles')

            group_list = node.pop('roles')
            groups = group_list.split(',')
            group_list = [group.strip() for group in groups]
            node['groups'] = group_list
            new_node_list.append(node)

        # Finally add the fuel node in
        fuel_node_config = self.eris_config['openstack_deployment']['fuel']
        fuel_node = dict(name='fuel',
                         groups=['grpfuel', ],
                         ip=fuel_node_config['ip'],
                         mac=fuel_node_config['mac'],
                         ansible_ssh_variables=fuel_node_config['ansible_ssh_variables'])
        new_node_list.append(fuel_node)

        return new_node_list
