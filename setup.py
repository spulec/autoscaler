#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='autoscaler',
    version='0.0.5',
    description='AutoScaler makes it easier to create and manage a large '
                'number of Launch Configurations and AutoScaling Groups',
    author='Steve Pulec',
    author_email='spulec@gmail',
    url='https://github.com/spulec/autoscaler',
    entry_points={
        'console_scripts': [
            'autoscaler_launch_config = autoscaler.cli:launch_config',
            'autoscaler_auto_scaling_group = autoscaler.cli:autoscaling_group',
        ],
    },
    packages=find_packages(),
    install_requires=[
        "boto",
        "docopt",
    ],
)
