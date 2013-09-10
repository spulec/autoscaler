import copy

from collections import OrderedDict
import boto
from boto.ec2.autoscale.group import AutoScalingGroup
from boto.ec2.autoscale.launchconfig import LaunchConfiguration

from .exceptions import AutoScalerException

DEFAULT_CONFIG_NAME = 'autoscaler_default'
launch_config_attrs = [
    "image_id", "key_name", "security_groups", "user_data", "instance_type",
    "kernel_id", "ramdisk_id", "block_device_mappings", "instance_monitoring",
    "instance_profile_name", "spot_price", "ebs_optimized",
]
empty_launch_config_attrs = OrderedDict()
for attr_name in launch_config_attrs:
    empty_launch_config_attrs[attr_name] = ""

autoscaling_group_attrs = [
    "availability_zones", "default_cooldown", "desired_capacity",
    "health_check_period", "health_check_type", "launch_config_name",
    "load_balancers", "max_size", "min_size", "placement_group",
    "vpc_zone_identifier", "termination_policies"
]
empty_group_attrs = OrderedDict()
for attr_name in autoscaling_group_attrs:
    if attr_name == 'launch_config_name':
        # The param is 'launch_config' while the attribute is 'launch_config_name'
        attr_name = 'launch_config'
    empty_group_attrs[attr_name] = ""


def update_all_groups(old_name, new_name):
    conn = boto.connect_autoscale()
    for group in conn.get_all_groups():
        if group.launch_config_name == old_name:
            group.launch_config_name = new_name
            group.update()


def attrs_from_config(config):
    default_attrs = OrderedDict()
    for attr in launch_config_attrs:
        default_attrs[attr] = getattr(config, attr)
    return default_attrs


def get_config_attributes_or_defaults(config_name):
    # Get current attributes or default
    attributes = get_config_values(config_name)
    if not any(attributes.values()):
        attributes = get_config_values(DEFAULT_CONFIG_NAME)
    return attributes


def get_config_values(name):
    conn = boto.connect_autoscale()
    default_configs = conn.get_all_launch_configurations(names=[name])
    if not default_configs:
        return copy.deepcopy(empty_launch_config_attrs)
    return attrs_from_config(default_configs[0])


def add_launch_config(name, base=DEFAULT_CONFIG_NAME, **kwargs):
    conn = boto.connect_autoscale()
    attributes = get_config_values(base)
    attributes.update(kwargs)
    attributes['name'] = name
    config = LaunchConfiguration(**attributes)
    conn.create_launch_configuration(config)
    return config


def edit_launch_config(name, **kwargs):
    conn = boto.connect_autoscale()
    configs = conn.get_all_launch_configurations(names=[name])
    if not configs:
        raise AutoScalerException("No launch configuration could be found for %s", name)
    config = configs[0]
    temp_name = "{}-autoscaler-temp".format(name)
    config_attrs = attrs_from_config(config)
    config_attrs.update(kwargs)

    # Create temp config and reassign groups to it
    add_launch_config(temp_name, **config_attrs)
    update_all_groups(name, temp_name)

    # Delete the old config
    conn.delete_launch_configuration(name)

    # Create new config with the original name and reassign groups
    new_config = add_launch_config(name, **config_attrs)
    update_all_groups(temp_name, name)

    # Delete the temp config
    conn.delete_launch_configuration(temp_name)

    return new_config


def attrs_from_group(group):
    default_attrs = OrderedDict()
    for attr in autoscaling_group_attrs:
        default_attrs[attr] = getattr(group, attr)
    return default_attrs


def get_group_attributes_or_defaults(group_name):
    conn = boto.connect_autoscale()
    groups = conn.get_all_groups(names=[group_name])
    if groups:
        return attrs_from_group(groups[0])
    else:
        return empty_group_attrs


def add_auto_scaling_group(name, **kwargs):
    conn = boto.connect_autoscale()
    kwargs['name'] = name
    config = AutoScalingGroup(**kwargs)
    conn.create_auto_scaling_group(config)
    return config


def edit_auto_scaling_group(name, **kwargs):
    conn = boto.connect_autoscale()
    groups = conn.get_all_groups(names=[name])
    if not groups:
        raise AutoScalerException("No autoscaling groups could be found for %s", name)
    group = groups[0]
    for attr_name, attr_value in kwargs.items():
        setattr(group, attr_name, attr_value)
    group.update()
