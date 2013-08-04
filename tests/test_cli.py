import boto
from mock import patch
from moto import mock_autoscaling
import sure  # noqa

from autoscaler import add_launch_config, add_auto_scaling_group
from autoscaler.cli import launch_config, autoscaling_group


@mock_autoscaling()
@patch('autoscaler.cli.get_input')
@patch('autoscaler.cli.sys')
def test_launch_config_add(sys, user_input):
    sys.argv = [
        'autoscaler_launch_config',
        'add',
        'web',
    ]

    # "image_id", "key_name", "security_groups", "user_data", "instance_type",
    # "kernel_id", "ramdisk_id", "block_device_mappings", "instance_monitoring"
    user_input.side_effect = [
        'ami-1234abcd',
        'the_key',
        "default,web",
        "echo 'web' > /etc/config",
        "m1.small",
        "",
        "",
        "",
        "yes",
    ]

    # Simulate CLI call
    launch_config()

    conn = boto.connect_autoscale()
    configs = conn.get_all_launch_configurations()
    configs.should.have.length_of(1)
    config = configs[0]
    config.name.should.equal("web")
    config.image_id.should.equal("ami-1234abcd")
    config.key_name.should.equal("the_key")
    set(config.security_groups).should.equal(set(["web", "default"]))
    config.user_data.should.equal("echo 'web' > /etc/config")
    config.instance_type.should.equal("m1.small")
    config.kernel_id.should.equal("")
    config.ramdisk_id.should.equal("")
    list(config.block_device_mappings).should.equal([])
    config.instance_monitoring.enabled.should.equal('true')


@mock_autoscaling()
@patch('autoscaler.cli.get_input')
@patch('autoscaler.cli.sys')
def test_launch_config_edit(sys, user_input):
    add_launch_config("web", user_data="echo 'web_machine' > /etc/config")

    sys.argv = [
        'autoscaler_launch_config',
        'edit',
        'web',
    ]

    # "image_id", "key_name", "security_groups", "user_data", "instance_type",
    # "kernel_id", "ramdisk_id", "block_device_mappings", "instance_monitoring"
    user_input.side_effect = [
        "",
        "",
        "",
        "echo 'other_machine' > /etc/config",
        "",
        "",
        "",
        "",
        "yes",
    ]

    # Simulate CLI call
    launch_config()

    conn = boto.connect_autoscale()
    configs = conn.get_all_launch_configurations(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]
    web_config.user_data.should.equal("echo 'other_machine' > /etc/config")


@mock_autoscaling()
@patch('autoscaler.cli.get_input')
@patch('autoscaler.cli.sys')
def test_autoscaling_group_add(sys, user_input):
    sys.argv = [
        'autoscaler_auto_scaling_group',
        'add',
        'web',
    ]
    # INPUTS
    # "availability_zones", "default_cooldown", "desired_capacity",
    # "health_check_period", "health_check_type", "launch_config_name",
    # "load_balancers", "max_size", "min_size", "placement_group",
    # "vpc_zone_identifier", "termination_policies"
    user_input.side_effect = [
        'us-east-1b,us-east-1c',
        '60',
        "2",
        "",
        "",
        "web_config",
        "",
        "2",
        "2",
        "",
        "",
        "",
    ]

    # Create the launch config
    add_launch_config("web_config")

    # Simulate CLI call
    autoscaling_group()

    conn = boto.connect_autoscale()
    configs = conn.get_all_groups()
    configs.should.have.length_of(1)
    config = configs[0]
    config.name.should.equal("web")
    set(config.availability_zones).should.equal(set(["us-east-1b", "us-east-1c"]))
    config.default_cooldown.should.equal(60)
    config.desired_capacity.should.equal(2)
    config.health_check_period.should.equal(None)
    config.health_check_type.should.equal("EC2")
    config.launch_config_name.should.equal("web_config")
    list(config.load_balancers).should.equal([])
    config.max_size.should.equal(2)
    config.min_size.should.equal(2)
    config.placement_group.should.equal(None)
    config.vpc_zone_identifier.should.equal("")
    list(config.termination_policies).should.equal([])


@mock_autoscaling()
@patch('autoscaler.cli.get_input')
@patch('autoscaler.cli.sys')
def test_autoscaling_group_edit(sys, user_input):
    add_launch_config("web_config", user_data="echo 'web_machine' > /etc/config")
    add_auto_scaling_group(
        "web",
        availability_zones=['us-east-1c'],
        max_size=2,
        min_size=2,
        launch_config='web_config',
    )

    sys.argv = [
        'autoscaler_auto_scaling_group',
        'edit',
        'web',
    ]
    # INPUTS
    # "availability_zones", "default_cooldown", "desired_capacity",
    # "health_check_period", "health_check_type", "launch_config_name",
    # "load_balancers", "max_size", "min_size", "placement_group",
    # "vpc_zone_identifier", "termination_policies"
    user_input.side_effect = [
        'us-east-1b,us-east-1c',
        '60',
        "2",
        "",
        "",
        "web_config",
        "",
        "1",
        "2",
        "",
        "",
        "",
    ]

    # Create the launch config
    add_launch_config("web_config")

    # Simulate CLI call
    autoscaling_group()

    conn = boto.connect_autoscale()
    configs = conn.get_all_groups(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]
    web_config.max_size.should.equal(1)
