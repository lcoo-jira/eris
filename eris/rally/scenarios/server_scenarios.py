
import jsonschema

from rally.common import logging
from rally import consts
from rally import exceptions as rally_exceptions
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.cinder import utils as cinder_utils
from rally.plugins.openstack.scenarios.neutron import utils as neutron_utils
from rally.plugins.openstack.scenarios.nova import utils
from rally.plugins.openstack.wrappers import network as network_wrapper
from rally.task import types
from rally.task import validation


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"},
               to_flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA,
                                               consts.Service.CINDER])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(
    context={"cleanup@openstack": ["cinder", "nova"]},
    name="ErisRallyScenarios.nova_cinder_neutron_load",
    platform="openstack")
class BootServerAttachCreatedVolumeAndReboot(utils.NovaScenario,
                                             cinder_utils.CinderBasic):

    def run(self, image, flavor, volume_size, min_sleep=0,
            max_sleep=0, force_delete=False, do_delete=True, hard_reboot=False,
            boot_server_kwargs=None, create_volume_kwargs=None):

        # NOTE: This is basically a fairly shameless copy of the rally
        # scenario. The scenario needs to be expanded further to do
        # a create network, create subnet along with delete network
        # per scenario. Essentially the entire scenario will be
        #
        """Create a VM from image, attach a volume to it and reboot.

        Simple test to create a VM and attach a volume, then resize the VM,
        detach the volume then delete volume and VM.
        Optional 'min_sleep' and 'max_sleep' parameters allow the scenario
        to simulate a pause between attaching a volume and running resize
        (of random duration from range [min_sleep, max_sleep]).
        :param image: Glance image name to use for the VM
        :param flavor: VM flavor name
        :param to_flavor: flavor to be used to resize the booted instance
        :param volume_size: volume size (in GB)
        :param min_sleep: Minimum sleep time in seconds (non-negative)
        :param max_sleep: Maximum sleep time in seconds (non-negative)
        :param force_delete: True if force_delete should be used
        :param do_delete: True if resources needs to be deleted explicitly
                        else use rally cleanup to remove resources
        :param boot_server_kwargs: optional arguments for VM creation
        :param create_volume_kwargs: optional arguments for volume creation
        """
        boot_server_kwargs = boot_server_kwargs or {}
        create_volume_kwargs = create_volume_kwargs or {}

        server = self._boot_server(image, flavor, **boot_server_kwargs)
        volume = self.cinder.create_volume(volume_size, **create_volume_kwargs)

        self._attach_volume(server, volume)
        self.sleep_between(min_sleep, max_sleep)
        if hard_reboot:
            self._reboot_server(server)
        else:
            self._soft_reboot_server(server)

        if do_delete:
            self._detach_volume(server, volume)
            self.cinder.delete_volume(volume)
            self._delete_server(server, force=force_delete)