
import os
import json

from eris.inventory import fileinv

from eris.tests import base


DUMMY_ERIS_CONFIG = {
    "openstack_deployment": {
        "name": "sample",
        "deployment_map": "/tmp/dummy_deployment.json",
        "deployment_ssh": {
            "ansible_user": "fuel",
            "ansible_ssh_private_key_file": "/tmp/jump/sample/id_rsa",
            "ansible_ssh_common_args": "-o ProxyCommand 'something'",
        },
        "groups": {
            "controllers": ["memcached", "nova", "glance", "cinder", "heat", "ceilometer", "corosync", "pacemaker"],
            "identity": ["keystone", "memcached"],
            "contrail-control": ["neutron", "contrail-control"]
        }
    },
    "rally": {
        "type": "ExistingCloud",
        "creds": {
            "openstack": {
                "auth_url": "http://keystone.fuel.local:5000/v3/",
                "region_name": "RegionOne",
                "endpoint_type": "admin",
                "admin": {
                    "username": "admin",
                    "password": "admin",
                    "user_domain_name": "Default",
                    "project_name": "admin",
                    "project_domain_name": "Default"
                },
                "https_insecure": "true",
                "https_cacert": ""
            }
        }
    },
}

DUMMY_DEPLOYMENT_MAP = [
    {
        "name": "swiftsre103", 
        "groups": ["swift-storage",],
        "ip": "172.24.91.136", 
        "mac": "52:54:00:40:1a:41", 
        "type": "vm"
    }, 
    {
        "name": "dbngsre101", 
        "groups": ["rabbitmq", "mysql"], 
        "ip": "172.24.91.108", 
        "mac": "52:54:00:3c:45:fd", 
        "type": "vm"
    }, 
    {
        "name": "computesre103", 
        "groups": ["compute",],
        "ip": "172.24.91.103", 
        "mac": "00:25:b5:40:1b:cf", 
        "type": "bare-metal"
    }, 
    {
        "name": "contrailanalysre102", 
        "groups": ["contrail-analytics", "contrail-analytics-db"],
        "ip": "172.24.91.118", 
        "mac": "52:54:00:f5:bb:f0", 
        "type": "vm"
    }, 
    {
        "name": "haprsre102", 
        "groups": "haproxy", 
        "ip": "172.24.91.121", 
        "mac": "52:54:00:da:bf:8d", 
        "type": "vm"
    }, 
    {
        "name": "computesre102", 
        "groups": ["compute",], 
        "ip": "172.24.91.138", 
        "mac": "00:25:b5:40:1a:bf", 
        "type": "bare-metal"
    }, 
    {
        "name": "haprsre103", 
        "groups": ["haproxy",], 
        "ip": "172.24.91.132", 
        "mac": "52:54:00:eb:25:5d", 
        "type": "vm"
    }, 
    {
        "name": "contrailcntlsre102", 
        "groups": ["contrail-config", "contrail-control", "contrail-db"],
        "ip": "172.24.91.116", 
        "mac": "52:54:00:fb:ae:d3", 
        "type": "vm"
    }, 
    {
        "name": "contrailcntlsre103", 
        "groups": ["contrail-config", "contrail-control", "contrail-db"],
        "ip": "172.24.91.129", 
        "mac": "52:54:00:33:e5:45", 
        "type": "vm"
    }, 
    {
        "name": "moscsre101", 
        "groups": ["cinder-volume", "controllers", "swift-proxy"],
        "ip": "172.24.91.113", 
        "mac": "52:54:00:38:ed:c0", 
        "type": "vm"
    }, 
    {
        "name": "swiftsre101", 
        "groups": ["swift-storage",], 
        "ip": "172.24.91.115", 
        "mac": "52:54:00:8e:01:09", 
        "type": "vm"
    }, 
    {
        "name": "computesre101", 
        "groups": ["compute",], 
        "ip": "172.24.91.137", 
        "mac": "00:25:b5:40:1b:6f", 
        "type": "bare-metal"
    }, 
    {
        "name": "identitysre102", 
        "groups": ["identity",], 
        "ip": "172.24.91.122", 
        "mac": "52:54:00:d6:b7:a4", 
        "type": "vm"
    }, 
    {
        "name": "contrailanalysre103", 
        "groups": ["contrail-analytics", "contrail-analytics-db"],
        "ip": "172.24.91.128", 
        "mac": "52:54:00:fb:f6:34", 
        "type": "vm"
    }, 
    {
        "name": "moscsre102", 
        "groups": ["cinder-volume", "controllers", "swift-proxy"], 
        "ip": "172.24.91.126", 
        "mac": "52:54:00:06:8a:7f", 
        "type": "vm"
    }, 
    {
        "name": "contrailcntlsre101", 
        "groups": ["contrail-config", "contrail-control", "contrail-db"], 
        "ip": "172.24.91.107", 
        "mac": "52:54:00:bd:25:3c", 
        "type": "vm"
    }, 
    {
        "name": "dbngsre103", 
        "groups": ["rabbitmq", "mysql"],
        "ip": "172.24.91.131", 
        "mac": "52:54:00:0c:5f:4f", 
        "type": "vm"
    }, 
    {
        "name": "contrailanalysre101", 
        "groups": ["contrail-analytics", "contrail-analytics-db"], 
        "ip": "172.24.91.139", 
        "mac": "52:54:00:b3:5a:25", 
        "type": "vm"
    }, 
    {
        "name": "identitysre103", 
        "groups": ["identity",], 
        "ip": "172.24.91.133", 
        "mac": "52:54:00:87:57:7a", 
        "type": "vm"
    }, 
    {
        "name": "moscsre103", 
        "groups": ["cinder-volume", "controllers", "swift-proxy"], 
        "ip": "172.24.91.135", 
        "mac": "52:54:00:ae:f8:31", 
        "type": "vm"
    }, 
    {
        "name": "haprsre101", 
        "groups": ["haproxy",], 
        "ip": "172.24.91.110", 
        "mac": "52:54:00:46:d9:79", 
        "type": "vm"
    }, 
    {
        "name": "mongosre102", 
        "groups": ["mongo",], 
        "ip": "172.24.91.125", 
        "mac": "52:54:00:92:a4:16", 
        "type": "vm"
    }, 
    {
        "name": "mongosre103", 
        "groups": ["mongo",], 
        "ip": "172.24.91.134", 
        "mac": "52:54:00:cf:78:20", 
        "type": "vm"
    }, 
    {
        "name": "identitysre101", 
        "groups": ["identity",], 
        "ip": "172.24.91.111", 
        "mac": "52:54:00:fa:84:5e", 
        "type": "vm"
    }, 
    {
        "name": "swiftsre102", 
        "groups": ["swift-storage",], 
        "ip": "172.24.91.127", 
        "mac": "52:54:00:c0:19:8d", 
        "type": "vm"
    }, 
    {
        "name": "mongosre101", 
        "groups": ["mongo",], 
        "ip": "172.24.91.112", 
        "mac": "52:54:00:82:7d:7d", 
        "type": "vm"
    }, 
    {
        "name": "dbngsre102", 
        "groups": ["rabbitmq", "mysql"],
        "ip": "172.24.91.119", 
        "mac": "52:54:00:d4:e0:b2", 
        "type": "vm"
    }
]

class ErisFileinvTest(base.TestCase):

    def test_erisfileinv(self):
        
        with open('/tmp/dummy_config.json', 'w') as fid:
            json.dump(DUMMY_ERIS_CONFIG, fid)
        with open('/tmp/dummy_deployment.json', 'w') as fid:
            json.dump(DUMMY_DEPLOYMENT_MAP, fid)
        
        os.environ['ERIS_CONFIG_FILE']='/tmp/dummy_config.json'
        invstr = fileinv.main()

        # First pass
        # Make sure JSON is good
        invstr_dict = json.loads(invstr)

        # Second pass
        # Are all the hosts & groups in there?

        # Third pass
        # Harder!!! Does it work with Ansible?
        
        os.remove('/tmp/dummy_deployment.json')
        os.remove('/tmp/dummy_config.json')
