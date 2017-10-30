#! /usr/bin/env python 

from ansible.module_utils.basic import *
import sys

from loader.rally_loader import RallyLoader

DOCUMENTATION = '''
---
module: rally DB
short_description: Executes rally commands to manage db 

'''

def create_db(data=None):
   pass

def recreate_db(data=None):
   pass

def main():
    module_args = { "name": { "required": True, type: "str" },
                    "command": { type: "str", "required": True, "choices" : ["create", "recreate"] } 
                  }
        
    module = AnsibleModule(argument_spec=module_args)
    module.exit_json(changed=False, meta=module.params)

if __name__ == "__main__":
    main()
