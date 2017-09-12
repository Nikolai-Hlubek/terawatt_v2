#!/usr/bin/env python

import sys

if sys.version_info[0] < 3:
    import devices
else:
    from .devices import *

