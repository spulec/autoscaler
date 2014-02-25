from __future__ import print_function

import readline
import sys
from docopt import docopt
from boto.ec2.blockdevicemapping import BlockDeviceType, BlockDeviceMapping

from . import (
    add_launch_config,
    edit_launch_config,
    add_auto_scaling_group,
    edit_auto_scaling_group,
)
from .core import get_config_attributes_or_defaults, get_group_attributes_or_defaults

# This makes mocking easier
get_input = raw_input


def read_input(prompt, prefill=''):
    if prefill:
        # We need to cast text since insert_text only takes strings
        prefill = unicode(prefill)
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return get_input(prompt)
    finally:
        readline.set_startup_hook()


def launch_config():
    docstring = """AutoScaler

    Usage:
        autoscaler_launch_config add <config_name>
        autoscaler_launch_config edit <config_name>

    Options:
        -h --help     Show this screen.
    """
    arguments = docopt(docstring, argv=sys.argv[1:])
    config_name = arguments['<config_name>']

    # Get current attributes or default
    attributes = get_config_attributes_or_defaults(config_name)

    # Loop through all attributes asking for input and adding to `attributes`
    new_attributes = {}
    for attr_name, attr_value in attributes.items():
        if attr_name == 'name':
            # Don't ask for name since we already have it
            continue
        if attr_name == 'security_groups':
            attr_value = ",".join(attr_value)
        if attr_name == 'instance_monitoring':
            if attr_value and attr_value.enabled == 'true':
                attr_value = 'yes'
            else:
                attr_value = 'no'
        if attr_name == 'ebs_optimized':
            if attr_value:
                attr_value = 'yes'
            else:
                attr_value = 'no'

        user_input = read_input("What {}?".format(attr_name), attr_value)

        if attr_name == 'security_groups':
            user_input = [x.strip() for x in user_input.split(",")]
        if attr_name in ['instance_monitoring', 'ebs_optimized', 'associate_public_ip_address']:
            if user_input.lower() in ['yes', 'y']:
                user_input = True
            elif user_input.lower() in ['no', 'n']:
                user_input = False
        if attr_name == 'block_device_mappings':
            if user_input:
                user_input = [_parse_block_device_mappings(user_input)]
        user_input = None if user_input == "" else user_input
        new_attributes[attr_name] = user_input

    if arguments['add']:
        add_launch_config(config_name, **new_attributes)
        print("Launch config {} created".format(config_name))
    elif arguments['edit']:
        edit_launch_config(config_name, **new_attributes)
        print("Launch config {} updated".format(config_name))


def autoscaling_group():
    docstring = """AutoScaler

    Usage:
        autoscaler_auto_scaling_group add <group_name>
        autoscaler_auto_scaling_group edit <group_name>

    Options:
        -h --help     Show this screen.
    """
    arguments = docopt(docstring, argv=sys.argv[1:])
    group_name = arguments['<group_name>']

    # Get current attributes or default
    attributes = get_group_attributes_or_defaults(group_name)

    # Loop through all attributes asking for input and adding to `attributes`
    new_attributes = {}
    for attr_name, attr_value in attributes.items():
        if attr_name == 'availability_zones':
            attr_value = ",".join(attr_value)
        user_input = read_input("What {}?".format(attr_name), attr_value)
        if attr_name == 'availability_zones':
            user_input = [x.strip() for x in user_input.split(",")]
        if attr_name == 'default_cooldown':
            user_input = int(user_input)
        user_input = None if user_input == "" else user_input
        new_attributes[attr_name] = user_input

    if arguments['add']:
        add_auto_scaling_group(group_name, **new_attributes)
        print("AutoScaling group {} created".format(group_name))
    elif arguments['edit']:
        edit_auto_scaling_group(group_name, **new_attributes)
        print("AutoScaling group {} updated".format(group_name))

def _parse_block_device_mappings(user_input):
    """
    Parse block device mappings per AWS CLI tools syntax (modified to add IOPS)

    http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html

    Syntax:
    /dev/xvd[a-z]=[snapshot-id|ephemeral]:[size in GB]:[Delete on Term]:[IOPS]
    - Leave inapplicable fields blank
    - Delete on Termination defaults to True
    - IOPS limits are not validated
    - EBS sizing is not validated

    Mount an Ephemeral Drive:
    /dev/xvdb1=ephemeral0

    Mount multiple Ephemeral Drives:
    /dev/xvdb1=ephemeral0,/dev/xvdb2=ephemeral1

    Mount a Snapshot:
    /dev/xvdp=snap-1234abcd

    Mount a Snapshot to a 100GB drive:
    /dev/xvdp=snap-1234abcd:100

    Mount a Snapshot to a 100GB drive and do not delete on termination:
    /dev/xvdp=snap-1234abcd:100:false

    Mount a Fresh 100GB EBS device
    /dev/xvdp=:100

    Mount a Fresh 100GB EBS Device and do not delete on termination:
    /dev/xvdp=:100:false

    Mount a Fresh 100GB EBS Device with 1000 IOPS
    /dev/xvdp=:100::1000
    """
    block_device_map = BlockDeviceMapping()
    mappings = user_input.split(",")
    for mapping in mappings:
        block_type = BlockDeviceType()
        mount_point, drive_type, size, delete, iops = _parse_drive_mapping(mapping)
        if 'ephemeral' in drive_type:
            block_type.ephemeral_name = drive_type
        elif 'snap' in drive_type:
            block_type.snapshot_id = drive_type
            block_type.volume_type = "standard"
        else:
            block_type.volume_type = "standard"
        block_type.size = size
        block_type.delete_on_termination = delete

        if iops:
            block_type.iops = iops
            block_type.volume_type = "io1"

        block_device_map[mount_point] = block_type
    return block_device_map

def _parse_drive_mapping(mapping):
    mount_point, drive = mapping.split("=")
    drive_details = drive.split(":")

    drive_type = safe_list_get(drive_details, 0, '')
    size = safe_list_get(drive_details, 1, None)
    delete = safe_list_get(drive_details, 2, "true")
    iops = safe_list_get(drive_details, 3, None)

    if size:
        size = int(size)
    else:
        size = None

    if delete.lower() == 'false':
        delete = False
    else:
        delete = True

    if iops:
        iops = int(iops)
    else:
        iops = None

    return mount_point, drive_type, size, delete, iops


def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default
