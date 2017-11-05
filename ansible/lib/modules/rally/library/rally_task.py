from ansible.module_utils.basic import *
from rally.cli.commands import task as task_cli
from rally.exceptions import RallyException
from rally.exceptions import DeploymentNotFound
from rally import api as rally_api

DOCUMENTATION = '''
---
module: rally
short_description: Executes rally commands

'''

taskCommand = task_cli.TaskCommands()
api = rally_api.API()

def create_task(data=None):
    meta = {"response" :  "hello"}
    return False, False, meta, error_msg

def start_task(data=None):
    """Start a task based on the scenario file"""

    scenario_file = data.get('scenario_file')
    deployment = data.get('deployment')
    try:
        taskCommand.start(api, scenario_file, deployment=deployment, task_args=None,
                       task_args_file=None,
                       tags=None, do_use=False, abort_on_sla_failure=False)
    except DeploymentNotFound as error_msg:
        pass
    except RallyException as error_msg:

        is_error = True

    meta = {"response" :  "hello"}
    return is_error, False, meta, error_msg

def delete_task(data=None):
    taskCommand.delete(api)

    meta = {"response" :  "hello"}
    is_error = False
    return is_error, False, meta, error_msg

def list_task(data=None):
   meta = {"response" :  "hello"}
   return False, False, meta, error_msg

def main():
    module_args = {
                   "name": { type: "str", "required": True },
                   "command": {"choices" : ["create", "start", "abort",
                                  "delete", "check", "list", "recreate"] ,
                               type: "str", "require": True },
                   "scenario_file": { type: "str", "required": True },
                   "deployment": { type: "str", "required": True }
                  }
    choice_map = {
                    "start" : start_task,
                    "delete": delete_task,
                    "create": create_task
                 }
    module = AnsibleModule(argument_spec=module_args)

    is_error, has_changed, result, error_msg = choice_map.get(module.params['command'] )(module.params)

    if not is_error:
        module.exit_json(changed=False, meta=result)
    else:
        module.fail_json(msg=error_msg, meta = result)

if __name__ == "__main__":
    main()
