
import os
import stat
import json
import subprocess

from eris.inventory import fileinv

from eris.tests import base


class ErisFileinvTest(base.TestCase):

    def test_erisfileinv(self):

        # Read in the config file into json
        with open('eris/tests/datafiles/test_config.json','r') as fid:
            eris_config = json.load(fid)

        inv_obj = fileinv.ErisAnsibleInventory(eris_config)
        inv_obj.create_inventory()
        inv_json_str = inv_obj.serialize_to_json()
        
        # Create raw json file
        fid1 = open('/tmp/json_inv.test', 'w')
        fid1.write(inv_json_str)
        fid1.close()

        # Create inventory bash
        fid2 = open('/tmp/json_inv_echo.sh', 'w') 
        fid2.write('#! /usr/bin/env bash\n')
        fid2.write('cat /tmp/json_inv.test\n')
        fid2.close()
        
        # Make it executable
        os.chmod('/tmp/json_inv_echo.sh', stat.S_IRWXU)

        # Run ansible with a raw echo on localhost
        cmd = ['ansible', 'localhost', '-i', '/tmp/json_inv_echo.sh', '-o', '-m', 'raw', '-a', 'echo OK']
        expected_output = 'localhost | SUCCESS | rc=0 | (stdout) OK'
        actual_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        
        # Remove created files - but don't raise error
        try:
            os.remove('/tmp/json_inv_echo.sh')
            os.remove('/tmp/json_inv.test')
        except:
            pass
        finally:
            pass

        # Main assertion - Ansible checks inventory. 
        # So if we can get here with just a raw OK
        # we're good on the inventory syntax/JSON 
        # Get all the fancy newlines, etc. at the end 
        # out of the success criteria
        idx = actual_output.rindex(expected_output)
        self.assertEqual(idx, 0)

