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
# File:           slalomDevice.py
# Type:           Module
# Purposes:       Devices definition class:
#                 * slalomDevice class define a set of devices (e.g. "InGaN_PN", CZTS_NP", etc.)...
#                   ...for easier and more robust optimization work.
#                 * Extend slalomDevice class to include any set of devices for a specific project.
# ------------------------------------------------------------------------------------------------------

import numpy as np
import os
import random
import math
import datetime

class slalomDevice(object):
    """ Device definition class. Contains a set of predefined solar cell structures """

    def __init__(self, deviceType, currentDir, randomInit = False):
        """ slalomDevice constructor where the solar cell structures are defined """

        self.__version__ = "Version 1.0 Build 1710"

        self.dirSepChar = '/'

        # Working directory
        self.currentDir = currentDir

        self.reset(deviceType)

        self.paramFormatOutput = "%.6f"

        # randomInit choose randomly a starting point for the optimizer.
        # Starting the optimizer with a random point could be a way
        # to check the uniqueness of the optimized set of parameters.
        if (randomInit == True) and (self.deviceType is not None):
            self.randomInit()
        #end if

    # end __init__

    def reset(self, deviceType):
        """ reset the device type """

        self.deviceType = deviceType

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
        # Parameters format string (e.g. for doping use "%.6e")
        self.paramFormat = None
        # Parameters short format string for console output (e.g. for doping use "%.4e")
        self.paramFormatShort = None
        # Normalized parameters format string for console output
        self.paramFormatNormalized = None
        # Normalization value for each parameter
        self.paramNorm = None
        # Parameters range limit (Start)
        self.paramStart = None
        # Parameters range limit (End)
        self.paramEnd = None
        # Parameters initial values (used as a starting point or when optimType is set to "Snap")
        self.paramInit = None
        # Parameters number of points (used as when optimType is set to "Brute")
        self.paramPoints = None
        # Parameters variation type (True for logarithmic variation (e.g. for doping), and False for linear)
        self.paramLogscale = None
        self.paramWeight = False
        # C source code files used to set the models used by the device simulator
        self.modelFilename =  None

        # device not defined: just define data and return.
        if (self.deviceType is None):
            return
        # end if

        # C files parameters and models common to all InGaN structures
        if self.deviceType.startswith("InGaN_"):
            # C source code files used to set the models used by the device simulator
             self.modelFilename = [ "InN_GaN_Parameters.h", "InGaN_Bandgap.c", "InGaN_Permittivity.c", "InGaN_Recomb.c", "InGaN_Index.c", "InGaN_Mobility.c" ]
        # end if

        if self.deviceType == "InGaN_PN":
            # on a server with 8-core Xeon processors and 32 GB of RAM...
            # one simulation takes up to five minutes, with the given input and parameters,
            # strongly depending on numerical parameters (mesh, propagation, solver...) and device parameters.
            # Deckbuild input filename
            self.inputFilename = "InGaN_PN.in"
            # Device description
            self.mainTitle = "PN InGaN PV Cell"
            # Output directory
            self.outputDir = self.currentDir + "output" + self.dirSepChar + self.deviceType + self.dirSepChar
            # Parameters name, as defined is the Deckbuild input
            self.paramName = ["PLayerThick", "PLayerDop", "NLayerThick", "NLayerDop", "AlloyComp"]
            # Parameters unit
            self.paramUnit = ["um", "1/cm3", "um", "1/cm3", ""]
            # Parameters format string (e.g. for doping use "%.6e")
            self.paramFormat = ["%.8f", "%.6e", "%.8f", "%.6e", "%.8f"]
            # Parameters short format string for console output (e.g. for doping use "%.4e")
            self.paramFormatShort = ["%.6f", "%.4e","%.6f",  "%.4e", "%.6f"]
            # Normalized parameters format string for console output
            self.paramFormatNormalized = ["%.8f", "%.8f", "%.8f", "%.8f", "%.8f"]
            # Normalization value for each parameter
            self.paramNorm = np.array([1.000, 1e17, 1.000, 1e17, 1.00])
            # Parameters range limit (Start)
            self.paramStart = np.array([0.001, 1e13, 0.001, 1e13, 0.05])
            # Parameters range limit (End)
            self.paramEnd = np.array([2.000, 1e20, 2.000, 1e20, 0.95])
            # Parameters initial values (used as a starting point or when optimType is set to "Snap")
            # should be in the [paramStart, paramEnd] range
            self.paramInit = np.array([0.100, 1e17, 0.500, 1e15, 0.56])
            # Parameters number of points (used as when optimType is set to "Brute")
            self.paramPoints = [5, 5, 5, 5, 1]
            # Parameters variation type (True for logarithmic variation (e.g. for doping), and False for linear)
            self.paramLogscale = [False, True, False, True, False]
            self.paramWeight = False

        elif self.deviceType == "CZTS":
            # on a server with 8-core Xeon processors and 32 GB of RAM...
            # one simulation takes up to ten minutes, with the given input and parameters,
            # strongly depending on numerical parameters (mesh, propagation, solver...) and device parameters.
            # Deckbuild input filename
            self.inputFilename = "CZTS_NP.in"
            # Device description
            self.mainTitle = "CdS/CZTS PV Cell"
            # Output directory
            self.outputDir = self.currentDir + "output" + self.dirSepChar + self.deviceType + self.dirSepChar
            # Parameters name, as defined is the Deckbuild input
            self.paramName = ["CZTSLayerThick", "CZTSLayerDop"]
            # Parameters unit
            self.paramUnit = ["um", "1/cm3"]
            # Parameters format string (e.g. for doping use "%.6e")
            self.paramFormat = ["%.8f", "%.6e"]
            # Parameters short format string for console output (e.g. for doping use "%.4e")
            self.paramFormatShort = ["%.6f", "%.4e"]
            # Normalized parameters format string for console output
            self.paramFormatNormalized = ["%.8f", "%.8f"]
            # Normalization value for each parameter
            self.paramNorm = np.array([1.000, 1e17])
            # Parameters range limit (Start)
            self.paramStart = np.array([0.100, 1e15])
            # Parameters range limit (End)
            self.paramEnd = np.array([3.000, 1e18])
            # Parameters initial values (used as a starting point or when optimType is set to "Snap")
            # should be in the [paramStart, paramEnd] range
            self.paramInit = np.array([0.500, 1e17])
            # Parameters number of points (used as when optimType is set to "Brute")
            self.paramPoints = [ 1, 1]
            # Parameters variation type (True for logarithmic variation (e.g. for doping), and False for linear)
            self.paramLogscale = [False, True]
            self.paramWeight = False
            # C source code files used to set the models used by the device simulator
            self.modelFilename = [ "CZTS_Parameters.h", "CZTS_Index.c", "CdS_Index.c", "ZnO_Index.c" ]

        else:
            self.deviceType = None
        # end if

    # end reset

    def validate(self):
        """ validate the device data. Returns (status,message) """

        strMsg = None
        try:
            if self.deviceType is None:
                return (False, 'Device not defined')
            # end if

            self.mainTitle = self.deviceType

            if (not self.inputFilename) or (len(self.inputFilename) < 4):
                return (False, "Device input file '%s' not defined" % self.inputFilename)
            # end if

            if (not self.currentDir) or (len(self.currentDir) < 4) or (not os.path.exists(self.currentDir)):
                return (False, "Current directory '%s' not defined" % self.currentDir)
            # end if

            if (not os.path.exists(self.currentDir)) or (not os.path.exists(self.currentDir + self.inputFilename)):
                return (False, "Input directory/file '%s/%s' not found" % (self.currentDir, self.inputFilename))
            # end if

            iCount = len(self.paramName)
            if (iCount < 1) or (iCount > 12):
                return (False, "Invalid number of parameters '%d' (should be between 1 and 12)" % iCount)
            # end if

            if ((iCount != len(self.paramUnit))
                or (iCount != len(self.paramFormat)) or (iCount != len(self.paramFormatShort))
                or (iCount != len(self.paramFormatNormalized)) or (iCount != len(self.paramNorm))
                or (iCount != len(self.paramStart)) or (iCount != len(self.paramEnd))
                or (iCount != len(self.paramInit)) or (iCount != len(self.paramPoints)) 
                or (iCount != len(self.paramLogscale))):
                return (False, "Invalid number of parameters data (should correspond to the number of parameters name '%d')" % iCount)
            # end if

            if self.modelFilename:
                iml = len(self.modelFilename)
                for ii in range(0, iml):
                    if (not self.modelFilename[ii]) or (len(self.modelFilename[ii]) < 3):
                        break
                    # end if
                    if (not os.path.exists(self.currentDir + self.modelFilename[ii])):
                        return (False, "Model file '%s' not found" % (self.currentDir + self.modelFilename[ii]))
                    # end if
                # end for
            # end if

            del self.paramFormatShort[:]
            self.paramFormatShort = list(self.paramFormat)
            del self.paramFormatNormalized[:]
            self.paramFormatNormalized = list(self.paramFormat)
            del self.paramUnit[:]
            for ii in range(0, iCount):
                try:
                    strT = self.paramFormat[ii] % self.paramStart[0]
                except:
                    return (False, "Invalid number format '%s' ( example of valid format: %.8f )" % self.paramFormat[ii])
                # end try
                self.paramFormatNormalized[ii] = '%.8f'

                self.paramUnit.append(' ')

                if (self.paramPoints[ii] < 1) or (self.paramPoints[ii] > 1001):
                    return (False, "Invalid number of points '%d' (should be between 1 and 1001)", self.paramPoints[ii])
                # end if
                if (self.paramInit[ii] < self.paramStart[ii]) or (self.paramInit[ii] > self.paramEnd[ii]):
                    return (False, "Invalid initial parameter '%s' value '%g' (should be in the [%g, %g] range)" % (self.paramName[ii], self.paramInit[ii], self.paramStart[ii], self.paramEnd[ii]))
                # end if
            # end for

        except Exception as excT:
            return (False, 'Device data not valid ' + str(excT))
        # end try

        return (True, 'Device data valid')
    # end validate

    def randomInit(self, printOut = False):
        """ choose randomly a starting point for the optimizer\nStarting the optimizer with a random point could be a way\nto check the uniqueness of the optimized set of parameters"""

        self.randomParamStr = None
        if self.deviceType is not None:
            paramCount = len(self.paramName)
            paramStart = 0
            paramEnd = 0
            for ii in range(0, paramCount):
                if self.paramLogscale[ii]:
                    paramStart = math.log10(self.paramStart[ii]) / math.log10(self.paramNorm[ii])
                    paramEnd = math.log10(self.paramEnd[ii]) / math.log10(self.paramNorm[ii])
                    paramInit = random.uniform(paramStart, paramEnd)
                    self.paramInit[ii] = math.pow(10.0, (paramInit * math.log10(self.paramNorm[ii])))
                else:
                    paramStart = self.paramStart[ii] / self.paramNorm[ii]
                    paramEnd = self.paramEnd[ii] / self.paramNorm[ii]
                    paramInit = random.uniform(paramStart, paramEnd)
                    self.paramInit[ii] = paramInit * self.paramNorm[ii]
                # end if
            # end for

            if printOut == True:
                strT = "\n---------------------- RANDOM-IN START ------------------------\n"
                dateT = datetime.datetime.now()
                dateStr = dateT.strftime("%Y-%m-%d %H:%M:%S")
                strT += (dateStr + "\n")

                strT += "Parameter:\t"
                for ii in range(0, paramCount - 1):
                    strT += self.paramName[ii] + "\t"
                # end for
                strT += self.paramName[paramCount - 1] + "\n"

                strT += "InitValue:\t"
                for ii in range(0, paramCount - 1):
                    strT += (self.paramFormat[ii] % self.paramInit[ii]) + "\t"
                # end for
                strT += (self.paramFormat[paramCount - 1] % self.paramInit[paramCount - 1]) + "\n"

                strT += "---------------------------------------------------------------\n"
                print strT
            # end if printOut

        #end if

    # end randomInit

# end slalomDevice
