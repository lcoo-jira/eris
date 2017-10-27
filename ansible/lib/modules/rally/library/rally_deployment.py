from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: rally
short_description: Executes rally commands

'''
def create_deployment(data=None):
    meta = {"response" :  "hello"}
    return False, False, meta

def destroy_deployment(data=None):
    meta = {"response" :  "hello"}
    return False, False, meta

def main():
    module_args = { "name" : { type: "str", "required": True }, 
                    "command" : {
                                "required": True,
                                type: "str",
                                "choices" : ["create", "destroy", "check", "list", "recreate"],
                               },
                    "from" : {"requred": True, type: "str", "choices": ["file", "env"]}
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
