# WARNING: This library is still under active development

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

# Default Launch Config

In order for the default values to work, you must create a launch configuration with the name "autoscaler_default". This is where the default values will be pulled from. If there is no such launch configuration, the defaults will just be blank.

# Python Interface

```python
from autoscaler import add_launch_config, edit_launch_config

add_launch_config("web", user_data="echo 'web_machine' > /etc/config")

edit_launch_config("web", image_id='ami-abcd1234')
```

## Install

```console
$ pip install autoscaler
```
