#! /usr/bin/env python

from ansible.module_utils.basic import *
from rally import api as rally_api
from rally.cli.commands.db import DBCommands

#sys.path.append('home/dola/eris/ansible/lib/modules/rally/library/loader')
#from loader.rally_loader import RallyLoader

DOCUMENTATION = '''
---
module: rally DB
short_description: Executes rally commands to manage db

'''
db = DBCommands()
api = rally_api.API()

def create_db(data=None):
    try:
        db.create(api)
    except Exception as e:
        pass
    meta = {"hello": "deji"}
    return False, False, meta

def recreate_db(data=None):
    try:
        db.recreate(api)
    except Exception as e:
        pass
    meta = {"hello": "deji"}
    return False, False, meta

def main():
    module_args = { "name": { "required": True, type: "str" },
                    "command": { type: "str", "required": True, "choices" : ["create", "recreate"] }
                  }

    choice_map = {
                        "create" : create_db,
                        "recreate": recreate_db
                     }
    module = AnsibleModule(argument_spec=module_args)

    is_error, has_changed, result = choice_map.get(module.params['command'] )(module.params)
    module.exit_json(changed=False, meta=module.params)

if __name__ == "__main__":
    main()
