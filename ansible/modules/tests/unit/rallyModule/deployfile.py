import os.path
import mock

from modules.rallyModule.library.rally_db import create_db

def test_deployfile_exists():
    """Test if deployment file exists"""
    assert (os.path.exists("/tmp/openrc.json"))

def text_task_file_exits():
    """Test if task file exists"""
    assert (os.path.exists("/tmp/create-and-delete-floating-ips.yaml"))

def test_db_created():
    pass

def test_credential_file_exists():

    pass
