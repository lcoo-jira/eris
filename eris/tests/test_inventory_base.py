import json

from eris.inventory import inventory_base

from eris.tests import base

DUMMY_INVENTORY = {
    "_meta": {
        "hostvars": {
            "some_vm1": {
                "var1": "val1",
                "var2": "val2"
            },
            "some_vm2": {
                "var1": "val1",
                "var2": "val2"
            }
        }
    },
    "group1": {
        "hosts": ["some_vm1", "some_vm2"],
        "vars": {
            "gvar1": "val1",
            "gvar2": "val2"
        },
        "children": []
    },
    "group2": {
        "hosts": [],
        "vars": {},
        "children": ["group1"]
    },
    "group3": {
        "hosts": ["some_vm1"],
        "vars": {
            "gvar1": "val1"
        },
        "children": ["group1", "group2"]
    }
}


class InventoryBaseTestCase(base.TestCase):
    def test_inventory_creation(self):
        # TEST: Happy Path
        # Simple test strategy
        # create a json of the dummy inventory
        # create a new inventory from the dummy
        # serialize it
        # check if the json strings match
        ib = inventory_base.InventoryBase()

        ib.add_host("some_vm1")
        ib.add_var_to_host("some_vm1", "var1", "val1")
        ib.add_var_to_host("some_vm1", "var2", "val2")

        ib.add_host("some_vm2")
        ib.add_var_to_host("some_vm2", "var1", "val1")
        ib.add_var_to_host("some_vm2", "var2", "val2")

        ib.add_group("group1")
        ib.add_group("group2")
        ib.add_group("group3")

        ib.add_host_to_group("group1", "some_vm1")
        ib.add_host_to_group("group1", "some_vm2")
        ib.add_var_to_group("group1", "gvar1", "val1")
        ib.add_var_to_group("group1", "gvar2", "val2")

        ib.add_child_to_group("group2", "group1")

        ib.add_host_to_group("group3", "some_vm1")
        ib.add_var_to_group("group3", "gvar1", "val1")
        ib.add_child_to_group("group3", "group1")
        ib.add_child_to_group("group3", "group2")

        json_str = ib.serialize_to_json()
        json_dict = json.loads(json_str)

        # Get both the dicts to use the same
        # encoding for string

        dummy_str = json.dumps(DUMMY_INVENTORY)
        dummy_dict = json.loads(dummy_str)

        # FIXME
        # Grrrr!!!
        # Sometimes the hash set and list conversions
        # throw the entire list order out of whack
        # Always decode back to set when comparing
        # This is so that the tests pass, we have
        # to compare elements. If someone has python
        # voodoo to decode back into a set please fix
        self.assertEqual(json_dict['_meta'], dummy_dict['_meta'])
        jd_keys = json_dict.keys()
        dd_keys = dummy_dict.keys()
        self.assertEqual(jd_keys, dd_keys)
        for key in jd_keys:
            if key == '_meta':
                continue
            self.assertEqual(set(json_dict[key]['hosts']),
                             set(dummy_dict[key]['hosts']))
            self.assertEqual(json_dict[key]['vars'], dummy_dict[key]['vars'])
            self.assertEqual(set(json_dict[key]['children']),
                             set(dummy_dict[key]['children']))
