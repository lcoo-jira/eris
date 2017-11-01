from ansible.module_utils.basic import *
from rally.cli.commands import task as task_cli
from rally.exceptions import RallyException
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
    return False, False, meta

def start_task(data=None):
    try:
        taskCommand.start(api, "task_file", deployment=None, task_args=None,
                       task_args_file=None,
                       tags=None, do_use=False, abort_on_sla_failure=False)
    except RallyException as e:
        pass

    meta = {"response" :  "hello"}
    return False, False, meta

def delete_task(data=None):
    taskCommand.delete(api)

    meta = {"response" :  "hello"}
    return False, False, meta

def list_task(data=None):
   meta = {"response" :  "hello"}
   return False, False, meta

def main():
    module_args = {
                   "name": { type: "str", "required": True },
                   "command": {"choices" : ["create", "start", "abort",
                                  "delete", "check", "list", "recreate"] ,
                               type: "str", "require": True }
                  }
    choice_map = {
                    "start" : start_task,
                    "delete": delete_task
                 }
    module = AnsibleModule(argument_spec=module_args)

    is_error, has_changed, result = choice_map.get(module.params['command'] )(module.params)

    if not is_error:
        module.exit_json(changed=False, meta=result)
    else:
        module.fail_json(msg="Error ", meta = result)

if __name__ == "__main__":
    main()
