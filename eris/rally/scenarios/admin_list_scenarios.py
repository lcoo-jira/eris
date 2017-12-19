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

from rally.plugins.openstack import scenario
from rally.task import atomic


@scenario.configure(name="ErisRallyScenarios.admin_list_load")
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

    def run(self):
        self._list_tenants()
        self._list_users()
        self._list_volumes()
        self._list_networks()
        self._list_servers()
        self._list_flavors()
        self._list_images()
        self._list_stacks()
        self._list_containers()
