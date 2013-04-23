#!/usr/bin/env python

from distutils.core import setup

setup(
        name = "collectd",
        version = "0.10",
        description="python stats service",
        maintainer="yancl",
        maintainer_email="kmoving@gmail.com",
        packages=['collectd', 'collectd.protocol', 'collectd.protocol.genpy', 'collectd.protocol.genpy.collectd']
)
