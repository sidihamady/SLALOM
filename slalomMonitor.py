#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================================
# SLALOM - Open-Source Solar Cell Multivariate Optimizer
# Copyright(C) 2012-2018 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.
# (1) Université de Lorraine, Laboratoire Matériaux Optiques, Photonique et Systèmes, Metz, F-57070, France
# (2) Laboratoire Matériaux Optiques, Photonique et Systèmes, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France
# (*) sidi.hamady@univ-lorraine.fr
# Version: 1.0 Build: 1807
# SLALOM source code is available to download here: http://www.hamady.org/photovoltaics/slalom_source.zip
# See Copyright Notice in COPYRIGHT
# ======================================================================================================

# ------------------------------------------------------------------------------------------------------
# File:           slalomMonitor.py
# Type:           Module
# Use:            slalomMonitor can be used to the monitor the optimizer...
#                  ... either in client/server configuration using ssh...
#                  ... or locally if it runs on the same machine than the optimizer.
#                 slalomMonitor uses the slalomWindow class that provide...
#                  ... visualisation and control functionality.
#                 To use slalomMonitor from the console type one of...
#                  ...the following commands:
#                   python slalomMonitor.py filename_fullpath remote_ssh simulator_name
#                   python slalomMonitor.py filename_fullpath remote_ssh
#                   python slalomMonitor.py filename_fullpath
#                   python slalomMonitor.py
#                   The parameters can be set later within the monitor window.
#                 slalomMonitor can be automatically started...
#                  ... if the enableMonitor variable in the driver (slalom.py)...
#                  ... is set to True
# ------------------------------------------------------------------------------------------------------

from slalomWindow import *

# disable the standard output buffering
sys.stdout = UnbufferedStdout(sys.stdout)

strOptimizedFilename = None

# set remoteSSHhost to None to monitor locally, or something like "user@remoteserver"
# to monitor optimization on the a remote server.
# the ssh connexion should use auth keys, not password, for security reasons
remoteSSHhost = None

# the used backend solar cell simulator.
# by default set to "atlas", the simulator from Silvaco(r) company,...
# ... or "tibercad", the simulator from TiberLAB(r)
deviceSimulator = "atlas"

# get the data filename if given at the command line
if len(sys.argv) >= 2:
    strOptimizedFilename = sys.argv[1]
# end if

# get the SSH host if given at the command line...
# ... e.g. "user@remoteserver" (always using auth keys)
if len(sys.argv) >= 3:
    remoteSSHhost = sys.argv[2]
# end if

# get the solar cell simulator name
if len(sys.argv) >= 4:
    deviceSimulator = sys.argv[3]
# end if

# start the monitor
try:
    tMonitor = slalomWindow(dataFilename=strOptimizedFilename, remoteHost=remoteSSHhost, simulator=deviceSimulator)
except:
    pass
# end try
