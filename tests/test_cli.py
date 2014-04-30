import boto
from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType
from mock import patch, call
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
    # "kernel_id", "ramdisk_id", "block_device_mappings", "instance_monitoring",
    # "instance_profile_name", "spot_price", "ebs_optimized", "associate_public_ip_address"
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
        "arn:aws:iam::123456789012:instance-profile/tester",
        "0.2",
        "yes",
        "",
    ]

    # Simulate CLI call
    launch_config()

    conn = boto.connect_autoscale(use_block_device_types=True)
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
    config.block_device_mappings.should.equal(BlockDeviceMapping())
    config.instance_monitoring.enabled.should.equal('true')
    config.spot_price.should.equal(0.2)
    config.ebs_optimized.should.equal(True)
    config.associate_public_ip_address.should.equal(False)


@mock_autoscaling()
@patch('autoscaler.cli.get_input')
@patch('autoscaler.cli.sys')
def test_launch_config_add_with_block_device_mapping(sys, user_input):
    sys.argv = [
        'autoscaler_launch_config',
        'add',
        'web',
    ]

    # "image_id", "key_name", "security_groups", "user_data", "instance_type",
    # "kernel_id", "ramdisk_id", "block_device_mappings", "instance_monitoring",
    # "instance_profile_name", "spot_price", "ebs_optimized", "associate_public_ip_address"
    user_input.side_effect = [
        'ami-1234abcd',
        'the_key',
        "default,web",
        "echo 'web' > /etc/config",
        "m1.small",
        "",
        "",
        "/dev/xvda=:100,/dev/xvdb=:200,/dev/xvdc=snap-1234abcd:10",
        "yes",
        "arn:aws:iam::123456789012:instance-profile/tester",
        "0.2",
        "yes",
        "",
    ]

    # Simulate CLI call
    launch_config()

    # Build a fake block device mapping
    bdm = BlockDeviceMapping()
    bdm['/dev/xvda'] = BlockDeviceType(volume_id='/dev/xvda', size=100)
    bdm['/dev/xvdb'] = BlockDeviceType(volume_id='/dev/xvdb', size=200)
    bdm['/dev/xvdc'] = BlockDeviceType(volume_id='/dev/xvdc', snapshot_id="snap-1234abcd", size=10)

    conn = boto.connect_autoscale(use_block_device_types=True)
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
    config.instance_monitoring.enabled.should.equal('true')
    config.spot_price.should.equal(0.2)
    config.ebs_optimized.should.equal(True)
    config.associate_public_ip_address.should.equal(False)
    config.block_device_mappings.keys().should.equal(bdm.keys())
    config.block_device_mappings['/dev/xvda'].size.should.equal(100)
    config.block_device_mappings['/dev/xvdb'].size.should.equal(200)
    config.block_device_mappings['/dev/xvdc'].size.should.equal(10)
    config.block_device_mappings['/dev/xvdc'].snapshot_id.should.equal("snap-1234abcd")


@mock_autoscaling()
@patch('autoscaler.cli.read_input')
@patch('autoscaler.cli.sys')
def test_launch_config_edit(sys, read_input):
    add_launch_config(
        "web",
        user_data="echo 'web_machine' > /etc/config",
        spot_price=0.2,
        instance_monitoring=True,
    )

    sys.argv = [
        'autoscaler_launch_config',
        'edit',
        'web',
    ]

    # "image_id", "key_name", "security_groups", "user_data", "instance_type",
    # "kernel_id", "ramdisk_id", "block_device_mappings", "instance_monitoring"
    # "instance_profile_name", "spot_price", "ebs_optimized", "associate_public_ip_address"
    read_input.side_effect = [
        "",
        "",
        "",
        "echo 'other_machine' > /etc/config",
        "",
        "",
        "",
        "",
        "yes",
        "arn:aws:iam::123456789012:instance-profile/tester",
        "0.1",
        "yes",
        "yes",
    ]

    # Simulate CLI call
    launch_config()

    list(read_input.mock_calls).should.equal([
        call('What image_id?', u'None'),
        call('What key_name?', ''),
        call('What security_groups?', ''),
        call('What user_data?', "echo 'web_machine' > /etc/config"),
        call('What instance_type?', u'm1.small'),
        call('What kernel_id?', ''),
        call('What ramdisk_id?', ''),
        call('What block_device_mappings?', BlockDeviceMapping()),
        call('What instance_monitoring?', "yes"),
        call('What instance_profile_name?', None),
        call('What spot_price?', 0.2),
        call('What ebs_optimized?', "no"),
        call('What associate_public_ip_address?', False),
    ])

    conn = boto.connect_autoscale(use_block_device_types=True)
    configs = conn.get_all_launch_configurations(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]
    web_config.user_data.should.equal("echo 'other_machine' > /etc/config")
    web_config.spot_price.should.equal(0.1)
    web_config.ebs_optimized.should.equal(True)
    web_config.associate_public_ip_address.should.equal(True)



@mock_autoscaling()
@patch('autoscaler.cli.read_input')
@patch('autoscaler.cli.sys')
def test_launch_config_edit_with_other_values(sys, read_input):
    add_launch_config(
        "web",
        user_data="echo 'web_machine' > /etc/config",
        spot_price=0.2,
        instance_monitoring=True,
        ebs_optimized=True,
    )

    sys.argv = [
        'autoscaler_launch_config',
        'edit',
        'web',
    ]

    # "image_id", "key_name", "security_groups", "user_data", "instance_type",
    # "kernel_id", "ramdisk_id", "block_device_mappings", "instance_monitoring"
    # "instance_profile_name", "spot_price", "ebs_optimized", "associate_public_ip_address"
    read_input.side_effect = [
        "",
        "",
        "",
        "echo 'other_machine' > /etc/config",
        "",
        "",
        "",
        "",
        "yes",
        "arn:aws:iam::123456789012:instance-profile/tester",
        "0.1",
        "no",
        "no",
    ]

    # Simulate CLI call
    launch_config()

    list(read_input.mock_calls).should.equal([
        call('What image_id?', u'None'),
        call('What key_name?', ''),
        call('What security_groups?', ''),
        call('What user_data?', "echo 'web_machine' > /etc/config"),
        call('What instance_type?', u'm1.small'),
        call('What kernel_id?', ''),
        call('What ramdisk_id?', ''),
        call('What block_device_mappings?', BlockDeviceMapping()),
        call('What instance_monitoring?', "yes"),
        call('What instance_profile_name?', None),
        call('What spot_price?', 0.2),
        call('What ebs_optimized?', "yes"),
        call('What associate_public_ip_address?', False),
    ])

    conn = boto.connect_autoscale(use_block_device_types=True)
    configs = conn.get_all_launch_configurations(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]
    web_config.ebs_optimized.should.equal(False)
    web_config.associate_public_ip_address.should.equal(False)


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

    conn = boto.connect_autoscale(use_block_device_types=True)
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

    conn = boto.connect_autoscale(use_block_device_types=True)
    configs = conn.get_all_groups(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]
    web_config.max_size.should.equal(1)
