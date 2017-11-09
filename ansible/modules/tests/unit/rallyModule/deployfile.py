import sys
print(sys.path)
from rallyModule.library.rally_db import create_db

def test_deployfile():
    print ("this is test")
    assert (1 == 1)
