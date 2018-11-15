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
# https://hal.archives-ouvertes.fr/hal-01897934v1
# http://www.hamady.org/photovoltaics/slalom_source.zip
# See Copyright Notice in COPYRIGHT
# ======================================================================================================

# ------------------------------------------------------------------------------------------------------
# File:           slalomDeviceExt.py
# Type:           Module
# Purposes:       Devices definition class:
#                 * slalomDevice class define a set of devices (e.g. "InGaN_PN", CZTS_NP", etc.)...
#                   ...for easier and more robust optimization work.
#                 * Extend slalomDevice class to include any set of devices for a specific project.
# ------------------------------------------------------------------------------------------------------

from slalomDevice import *

class slalomDeviceExt(slalomDevice):
    """ Device definition class. Contains a set of predefined solar cell structures """

    def __init__(self, deviceType, currentDir, randomInit=False):
        """ slalomDevice constructor where the solar cell structures are defined """

        slalomDevice.__init__(deviceType, currentDir, randomInit)

    # end __init__

    def reset(self, deviceType):
        """ reset the device type """

        slalomDevice.reset(deviceType)

        self.deviceType = deviceType

        # device not defined: just define data and return.
        if (self.deviceType is None):
            # Deckbuild input filename
            self.inputFilename = ""
            # Device description
            self.mainTitle = ""
            # Output directory
            self.outputDir = ""
            # Parameters name, as defined is the Deckbuild input
            self.paramName = None
            # Parameters unit
            self.paramUnit = None
            # Parameters format string (e.g.  for doping use "%.6e")
            self.paramFormat = None
            # Parameters short format string for console output (e.g.  for
            # doping use "%.4e")
            self.paramFormatShort = None
            # Normalized parameters format string for console output
            self.paramFormatNormalized = None
            # Normalization value for each parameter
            self.paramNorm = None
            # Parameters range limit (Start)
            self.paramStart = None
            # Parameters range limit (End)
            self.paramEnd = None
            # Parameters initial values (used as a starting point or when
            # optimType is set to "Snap")
            self.paramInit = None
            # Parameters number of points (used as when optimType is set to
            # "Brute")
            self.paramPoints = None
            # Parameters variation type (True for logarithmic variation (e.g.
            # for doping), and False for linear)
            self.paramLogscale = None
            self.paramWeight = False
            # C source code files used to set the models used by the device
            # simulator
            self.modelFilename = None
            return
        # end if

        # C files parameters and models common to all InGaN structures
        if self.deviceType.startswith("InGaN_"):
            # C source code files used to set the models used by the device
            # simulator
             self.modelFilename = ["InN_GaN_Parameters.h", "InGaN_Bandgap.c", "InGaN_Permittivity.c", "InGaN_Recomb.c", "InGaN_Index.c", "InGaN_Mobility.c"]
        # end if

        if self.deviceType == "InGaN_Schottky" or deviceType == "InGaN_SCH":
            # Deckbuild input filename
            self.inputFilename = "InGaN_Schottky.in"
            # Device description
            self.mainTitle = "Schottky InGaN PV Cell"
            # Output directory
            self.outputDir = self.currentDir + "output" + self.dirSepChar + "InGaN" + self.dirSepChar
            # Parameters name, as defined is the Deckbuild input
            self.paramName = ["Workfunction", "NLayerThick", "NLayerDop", "AlloyComp"]
            # Parameters unit
            self.paramUnit = ["eV", "um", "1/cm3", ""]
            # Parameters format string (e.g.  for doping use "%.6e")
            self.paramFormat = ["%.8f", "%.8f", "%.6e", "%.8f"]
            # Parameters short format string for console output (e.g.  for
            # doping use "%.4e")
            self.paramFormatShort = ["%.6f", "%.6f", "%.4e", "%.6f"]
            # Normalized parameters format string for console output
            self.paramFormatNormalized = ["%.8f", "%.8f", "%.8f", "%.8f"]
            # Normalization value for each parameter
            self.paramNorm = np.array([1.00, 1.000, 1e15, 1.000])
            # Parameters range limit (Start)
            self.paramStart = np.array([5.5, 0.0001, 1e15, 0.10])
            # Parameters range limit (End)
            self.paramEnd = np.array([6.5, 5.000, 1e21, 0.90])
            # Parameters initial values (used as a starting point or when
            # optimType is set to "Snap" or when set to "Brute" with 1 point)
            self.paramInit = np.array([6.0, 0.500, 1e17, 0.50])
            # Parameters number of points (used as when optimType is set to
            # "Brute")
            self.paramPoints = [1, 1, 3, 3]
            # Parameters variation type (True for logarithmic variation, e.g.
            # for doping, ...)
            self.paramLogscale = [False, False, True, False]
            self.paramWeight = False

        if self.deviceType == "InGaN_PIN":
            # Deckbuild input filename
            self.inputFilename = "InGaN_PIN.in"
            # Device description
            self.mainTitle = "PIN InGaN PV Cell"
            # Output directory
            self.outputDir = self.currentDir + "output" + self.dirSepChar + "InGaN" + self.dirSepChar
            # Parameters name, as defined is the Deckbuild input
            self.paramName = ["PLayerThick", "NLayerThick", "PLayerDop", "NLayerDop", "ILayerThick", "AlloyComp"]
            # Parameters unit
            self.paramUnit = ["um", "um", "1/cm3", "1/cm3", "um", ""]
            # Parameters format string (e.g.  for doping use "%.6e")
            self.paramFormat = ["%.8f", "%.8f", "%.6e", "%.6e", "%.8f", "%.8f"]
            # Parameters short format string for console output (e.g.  for
            # doping use "%.4e")
            self.paramFormatShort = ["%.6f", "%.6f", "%.4e", "%.4e", "%.6f", "%.6f"]
            # Normalized parameters format string for console output
            self.paramFormatNormalized = ["%.8f", "%.8f", "%.8f", "%.8f", "%.8f", "%.8f"]
            # Normalization value for each parameter
            self.paramNorm = np.array([1.00, 1.000, 1e17, 1e17, 1.000, 1.000])
            # Parameters range limit (Start)
            self.paramStart = np.array([0.0001, 0.0001, 1e15, 1e15, 0.0001, 0.10])
            # Parameters range limit (End)
            self.paramEnd = np.array([5.000, 5.000, 1e21, 1e21, 5.000, 0.90])
            # Parameters initial values (used as a starting point or when
            # optimType is set to "Snap")
            self.paramInit = np.array([0.500, 0.500, 1e17, 1e17, 0.500, 0.50])
            # Parameters number of points (used as when optimType is set to
            # "Brute")
            self.paramPoints = [3, 3, 3, 3, 3, 3]
            # Parameters variation type (True for logarithmic variation (e.g.
            # for doping), and False for linear)
            self.paramLogscale = [False, False, True, True, False, False]
            self.paramWeight = False

        elif self.deviceType == "InGaN_MIN":
            # Deckbuild input filename
            self.inputFilename = "InGaN_MIN.in"
            # Device description
            self.mainTitle = "MIN InGaN PV Cell"
            # Output directory
            self.outputDir = self.currentDir + "output" + self.dirSepChar + "InGaN" + self.dirSepChar
            # Parameters name, as defined is the Deckbuild input
            self.paramName = ["ILayerThick", "ILayerDop", "NLayerDop", "NLayerThick", "AlloyComp", "TrapConc"]
            # Parameters unit
            self.paramUnit = ["um", "1/cm3", "1/cm3", "um", "", "1/cm3"]
            # Parameters format string (e.g.  for doping use "%.6e")
            self.paramFormat = ["%.8f", "%.6e", "%.6e", "%.8f", "%.8f", "%.6e"]
            # Parameters short format string for console output (e.g.  for
            # doping use "%.4e")
            self.paramFormatShort = ["%.6f", "%.4e", "%.4e", "%.6f", "%.6f", "%.4e"]
            # Normalized parameters format string for console output
            self.paramFormatNormalized = ["%.8f", "%.8f", "%.8f", "%.8f", "%.8f", "%.8f"]
            # Normalization value for each parameter
            self.paramNorm = np.array([1.000, 1e17, 1e17, 1.000, 1.000, 1e17])
            # Parameters range limit (Start)
            self.paramStart = np.array([0.100, 1e14, 1e14, 0.100, 0.12, 1e14])
            # Parameters range limit (End)
            self.paramEnd = np.array([0.400, 1e17, 1e18, 0.400, 0.25, 1e18])
            # Parameters initial values (used as a starting point or when
            # optimType is set to "Snap")
            self.paramInit = np.array([0.400, 7.5e15, 7.4e16, 0.400, 0.25, 1e13])
            # Parameters number of points (used as when optimType is set to
            # "Brute")
            self.paramPoints = [1, 1, 1, 6, 1, 1]
            # Parameters variation type (True for logarithmic variation (e.g.
            # for doping), and False for linear)
            self.paramLogscale = [False, True, True, False, False, True]
            self.paramWeight = False

        # end if

    # end reset

# end slalomDeviceExt
