# AutoScaler - AWS AutoScaling Configuration Tool

[![Build Status](https://travis-ci.org/spulec/autoscaler.png?branch=master)](https://travis-ci.org/spulec/autoscaler)
[![Coverage Status](https://coveralls.io/repos/spulec/autoscaler/badge.png?branch=master)](https://coveralls.io/r/spulec/autoscaler)

# In a nutshell

Creating and managing a large number of Launch Configurations and AutoScaling Groups can be a pain. AutoScaler aims to make it easier.

# Command line

Create a new launch configuration with the ability to override default values.

![](https://spulec.s3.amazonaws.com/launch_config_add.gif)

![](https://spulec.s3.amazonaws.com/launch_config_edit.gif)

It should be noted that AutoScaler is not actually editing the launch configuration since that is not available in the AutoScaling API. What AutoScaler is actually doing is:
- creating a temporary launch configuration with the new values
- moving over all autoscaling groups to the temporary configuration
- deleting the original launch configuration
- creating a replacement launch configuration with the same name
- moving over all autoscaling groups to the replacement configuration
- deleting the temporary configuration

There is also `autoscaler_auto_scaling_group` which has the same interface for AutoScaling groups.

You must set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables properly for this to work.

# Default Launch Config

In order for the default values to work, you must create a launch configuration with the name "autoscaler_default". This is where the default values will be pulled from. If there is no such launch configuration, the defaults will just be blank.

# Python Interface

```python
from autoscaler import add_launch_config, edit_launch_config

add_launch_config("web", user_data="echo 'web_machine' > /etc/config")

edit_launch_config("web", image_id='ami-abcd1234')
```

# Block Device Mappings

A custom syntax has been added to create Block Device Mappings from the command line and convert those to Python objects.

The tested format can be found in `tests/test_parsers.py` but the abbreviated form is available here.  All examples show the expected user input.

### General Format

```python
# Ephemeral Drive
user_input = "[mount_point]=[ephemeral_drive]"
# EBS Drives
user_input = "[mount_point]=[snapshot]:[size]:[delete_on_termination]:[iops]"
```

### Ephemeral Drive

```python
# Note ephemeral[0-7] corresponds to the AWS ephemeral disk mapping
user_input = "/dev/xvdb=ephemeral0"
```

### Snapshot or EBS Drive

```python
# This will preserve the snapshot size
user_input = "/dev/xvdf=snap-1234abcd"

# 100GB Drive
user_input = "/dev/xvdf=:100"

# 100GB Drive without 'Delete on Termination'
user_input = "/dev/xvdf=:100:false"

# 100GB Drive with 1000 IOPS and no 'Delete on Termination'
user_input = "/dev/xvdf=:100:false:1000"
```

## Install

```console
$ pip install autoscaler
```
