#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()
progname = sys.argv[1]

cpu.load(progname)
cpu.run()