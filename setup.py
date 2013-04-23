#!/usr/bin/env python

from distutils.core import setup

setup(
        name = "xbird",
        version = "0.10",
        description="python stats service",
        maintainer="yancl",
        maintainer_email="kmoving@gmail.com",
        packages=['xbird', 'xbird.protocol', 'xbird.protocol.genpy', 'xbird.protocol.genpy.xbird']
)
