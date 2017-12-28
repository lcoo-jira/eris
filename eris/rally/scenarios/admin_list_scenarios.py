# Eris scenario to run the following list
# commands through an admin client in rally
# List tenants
# List users
# TODO: List hypervisors
# List volumes
# List networks
# List instances
# List flavors
# List images
# List stacks - HEAT
# List containers - SWIFT
# TODO: List objects in containers - SWIFT

import random
import collections

from rally import consts
from rally.plugins.openstack import scenario
from rally.task import atomic
from rally.task import validation
""" Rally admin task list load scenario.
The sample task file will look something like this
{
    "ErisRallyScenarios.admin_list_load": [
        {
            "args": {
                "list_tenants": True,
                "list_users": True,
                "list_volumes": True,
                "list_networks": True,
                "list_servers": True,
                "list_flavors": True,
                "list_images": True,
                "list_stacks": True,
                "list_containers": True,
                "shuffle": True
            },
            "runner": {
                "type": "constant_for_duration",
                "concurrency": 5,
                "duration": 30
            }
        }
    ]
}

To enable any of the list scenarios just set the args to true. All the
options are disabled by default. If more list functions are added in, add the enablers to the list of args
in the run method.
"""


@validation.add("required_services", services=[consts.Service.KEYSTONE,
                                               consts.Service.CINDER,
                                               consts.Service.NEUTRON,
                                               consts.Service.NOVA,
                                               consts.Service.GLANCE,
                                               consts.Service.HEAT,
                                               consts.Service.SWIFT])
@validation.add("required_platform", platform="openstack", admin=True)
@scenario.configure(name="ErisRallyScenarios.admin_list_load", platform="openstack")
class AdminListScenarios(scenario.OpenStackScenario):

    @atomic.action_timer("list_tenants")
    def _list_tenants(self):
        return self.admin_clients("keystone").projects.list()

    @atomic.action_timer("list_users")
    def _list_users(self):
        return self.admin_clients("keystone").users.list()

    @atomic.action_timer("list_volumes")
    def _list_volumes(self, detailed=True):
        return self.admin_clients("cinder").volumes.list(detailed)

    @atomic.action_timer("list_networks")
    def _list_networks(self, **kwargs):
        return self.admin_clients("neutron").list_networks(**kwargs)["networks"]

    @atomic.action_timer("list_servers")
    def _list_servers(self, detailed=True):
        return self.admin_clients("nova").servers.list(detailed)

    @atomic.action_timer("list_flavors")
    def _list_flavors(self, detailed=True, **kwargs):
        return self.admin_clients("nova").flavors.list(detailed, **kwargs)

    @atomic.action_timer("list_images")
    def _list_images(self):
        return self.admin_clients("glance").images.list()

    @atomic.action_timer("list_stacks")
    def _list_stacks(self):
        return self.admin_clients("heat").stacks.list()

    @atomic.action_timer("list_containers")
    def _list_containers(self, full_listing=True, **kwargs):
        return self.admin_clients("swift").get_account(full_listing=full_listing, **kwargs)

    def run(self, list_tenants=False, list_users=False, list_volumes=False,
            list_networks=False, list_servers=False, list_flavors=False,
            list_images=False, list_stacks=False, list_containers=False,
            shuffle=False):
        """ Run a list of admin list tasks in a randomized manner.

        Randomize the list run. This can be done by putting
        all the functions in an array and then creating a
        random permutation of that array.
        This is so that the load is more evenly distributed as
        may be expected in a real cloud as opposed to a single
        client always executing these functions in a sequential
        manner

        :param list_tenants: List all the projects
        :param list_users: List all the users
        :param list_volumes: List all the volumes
        :param list_networks: List all the networks
        :param list_servers: List all the servers
        :param list_flavors: List all the flavors
        :param list_images: List all the images
        :param list_stacks: List all the heat stacks
        :param list_containers: List all the swift containers
        :param shuffle: Randomize the run
        :returns: None
        """

        funcrun = collections.namedtuple('funcrun', ['func', 'enable'])

        function_list = [
            funcrun(func=self._list_tenants, enable=list_tenants),
            funcrun(func=self._list_users, enable=list_users),
            funcrun(func=self._list_volumes, enable=list_volumes),
            funcrun(func=self._list_networks, enable=list_networks),
            funcrun(func=self._list_servers, enable=list_servers),
            funcrun(func=self._list_flavors, enable=list_flavors),
            funcrun(func=self._list_images, enable=list_images),
            funcrun(func=self._list_stacks, enable=list_stacks),
            funcrun(func=self._list_containers, enable=list_containers)]

        functions_to_run = filter(lambda j: j.enable, function_list)
        if shuffle:
            random.shuffle(functions_to_run)
        map(lambda k: k.func(), functions_to_run)
