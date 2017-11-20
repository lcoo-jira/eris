#! /usr/bin/env python

from ansible.module_utils.basic import *
from rally.cli.commands import task as task_cli
from rally.exceptions import RallyException
from rally.exceptions import DeploymentNotFound
from rally import api as rally_api
from rally.exceptions import TaskNotFound

DOCUMENTATION = '''
---
module: rally
short_description: Executes rally commands

'''
taskCommand = task_cli.TaskCommands()
api = rally_api.API()

def create_task(data=None):
    error_msg = ""
    is_error = False
    has_changed = False
    meta = {}
    ansible_facts = {}
    """Create a task to get the UUID"""
    #Get deployment name
    deployment = data.get('deployment')

    #Create task API
    task_api = rally_api._Task(api)

    #Create task object and get UUID
    try:
        task_object = task_api.create(deployment)
        task_uuid = task_object.get('uuid')
        meta ['uuid'] = task_uuid
        ansible_facts = {"task_uuid" : task_uuid}

    except Exception as e:
        error_msg = e
        is_error = True

    return is_error, has_changed, meta, error_msg, ansible_facts


def start_task(data=None):
    """Start a pre created task using the UUID"""

    scenario_file = data.get('scenario_file')
    #Get deployment name
    deployment = data.get('deployment')
    task_uuid = data.get('task_uuid')
    error_msg = ""
    is_error = False
    has_changed = False
    meta = {}
    ansible_facts = {}
    #Load scenario_file
    scenaro_config = taskCommand._load_and_validate_task(api, scenario_file)

    #Create task API
    task_api = rally_api._Task(api)
    #Start task
    try:
        task_run = task_api.start(deployment, scenaro_config, task_uuid, abort_on_sla_failure=False)
        has_changed = True
    except TaskNotFound as e:
        error_msg = e
        is_error = True
    except Exception as e:
        error_msg = e
        is_error = True

    return is_error, has_changed, meta, error_msg, ansible_facts

"""
def start_task(data=None):
    Start a task based on the scenario file

    error_msg = ""
    scenario_file = data.get('scenario_file')
    deployment = data.get('deployment')
    is_error = False
    has_changed = False
    try:
        taskCommand.start(api, scenario_file, deployment=deployment, task_args=None,
                       task_args_file=None,
                       tags=None, do_use=False, abort_on_sla_failure=False)
        has_changed = True
    except DeploymentNotFound as e:
        error_msg = e
        is_error = True
    except RallyException as e:
        error_msg = e
        is_error = True

    meta = {}
    return is_error, has_changed, meta, error_msg, ansible_facts """

def delete_task(data=None):
    """ Delete rally task """
    error_msg = ""
    is_error = False
    has_changed = False
    meta = {}
    ansible_facts = {}
    try:
        taskCommand.delete(api, task_id=None, force=False)
        has_changed = True
    except RallyException as e:
        error_msg = e
        is_error = True
    return is_error, has_changed, meta, error_msg, ansible_facts

def list_task(data=None):
    """ List tasks """
    error_msg = ""
    is_error = False
    has_changed = False
    meta = {}
    ansible_facts = {}
    try:
        taskCommand.list(api, task_id=None, force=False)
        has_changed = True
    except RallyException as e:
        error_msg = e
        is_error = True
    return is_error, has_changed, meta, error_msg, ansible_facts

def main():
    module_args = {
                   "name": { type: "str", "required": True },
                   "command": {"choices" : ["create", "start", "abort",
                                  "delete", "check", "list", "recreate"] ,
                               type: "str", "require": True },
                   "scenario_file": { type: "str", "required": True },
                   "deployment": { type: "str", "required": True },
                   "task_uuid": { type: "str", "required": False }
                  }
    choice_map = {
                    "start" : start_task,
                    "delete": delete_task,
                    "create": create_task
                 }
    module = AnsibleModule(argument_spec=module_args)

    is_error, has_changed, result, error_msg, ansible_facts = choice_map.get(module.params['command'] )(module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result, ansible_facts=ansible_facts)
    else:
        module.fail_json(msg=error_msg, meta=result, ansible_facts=ansible_facts )

if __name__ == "__main__":
    main()
