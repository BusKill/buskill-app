#!/usr/bin/env python3.7
"""
::

  File:    packages/buskill/root_child_mac.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2022-10-15
  Updated: 2022-10-15
  Version: 0.1

This is a very small python script that is intended to be run with root privileges on MacOS platforms. It should be as small and paranoid as possible, and only contain logic that cannot run as the normal user due to insufficient permissions (eg shutting down the machine)

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

################################################################################
#                                  SETTINGS                                    #
################################################################################

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

################################################################################
#                                  MAIN BODY                                   #
################################################################################

import os
with open("/Users/administrator/buskill_root.out", "a") as f:
    f.write("I am root!\n")
