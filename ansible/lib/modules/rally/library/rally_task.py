from ansible.module_utils.basic import *
from rally.cli.commands import task as task_cli
from rally.exceptions import RallyException


DOCUMENTATION = '''
---
module: rally
short_description: Executes rally commands

'''
taskCommand = task_cli.TaskCommands()
api = task_cli.API()

def create_task(data=None):
    pass

def start_task(data=None):
    taskCommand.start(api, task_file, deployment=None, task_args=None,
                       task_args_file=None,
                       tags=None, do_use=False, abort_on_sla_failure=False)

def delete_task(data=None):
    taskCommand.delete(api)

def list_task(data=None):
   pass

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
    
    if not is_error:
        module.exit_json(changed=False, meta=result )
    else:
        module.fail_json(msg="Error ", meta = result)

if __name__ == "__main__":
    main()
