
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

import random
import time
import os
import multiprocessing
from multiprocessing import pool
from ansible.module_utils.basic import AnsibleModule


def full_cpu(nice_value):
    # NOTE: Simple function to create a full cpu in python
    if nice_value != 0:
        os.nice(nice_value)

    while True:
        pass


def main():
    """
    Ansible arguments
    min_cpu: The minimum number of CPUs to start the burn. The min_cpu should
             at least 1. The default is 1.
    max_cpu: The maximum number of CPUs to burn. The max_cpu should be greater
             than the min cpu. The default is the number of CPUs on the system.
    duration: The total duration to sustain a max_cpu burn.
    burn_model: The model to get from min_cpu to max_cpu burn.
                at_once: Ignore the min_cpu, burn all cpu's to start with.
                exponential: Start with min_cpu and burn 2, 4, 8, ... CPUs until
                             max cpu's are burnt.
                linear: Start with min_cpu and burn 1, 2, 3, ... until max_cpu
                        are burnt.
                random: Start with min_cpu and burn a random number of CPUs
                        until max_cpus are burnt.
                constant: Start with min_cpu and increase 1 at a time until max_cpu
    interval: The wait interval between each burn when getting from min_cpu
              to max_cpu. N/A for at_once.
    nice_value: The Linux nice_value to set the burn processes. This will
                give the burn processes a higher priority. Needs root
                access if the nice_value is negative, i.e. a higher priority.
                Default is 0.
    dry_run: Checks and interval waits only, no burn. Only for testing purposes.
             Default is false.
    ignore_system_cpu: Ignore system cpu checks on max and min cpu. Only for
                       testing purposes. Valud only with dry_run.
    """

    total_cpus = multiprocessing.cpu_count()

    # NOTE: dry_run and ignore_system_cpu are for testing purposes only.
    # The functionality there could be expanded. The reason mocks are not
    # used is because the testing can be done even through playbooks.
    module = AnsibleModule(
        argument_spec=dict(
            min_cpu=dict(required=False, default=1, type='int'),
            max_cpu=dict(required=False,
                         default=total_cpus, type='int'),
            duration=dict(required=True, type='int'),
            burn_model=dict(required=False, default='at_once',
                            choices=['at_once', 'exponential', 'linear', 'random', 'constant']),
            interval=dict(required=False, default=60, type='int'),
            nice_value=dict(required=False, default=0, type='int'),
            dry_run=dict(required=False, default=False, type='bool'),
            ignore_system_cpu=dict(required=False, default=False, type='bool')
        ),
        supports_check_mode=True,
    )

    params = module.params
    min_cpu = params['min_cpu']
    max_cpu = params['max_cpu']
    duration = params['duration']
    burn_model = params['burn_model']
    interval = params['interval']
    nice_value = params['nice_value']
    dry_run = params['dry_run']
    ignore_system_cpu = params['ignore_system_cpu']

    if max_cpu > total_cpus and ignore_system_cpu is False and dry_run is True:
        module.fail_json(msg='max_cpu should be less than or equal to total cpus on the target')

    if min_cpu <= 0:
        module.fail_json(msg='min_cpu should be at least 1')

    if min_cpu > total_cpus and ignore_system_cpu is False and dry_run is True:
        module.fail_json(msg='min_cpu should be less than or equal to total cpus on the target')

    if min_cpu > max_cpu:
        module.fail_json(msg='max_cpu should be greater than or equal to min_cpu')

    if nice_value < -20 or nice_value > 19:
        module.fail_json(msg='nice_value should be between -20 and 19')

    if nice_value < 0 and os.geteuid() != 0:
        module.fail_json(msg='nice_value of less than 0 needs root access')

    # No point of a burn_model if max_cpu = min_cpu
    # Just reset the burn model to at_once
    if min_cpu == max_cpu:
        burn_model = 'at_once'

    output = dict(
        burn_sequence=list(),
        ramp_up_start=0,
        ramp_up_end=0,
        hold_start=0,
        hold_end=0,
        ramp_down_start=0,
        ramp_down_end=0)

    pool_list = list()

    if burn_model == 'at_once':
        pool_list.append((pool.Pool(max_cpu), max_cpu))
        output['burn_sequence'].append(max_cpu)
    else:
        # Use j for linear and exponential growth
        j = 0
        # Use k as a counter from min_cpu to max_cpu
        burn_cpu = min_cpu
        # Keep track of the last update to k with burn_cpu
        # Initialize to 1 so that at there is no infinite loop
        k = burn_cpu

        while k <= max_cpu:
            pool_list.append((pool.Pool(burn_cpu), burn_cpu))
            output['burn_sequence'].append(burn_cpu)

            j += 1

            if burn_model == 'exponential':
                burn_cpu = 2 ** j
            elif burn_model == 'linear':
                burn_cpu = j
            elif burn_model == 'random' and max_cpu > k:
                # NOTE: So this is a bit of a hack but it needs to be there
                # randint works only if max_cpu>k, i.e. max_cpu-k > 1
                # If max_cpu=k, we don't initialize a new burn_cpu
                # But notice that at the end k+= burn_cpu is still done
                # This is because we need to break out of the loop
                # Once that is accomplished, we can check in the
                # if statement below past the while loop. That won't be true
                # since k - burn_cpu = max_cpu.
                burn_cpu = random.randint(1, max_cpu-k)
            elif burn_model == 'constant':
                burn_cpu = 1

            k += burn_cpu

        if k - burn_cpu < max_cpu:
            # if k-burn_cpu < max_cpu then we know the last increment
            # puts it past max_cpu.
            # Reduce by the number of CPUs incremented in the last iteration
            k = k - burn_cpu
            # Get the remaining CPUs till max_cpu
            burn_cpu = max_cpu - k
            pool_list.append((pool.Pool(burn_cpu), burn_cpu))
            output['burn_sequence'].append(burn_cpu)

    # Ramp - up
    output['ramp_up_start'] = time.time()
    for p in pool_list:
        proc_args = [nice_value]*p[1]
        if dry_run is False:
            p[0].map_async(full_cpu, proc_args)
        if interval != 0:
            time.sleep(interval)
    output['ramp_up_end'] = time.time()

    # Hold
    output['hold_start'] = time.time()
    time.sleep(duration)
    output['hold_end'] = time.time()

    # Ramp - down in reverse order
    output['ramp_down_start'] = time.time()
    for p in pool_list[::-1]:
        if dry_run is False:
            p[0].terminate()
        if interval != 0:
            time.sleep(interval)
    output['ramp_down_end'] = time.time()

    module.exit_json(changed=True, stats=output)

if __name__ == '__main__':
    main()
