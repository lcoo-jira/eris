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
    """Create deployment from file or enviroment variables"""
    try:
        deploymentCommand.create(api, "name", fromenv=False, filename=None,
                                 do_use=False)

    except Exception as e:
        pass
    #deployment source
    deployment_source = data.get('from')


    meta = {"response" : deployment_source }
    return False, False, meta

def destroy_deployment(data=None):
    """Destroy deployment from file or enviroment variables"""
    try:
        deploymentCommand.destroy()
    except Exception as e:
        pass

    meta = {"response" :  "hello"}
    return False, False, meta

def main():
    module_args = { "name" : { type: "str", "required": True },
                    "command" : {
                                "required": True,
                                type: "str",
                                "choices" : ["create", "destroy", "check", "list", "recreate"],
                               },
                    "from" : {"requred": True, type: 'dict'}
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
