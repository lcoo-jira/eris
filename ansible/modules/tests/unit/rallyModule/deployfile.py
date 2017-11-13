import os.path
import mock

from modules.rallyModule.library.rally_db import create_db

def test_deployfile_exists():
    """Test if deployment file exists"""
    print ("this is test")
    assert (os.path.exists("/tmp/openrc.json"))

def test_db_created():
    pass

def test_credential_file_exists():
    pass
