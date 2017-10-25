from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: rally
short_description: Executes rally commands

'''
def main():
    module_args = { 
                    "command": {"choices" : ["create", "destroy", "check", "list", "recreate"],
                                type: "str",
                                "required": True
                               }
                  }
        
    module = AnsibleModule(argument_spec=module_args)
    module.exit_json(changed=False, meta=module.params)

if __name__ == "__main__":
    main()
