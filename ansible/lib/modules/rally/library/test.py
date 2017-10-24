from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: rally
short_description: Executes rally commands

'''
def main():
    module_args = dict(
        command=dict(type='str', required=True),
        command_args=dict(type='dict', required=True)
    )

    commands = {'db_create', 'create_deployment', 'check_deployment', 'start_task' , 'task_report' 'db_recreate' , 
	        'create_task_uuid'}
    module = AnsibleModule(argument_spec=module_args)

    response = {"hello": "world"}
    module.exit_json(changed=False, meta=response)
def create_db:
	pass

def create_deployment:
	pass

def check_deployment:
	pass

def start_task:
	pass

def task_report:
	pass

	
if __name__ == '__main__':
    # CALL Rally loader
    # TODO
    main()

