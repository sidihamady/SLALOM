# -*- coding: utf-8 -*-

# ======================================================================================================
# SLALOM - Open-Source Solar Cell Multivariate Optimizer
# Copyright(C) 2012-2018 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.
# (1) Université de Lorraine, Laboratoire Matériaux Optiques, Photonique et Systèmes, Metz, F-57070, France
# (2) Laboratoire Matériaux Optiques, Photonique et Systèmes, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France
# (*) sidi.hamady@univ-lorraine.fr
# Version: 1.0 Build: 1811
# SLALOM source code is available to download from:
# https://github.com/sidihamady/SLALOM
# https://hal.archives-ouvertes.fr/hal-01897934
# http://www.hamady.org/photovoltaics/slalom_source.zip
# See Copyright Notice in COPYRIGHT
# ======================================================================================================

# ------------------------------------------------------------------------------------------------------
# File:           slalomSimulator.py
# Type:           Class
# Use:            slalomSimulator is used by slalomCore.py
#                  it includes the solar cell simulators interface...
#                  ...and can be easily extended to include any simulator that can be launched...
#                  ...from the command line and output results in text files
#                  ...(as for any well-designed simulator) 
# ------------------------------------------------------------------------------------------------------

import os
import sys

class slalomSimulator(object):
    """ the SLALOM interface class for solar cell simulators """

    def __init__(self, name):
        """ slalomSimulator constructor """

        self.__version__ = "Version 1.0 Build 1710"

        # list of supported simulators
        self.supported = ["atlas", "tibercad"]

        self.command = list()

        self.update("atlas")

    # end __init__

    def update(self, name, inputFilename = None, currentDir = None, outputDir = None, verboseFilename = None):
        """ slalomSimulator constructor """

        self.name = "atlas" if (name is None) else name
        if self.name not in self.supported:
            dispError("Unknown simulator engine '%s'" % str(self.name), doExit = True)
        # end if

        del self.command[:]
        self.command = list()

        if (outputDir is not None):
            if (os.name == "nt"):
                self.command.append("@echo off")
                self.command.append("cd " + outputDir)
            else:
                self.command.append("#!/bin/sh")
                self.command.append("cd " + outputDir)
            # end if
        # end if

        if (self.name == "atlas"):
            self.header = "v ATLAS"
            self.error = "ERROR:"
            self.error = [("ERROR:","Atlas error"),("SCI System Error:","Silvaco C interpreter error")]
            self.filedecl = ["outfile=\"%s\"", "outf=\"%s\"", "datafile=\"%s\"", "dataf=\"%s\""]
            self.vardeclpre = "set %s"
            self.vardecl = "set %s=%g"
            self.dataSeparator = " "
            if (inputFilename is not None) and (verboseFilename is not None):
                self.command.append("deckbuild -run " + inputFilename + " -outfile " + verboseFilename + " -noplot")
            # end if
        elif (self.name == "tibercad"):
            self.header = "v ATLAS"
            self.error = [("ERROR:","Atlas error"),("SCI System Error:","Silvaco C interpreter error")]
            self.filedecl = ["outfile=\"%s\"", "outf=\"%s\"", "datafile=\"%s\"", "dataf=\"%s\""]
            self.vardeclpre = "set %s"
            self.vardecl = "set %s=%g"
            self.dataSeparator = " "
            if (inputFilename is not None) and (verboseFilename is not None):
                self.command.append("deckbuild -ascii -run " + inputFilename + " -outfile " + verboseFilename + " -noplot")
            # end if
        else:
            dispError("Unknown simulator engine '%s'" % str(self.name), doExit = True)
        # end if

        if (currentDir is not None):
            if (os.name == "nt"):
                self.command.append("cd " + currentDir)
                self.command.append("exit")
            else:
                self.command.append("cd " + currentDir)
                self.command.append("exit 0")
            # end if
        # end if

    # end update

# end slalomSimulator
