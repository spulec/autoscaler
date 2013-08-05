import boto
from boto.ec2.autoscale.group import AutoScalingGroup
from boto.ec2.autoscale.launchconfig import LaunchConfiguration
from moto import mock_autoscaling
import sure  # noqa

from autoscaler import add_launch_config, edit_launch_config, AutoScalerException


@mock_autoscaling
def test_add_launch_configuration():
    add_launch_config("web", user_data="echo 'web_machine' > /etc/config")

    conn = boto.connect_autoscale()
    configs = conn.get_all_launch_configurations(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]

    web_config.user_data.should.equal("echo 'web_machine' > /etc/config")


@mock_autoscaling
def test_add_launch_configuration_with_default_config():
    conn = boto.connect_autoscale()

    config = LaunchConfiguration(
        name='autoscaler_default',
        image_id='ami-1234abcd',
        key_name='tester',
        security_groups=["default"],
        user_data="echo 'default_machine' > /etc/config",
        instance_type='m1.large',
        instance_monitoring=True,
        instance_profile_name='arn:aws:iam::123456789012:instance-profile/tester',
        spot_price=0.1,
    )
    conn.create_launch_configuration(config)
    conn.get_all_launch_configurations().should.have.length_of(1)

    add_launch_config("web", user_data="echo 'web_machine' > /etc/config")

    configs = conn.get_all_launch_configurations(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]

    web_config.user_data.should.equal("echo 'web_machine' > /etc/config")
    web_config.image_id.should.equal('ami-1234abcd')
    web_config.key_name.should.equal('tester')
    web_config.instance_profile_name.should.equal('arn:aws:iam::123456789012:instance-profile/tester')
    web_config.spot_price.should.equal(0.1)


@mock_autoscaling
def test_edit_launch_configuration():
    add_launch_config("web", user_data="echo 'web_machine' > /etc/config")

    conn = boto.connect_autoscale()
    configs = conn.get_all_launch_configurations(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]
    web_config.user_data.should.equal("echo 'web_machine' > /etc/config")

    # Now edit the user data
    edit_launch_config("web", user_data="echo 'other_machine' > /etc/config")

    configs = conn.get_all_launch_configurations(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]

    web_config.user_data.should.equal("echo 'other_machine' > /etc/config")

    # And there should only be a single launch configuration
    conn.get_all_launch_configurations().should.have.length_of(1)


@mock_autoscaling
def test_edit_missing_launch_configuration():
    (edit_launch_config.when.called_with("web", key_name='tester')
        .should.throw(AutoScalerException))


@mock_autoscaling
def test_editing_launch_configuration_update_AS_groups():
    conn = boto.connect_autoscale()
    config = add_launch_config("web", user_data="echo 'web_machine' > /etc/config")
    group = AutoScalingGroup(
        name='web',
        launch_config=config,
        max_size=2,
        min_size=2,
    )
    conn.create_auto_scaling_group(group)

    # Now edit the user data
    edit_launch_config("web", user_data="echo 'other_machine' > /etc/config")

    group = conn.get_all_groups()[0]
    config_name = group.launch_config_name
    config_name.should.equal("web")
    config = conn.get_all_launch_configurations(names=[config_name])[0]
    config.user_data.should.equal("echo 'other_machine' > /etc/config")
