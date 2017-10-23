from ansible.module_utils.basic import *

def main():
    fields = {
          "scenario_file" : {"required": True, "type": "str"},
          "scenario_args" : {"required" : False, "type": "str"},
	   
	}
    commands = {'create_db', 'create_deployment', 'check_deployment', 'start_task' }
    module = AnsibleModule(argument_spec={})
    response = {"hello": "world"}
    module.exit_json(changed=False, meta=response)
    
if __name__ == '__main__':
    main()

