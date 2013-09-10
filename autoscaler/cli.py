from __future__ import print_function

import readline
import sys
from docopt import docopt

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

        user_input = read_input("What {}?".format(attr_name), attr_value)

        if attr_name == 'security_groups':
            user_input = [x.strip() for x in user_input.split(",")]
        if attr_name == 'ebs_optimized':
            if user_input.lower() in ['yes', 'y']:
                user_input = True
            elif user_input.lower() in ['no', 'n']:
                user_input = False
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
