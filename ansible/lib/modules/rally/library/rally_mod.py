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

    module = AnsibleModule(argument_spec=module_args)

    response = {"hello": "world"}
    module.exit_json(changed=False, meta=response)

if __name__ == '__main__':
    # CALL Rally loader
    # TODO
    main()
