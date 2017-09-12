#!/usr/bin/env python

import sys

if sys.version_info[0] < 3:
    from devices import *
else:
    from .devices import *

