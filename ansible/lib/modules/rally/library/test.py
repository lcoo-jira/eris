from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: rally
short_description: Executes rally commands

'''
def main():
    fields = {
          "scenario_file" : {"required": True, "type": "str"},
          "scenario_args" : {"required" : False, "type": "str"},
	   
	}
    commands = {'create_db', 'create_deployment', 'check_deployment', 'start_task' , 'task_report' }
    module = AnsibleModule(argument_spec={})
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

