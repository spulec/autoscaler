import boto
from moto import mock_autoscaling
import sure  # noqa

from autoscaler import (
    add_launch_config,
    add_auto_scaling_group,
    edit_auto_scaling_group,
    AutoScalerException,
)


@mock_autoscaling
def test_add_autoscaling_groups():
    add_launch_config("web_config", user_data="echo 'web_machine' > /etc/config")
    add_auto_scaling_group(
        "web",
        availability_zones=['us-east-1c'],
        max_size=2,
        min_size=2,
        launch_config='web_config',
    )

    conn = boto.connect_autoscale()
    configs = conn.get_all_groups(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]

    web_config.max_size.should.equal(2)


@mock_autoscaling
def test_edit_autoscaling_group():
    add_launch_config("web_config", user_data="echo 'web_machine' > /etc/config")
    add_auto_scaling_group(
        "web",
        availability_zones=['us-east-1c'],
        max_size=2,
        min_size=2,
        launch_config='web_config',
    )

    conn = boto.connect_autoscale()
    configs = conn.get_all_groups(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]
    web_config.max_size.should.equal(2)

    # Now edit the user data
    edit_auto_scaling_group("web", max_size=1)

    configs = conn.get_all_groups(names=['web'])
    configs.should.have.length_of(1)
    web_config = configs[0]

    web_config.max_size.should.equal(1)


@mock_autoscaling
def test_edit_missing_autoscaling_group():
    (edit_auto_scaling_group.when.called_with("web", max_size=2)
        .should.throw(AutoScalerException))
