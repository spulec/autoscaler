# WARNING: This library is still under active development

# AutoScaler - AWS AutoScaling Configuration Tool

[![Build Status](https://travis-ci.org/spulec/autoscaler.png?branch=master)](https://travis-ci.org/spulec/autoscaler)
[![Coverage Status](https://coveralls.io/repos/spulec/autoscaler/badge.png?branch=master)](https://coveralls.io/r/spulec/autoscaler)

# In a nutshell

Creating and managing a large number of Launch Configurations and AutoScaling Groups can be a pain. AutoScaler aims to make it easier.

# Command line

Create a new launch configuration with the ability to override default values.

TODO: make this a gif of use
```console
$ autoscaler_launch_config add web
Iam Instance Profile? web
Image id? ami-1234abcd
Instnace Monitoring? y
Key name? prod_web
Security groups? default,web
User data? "echo 'web' > /etc/config"
```

```console
$ autoscaler_launch_config edit web
Iam Instance Profile? web
Image id? ami-1234abcd
Instnace Monitoring? y
Key name? prod_web
Security groups? default,web
User data? "echo 'web' > /etc/config"
```

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
