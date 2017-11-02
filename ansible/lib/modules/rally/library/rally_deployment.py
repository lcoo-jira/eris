#! /usr/bin/env python

from ansible.module_utils.basic import *
from rally import api as rally_api
from rally.cli.commands.deployment import DeploymentCommands
from rally.exceptions import DeploymentNotFound
from rally.exceptions import RallyException

DOCUMENTATION = '''
---
module: rally
short_description: Executes rally commands

'''
api = rally_api.API()
deploymentCommand = DeploymentCommands()

def create_deployment(data=None):
    """Create deployment from RC file or enviroment variables"""
    #deployment source
    rc_file = data.get('from')
    deployment_name = data.get('name')
    try:
        deploymentCommand.create(api, deployment_name, fromenv=False, filename=rc_file,
                             do_use=False)
    except DeploymentNameExists:
        raise ("Deployment already exist")

    meta = {"env_file" : rc_file, "deployment_name":deployment_name }
    return False, False, meta

def destroy_deployment(data=None):
    """Destroy deployment from file or enviroment variables"""
    try:
        deploymentCommand.destroy(self, api, deployment=None)
    except Exception as e:
        pass

    meta = {"response" :  "hello"}
    return False, False, meta

def main():
    module_args = { "name" : {"required": True, type: "str" },
                    "command" : {
                                "required": True,
                                type: "str",
                                "choices" : ["create", "destroy", "check", "list", "recreate"],
                               },
                    "from" : {"requred": True, type: 'str'}
                  }

    choice_map = {
                    "create" : create_deployment,
                    "destroy": destroy_deployment
                 }
    module = AnsibleModule(argument_spec=module_args)
    is_error, has_changed, result = choice_map.get(module.params['command'] )(module.params)

    if not is_error:
        module.exit_json(changed=False, meta=result )
    else:
        module.fail_json(msg="Error ", meta = result)

if __name__ == "__main__":
    main()
