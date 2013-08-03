import boto
from boto.ec2.autoscale.group import AutoScalingGroup
from boto.ec2.autoscale.launchconfig import LaunchConfiguration

from .exceptions import AutoScalerException

DEFAULT_CONFIG_NAME = 'autoscaler_default'
launch_config_attrs = set([
    "image_id", "key_name", "security_groups", "user_data", "instance_type",
    "kernel_id", "ramdisk_id", "block_device_mappings", "instance_monitoring"
])

conn = boto.connect_autoscale()


def update_all_groups(old_name, new_name):
    for group in conn.get_all_groups():
        if group.launch_config_name == old_name:
            group.launch_config_name = new_name
            group.update()


def attrs_from_config(config):
    default_attrs = {}
    for attr in launch_config_attrs:
        default_attrs[attr] = getattr(config, attr)
    return default_attrs


def get_default_config_values():
    default_configs = conn.get_all_launch_configurations(names=[DEFAULT_CONFIG_NAME])
    if not default_configs:
        return {}
    return attrs_from_config(default_configs[0])


def add_launch_config(name, **kwargs):
    attributes = get_default_config_values()
    attributes.update(kwargs)
    attributes['name'] = name
    config = LaunchConfiguration(**attributes)
    conn.create_launch_configuration(config)
    return config


def edit_launch_config(name, **kwargs):
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


def add_auto_scaling_group(name, **kwargs):
    kwargs['name'] = name
    config = AutoScalingGroup(**kwargs)
    conn.create_auto_scaling_group(config)
    return config


def edit_auto_scaling_group(name, **kwargs):
    groups = conn.get_all_groups(names=[name])
    if not groups:
        raise AutoScalerException("No autoscaling groups could be found for %s", name)
    group = groups[0]
    for attr_name, attr_value in kwargs.items():
        setattr(group, attr_name, attr_value)
    group.update()
