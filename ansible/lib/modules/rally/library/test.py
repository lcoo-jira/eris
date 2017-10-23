from ansible.module_utils.basic import *

def main():
    fields = {
          "name" : {"required": True, "type": "str"},
          "file" : {"required" : True, "type": "str"}
	}
    module = AnsibleModule(argument_spec={})
    response = {"hello": "world"}
    module.exit_json(changed=False, meta=response)
    
if __name__ == '__main__':
    main()

