#!/usr/bin/env python
import os
import sys
from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r internal')
    sys.exit()

setup(
        name="collectd",
        version="0.11",
        description="python stats service",
        long_description=open("README.md").read(),
        author="yancl",
        author_email="kmoving@gmail.com",
        url='https://github.com/yancl/collectd',
        classifiers=[
            'Programming Language :: Python',
        ],
        platforms='Linux',
        license='MIT License',
        zip_safe=False,
        install_requires=[
            'distribute',
            'cassandra_client >= 0.10',
        ],
        tests_require=[
            'nose',
        ],
        packages=['collectd', 'collectd.protocol', 'collectd.protocol.genpy', 'collectd.protocol.genpy.collectd']
)
