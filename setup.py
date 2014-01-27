#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='autoscaler',
    version='0.0.7',
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
    dependency_links=[
        "https://github.com/hltbra/boto/archive/8673805da0c343dbf259bb0473c10ff1f6435094.zip#egg=boto-2.23.0-hltbra",
    ],
    install_requires=[
        "boto==2.23.0-hltbra",
        "docopt",
    ],
)
