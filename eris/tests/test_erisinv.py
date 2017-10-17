
import os
import subprocess
import shutil
import stat

from eris.cli import erisinv

from eris.tests import base


class ErisInventoryCLITest(base.TestCase):
    
    def setUp(self):
        super(ErisInventoryCLITest, self).setUp()
        shutil.copyfile('eris/cli/erisinv.py', '/tmp/erisinv')
        os.chmod('/tmp/erisinv', stat.S_IRWXU)

    def test_erisinventorycli(self):
        cmd = ['ansible', 'localhost', '-i', '/tmp/erisinv', '-o', '-m', 'raw', '-a', 'echo OK']
        os.putenv('ERIS_CONFIG_FILE', 'eris/tests/datafiles/test_config.json')
        expected_output = 'localhost | SUCCESS | rc=0 | (stdout) OK'
        actual_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        print actual_output
        idx = actual_output.rindex(expected_output)
        self.assertEqual(idx, 0)

    def test_erisinvcli_with_customplugin(self):
        cmd = ['ansible', 'localhost', '-i', '/tmp/erisinv', '-o', '-m', 'raw', '-a', 'echo OK']
        os.putenv('ERIS_CONFIG_FILE', 'eris/tests/datafiles/test_config_invplugin.json')
        expected_output = 'localhost | SUCCESS | rc=0 | (stdout) OK'
        actual_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        print actual_output
        idx = actual_output.rindex(expected_output)
        self.assertEqual(idx, 0)

    def test_erisinvcli_with_fuelplugin(self):
        cmd = ['ansible', 'localhost', '-i', '/tmp/erisinv', '-o', '-m', 'raw', '-a', 'echo OK']
        os.putenv('ERIS_CONFIG_FILE', 'eris/tests/datafiles/test_fuel_config.json')
        expected_output = 'localhost | SUCCESS | rc=0 | (stdout) OK'
        actual_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        print actual_output
        idx = actual_output.rindex(expected_output)
        self.assertEqual(idx, 0)



    def tearDown(self):
        super(ErisInventoryCLITest, self).tearDown()
        try:
            os.remove('/tmp/erisinv')
        except:
            pass
        finally:
            pass
