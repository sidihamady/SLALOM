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
# File:           slalomCore.py
# Type:           Class
# Use:            slalomCore is used throw the included slalom.py startup module
#                 To extend the slalomCore class, do not modify it directly but extend it by...
#                 ...creating a new inherited class. Here, perform only performance tuning and bug fixing.
# ------------------------------------------------------------------------------------------------------

# Calculation
import math
import numpy as np
from scipy import optimize, interpolate, signal
import random

# Control
import subprocess
import datetime, shutil, os, stat, sys, time
import zipfile
import traceback

import itertools

from slalomSimulator import *

def dispError(message, doExit = True, atExit = None, errFilename = None, **atExitArgs):
    """ print out an error message and exit if doExit set to True """
    try:
        if doExit:
            strT = "\n--------------------------- ERROR: ----------------------------\n"
        else:
            strT = "\n-------------------------- WARNING: ---------------------------\n"
        # end if
        strT += message
        if not message.endswith("\n"):
            strT += "\n"
        # end if
        strT +=      "---------------------------------------------------------------\n"
        print strT
        if doExit == False:
            return
        # end if

        if atExit is not None:
            atExit(atExitArgs)
        # end if
        if errFilename is not None:
            fileErr = open(errFilename, 'w')
            fileErr.write(message)
            fileErr.close()
        # end if
    finally:
        if doExit:
            # sys.exit raise SystemExit (inherits from BaseException)
            sys.exit(1)
        # end if
    # end try
# end dispError

class slalomCore(object):
    """ the SLALOM core class """

    def __init__(self, Device = None, pythonInterpreter = None, deviceSimulator = "atlas"):
        """ slalomCore constructor """

        self.__version__ = "Version 1.0 Build 1710"

        self.pythonInterpreter = "python"

        self.simulator = slalomSimulator(name = deviceSimulator)

        self.optimType = ""

        self.isRunning = False
        self.isParamUpdated = False
        self.isInputChecked = False

        self.optimType = ""
        self.minimizeMethodList = ["L-BFGS-B", "SLSQP"]
        self.minimizeMethod = ""
        self.isBound = True
        self.tolerance = 1e-3
        self.jaceps = np.array([])

        # Optimization cache
        self.lastParam = list()
        self.lastOutput = list()
        self.lastParamLimit = 12

        self.mainTitle = ""
        self.pythonInterpreter = ""
        self.inputFilename = ""
        self.paramCount = 0
        self.paramName = []
        self.paramFormat = []
        self.paramFormatShort = []
        self.paramFormatNormalized = []
        self.paramNorm = np.array([])
        self.paramStart = np.array([])
        self.paramEnd = np.array([])
        self.paramInit = np.array([])
        self.paramPoints = []
        self.paramBounds = None
        # Tukey Window (Parameters Weight: decreases near the bounds)
        # If optimum is near the bounds, disable this feature or enlarge domain
        self.paramWeight = False
        self.weightFunc = None
        self.weightAlpha = 0.20
        self.weightPoints = 101
        # optimPoints is used to approximate the jacobian. If increased, the optimisation time will dramatically increase. The default value is 51 and the maximum value is 201.
        self.optimPoints = 51
        self.paramLogscale = []
        self.modelFilename = None

        self.paramOptim = np.array([])
        self.paramNatural = np.array([])
        self.paramCountTotal = 0
        self.paramFormatOutput = ""
        self.maxIter = 0
        self.outputOptimized = 0.0
        self.outputOptimizedx = 0.0
        self.outputOptimizedy = 0.0
        self.outputOptimizedz = 0.0
        self.optimCounter = 1
        self.funcCounter = 1
        self.jacCounter = 0
        self.elapsedTime = 0
        self.delayMin = 0
        self.delayMax = 0
        self.delayMean = 0
        self.counterFormat = '{0:02d}'

        self.guessParam = False
        self.bruteSimul = False

        self.inJac = False

        # output filenames:
        # * these names are the same than the simulator output filenames
        # * before last file = efficiency calculated by simulator
        # * last file = J(V) (for efficiency calculation)
        # * the output file names remain unchanged since at every 
        #   optimization a new output directory is created
        self.outputFilename = [ "simuloutput_all.log",
                                "simuloutput_jvp.log",
                                "simuloutput_pv.log",
                                "simuloutput.log",
                                "simuloutput_spectralresponse_eqe.log",
                                "simuloutput_popt.log",
                                "simuloutput_efficiency.log",
                                "simuloutput_jv.log" ]

        # output filenames description (each output file should have a description)
        self.outputComment = [  "Voltage Sweep Data",
                                "J(V) Characteristic from 0V to VOC (J in mA/cm2)",
                                "P(V) Characteristic (P in mW/cm2)",
                                "PV Performances Data (JSC (mA/cm2), VOC (V), FF, EFF)",
                                "External quantum efficiency",
                                "Optical Power (in mW/cm2)",
                                "PV Efficiency",
                                "J(V) Characteristic (J in mA/cm2)" ]

        self.outputCount = len(self.outputComment)

        # pipe filename (used for the simulator standard output redirection)
        self.verboseFilename = "simuloutput_stdout.txt"

        # log filename: used for the internal optimizer logging
        self.logFilename = "simuloutput_log.txt"

        # weight filename: not used yet
        self.weightFilename = "simuloutput_weight.txt"

        # log filename:
        # * contain the calculated efficiency at every optimization step along with 
        #   the corresponding set of parameters
        self.outputOptimizedFilename = "simuloutput_optimized.txt"

        self.commandFilename = "Optimize.bat" if (os.name == "nt") else "Optimize.sh"

        # internal filenames
        self.stopFilename = "stop.txt"
        self.stoppedFilename = "stopped.txt"
        self.stoppedDone = False
        self.delayFilename = "delay.txt"

        self.currentDir = ""
        self.outputDir = ""
        self.outputRoot = ""
        self.outputDirShort = ""
        self.dirSepChar = '/'

        if (Device is not None) and (pythonInterpreter is not None):
           self.setParam(Device, pythonInterpreter)
        # end if

        return

    # end __init__

    def log(self, strT):
        """ internal logging routine (the significant events are logged in the log file) """

        try:
            print strT
            fileT = open(self.outputDir + self.logFilename, "a")
            fileT.write(strT)
            fileT.close()
        except:
            pass
        # end try

    # end log

    def setCounterFormat(self, maxcount):
        if maxcount < 100:
            self.counterFormat = '{0:02d}'
        elif maxcount >= 100 and maxcount < 1000:
            self.counterFormat = '{0:03d}'
        elif maxcount >= 1000 and maxcount < 10000:
            self.counterFormat = '{0:04d}'
        else:
            self.counterFormat = '{0:07d}'
        # endif
    # end setCounterFormat

    def setInterpreter(self, pythonInterpreter):
        """ set the Python interpreter (usually just 'python') """
        self.pythonInterpreter = pythonInterpreter
    # end setInterpreter

    @staticmethod
    def chmodExec(strFilename):
        """ chmod a+x the simulator launcher """
        statT = os.stat(strFilename)
        os.chmod(strFilename, statT.st_mode | stat.S_IEXEC)
        return
    # end chmodExec

    def checkInput(self):
        """ check if the simulator files (input, C models, etc.) can be accessed """
        if (self.outputCount > 0):
            pathIn = ""
            # Check if the simulator input file contains the correct output filenames
            try:
                pathIn = os.path.join(self.currentDir, self.inputFilename)
                if not os.path.isfile(pathIn):
                    dispError("cannot open input: file not found '%s'" % pathIn,
                        doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
                # end if
                fileT = open("{0}{1}".format(self.currentDir, self.inputFilename), "r")
                foundCounter = 0
                for lineT in fileT:
                    for ii in range(0, self.outputCount):
                        for ll in range(0, len(self.simulator.filedecl)):
                            statementT = self.simulator.filedecl[ll] % self.outputFilename[ii]
                            # syntax should be the same than what defined in slalomSimulator
                            # for Silvaco: outfile=filename (without spaces aroud '=')
                            if (statementT in lineT):
                                foundCounter += 1
                                break
                            # end if
                        # end for
                    # end for
                    if foundCounter == self.outputCount:
                        break
                    # end for
                # end for
                fileT.close()
                if foundCounter != self.outputCount:
                    dispError("Output statements not found in the simulator input file",
                        doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
                # end if
            except Exception as excT:
                # catch only Exception (since sys.exit raise BaseException)
                dispError("Cannot open the simulator input file '%s' %s" % (pathIn, str(excT)),
                    doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
            # end try
        # end if

        self.isInputChecked = True

        return self.isInputChecked

    # end checkInput

    def updatePath(self, bCreateCommand = True):
        """ update/normalize input files """

        # Format simulator input file
        fileT = open(self.currentDir + self.inputFilename, "r")
        fileContent = ""
        for lineT in fileT:
            # Normalize line ending (Silvaco do not run input file if contains CRLF terminated lines)
            lineT = lineT.rstrip("\r\n")
            fileContent += (lineT + "\n")
        # end for
        fileT.close()
        fileT = open(self.outputDir + self.inputFilename, "w")
        fileT.write(fileContent)
        fileT.close()

        # Format model files
        if self.modelCount > 0:
            for ii in range(0, self.modelCount):
                if self.modelFilename[ii] == "":
                    continue
                # end if
                fileT = open(self.currentDir + self.modelFilename[ii], "r")
                fileContent = ""
                for lineT in fileT:
                    # Normalize line ending (Silvaco do not run input file if contains CRLF terminated lines)
                    lineT = lineT.rstrip("\r\n")
                    fileContent += (lineT + "\n")
                # end for
                fileT.close()
                fileT = open(self.outputDir + self.modelFilename[ii], "w")
                fileT.write(fileContent)
                fileT.close()
            # end for
        # end if

        if bCreateCommand == True:
            self.simulator.update(self.simulator.name, self.inputFilename, self.currentDir, self.outputDir, self.verboseFilename)
            strT = ""
            lenT = len(self.simulator.command)
            for ii in range(0, lenT):
                strT += self.simulator.command[ii]
                if (ii < (lenT - 1)):
                    strT += "\n"
                # end if
            # end for
            fileT = open(self.outputDir + self.commandFilename, "w")
            fileT.write(strT)
            fileT.close()
            # chmod a+x self.commandFilename
            self.chmodExec(self.outputDir + self.commandFilename)
        # end if

        return True

    # end updatePath

    def isChecked(self):
        """ input files successfully checked? """
        return (self.isInputChecked and self.isParamUpdated)
    # end isChecked

    @staticmethod
    def printTime(secondsT, short=False):
        """ print the time in a readable form """

        strT = ""
        if (secondsT < 60.0):
            strT = ("%02d" % secondsT) + (" seconds" if not short else " s")
        elif (secondsT < 3600.0):
            strT = ("%.2f" % (secondsT / 60.0)) + (" minutes" if not short else " m")
        else:
            strT = ("%.2f" % (secondsT / 3600.0)) + (" hours" if not short else " h")
        # end if

        return strT

    # end printTime

    def finish(self, errorOccured=True, userStopped=True, x=None, success=None, message=None, nit=None):
        """ print out results at the optimization end """

        try:
            dateT = datetime.datetime.now()
            dateStr = dateT.strftime("%Y-%m-%d %H:%M:%S")

            if errorOccured == False:
                strT = "\n---------------------------------------------------------------\n"
                strT += ("Optimization ended @ " if (userStopped == False) else "Optimization interrupted @ ") + dateStr
                strT += ("\nMAXIMUM Efficiency: %g %%" % self.outputOptimized)
                strT += ("\nWITH Jsc = %g mA/cm2" % self.outputOptimizedx) + (" ; Voc = %.4f" % self.outputOptimizedy) + (
                " ; FF = %.3f %%" % self.outputOptimizedz) + "\nOBTAINED FOR:\n"
                for ii in range(0, self.paramCount - 1):
                    strT += self.paramName[ii] + "\t"
                # end for
                strT += self.paramName[self.paramCount - 1] + "\n"
                for ii in range(0, self.paramCount - 1):
                    strT += (self.paramFormat[ii] % self.paramOptim[ii]) + "\t"
                # end for
                strT += (self.paramFormat[self.paramCount - 1] % self.paramOptim[self.paramCount - 1])
                strT += "\nTotal duration: " + self.printTime(float(self.elapsedTime))
                strT += ("\nNumber of function evaluations: %d" % self.funcCounter)
                if (self.jacCounter >= self.paramCount):
                    strT += (" (%d for the Jacobian approximation)" % self.jacCounter)
                # end if
                strT += "\n---------------------------------------------------------------\n"

                if (x is not None) and (success is not None) and (message is not None):
                    xt = np.zeros(self.paramCount)
                    for ii in range(0, self.paramCount):
                        if self.paramLogscale[ii]:
                            xt[ii] = math.pow(10.0, (x[ii] * math.log10(self.paramNorm[ii])))
                        else:
                            xt[ii] = x[ii] * self.paramNorm[ii]
                    strT += "\n---------------------------------------------------------------\n"
                    strT += "Optimization function" + "(" + self.minimizeMethod + ")" + " output:\n"

                    strT += "Parameter:\t"
                    for ii in range(0, self.paramCount - 1):
                        strT += self.paramName[ii] + "\t"
                    # end for
                    strT += self.paramName[self.paramCount - 1] + "\n"

                    strT += "x (natural):\t"
                    for ii in range(0, self.paramCount - 1):
                        strT += (self.paramFormat[ii] % xt[ii]) + "\t"
                    # end for
                    strT += (self.paramFormat[self.paramCount - 1] % xt[self.paramCount - 1]) + "\n"

                    strT += "x (normalized):\t"
                    for ii in range(0, self.paramCount - 1):
                        strT += (self.paramFormatNormalized[ii] % x[ii]) + "\t"
                    # end for
                    strT += (self.paramFormatNormalized[self.paramCount - 1] % x[self.paramCount - 1]) + "\n"

                    strT += "\nsuccess: " + str(success) + "\n"
                    strT += "\nmessage: " + str(message) + "\n"
                    strT += "\nevaluations: " + str(self.funcCounter)
                    strT += "\n---------------------------------------------------------------\n"
                # end if

                self.log(strT)

            # end if

            strLog = ("# Optimization ended @ " if (userStopped == False) else "# Optimization interrupted @ ") + dateStr + "\n"

            fileOptim = open(self.outputDir + self.outputOptimizedFilename, "a")
            fileOptim.write(strLog)
            fileOptim.close()

            self.log(strLog)

            self.stopSet()

            if self.stoppedDone == False:
                pathStopped = os.path.join(self.outputDir, self.stoppedFilename)
                fileT = open(pathStopped, "w")
                fileT.write(strLog)
                fileT.close()
                self.stoppedDone = True
            # end if

            self.log("\nZipping optimization result files...")
            zipFilename = self.outputRoot + self.outputDirShort + ".zip"
            outFile = zipfile.ZipFile(zipFilename, "w", compression=zipfile.ZIP_DEFLATED)
            dirToZip = self.outputDir.rstrip(self.dirSepChar)
            for (dirPath, dirNames, fileNames) in os.walk(dirToZip):
                for fileName in fileNames:
                    fileAbsolutePath = os.path.join(dirPath, fileName)
                    fileRelativePath = fileAbsolutePath.replace(dirToZip + self.dirSepChar, '')
                    outFile.write(fileAbsolutePath, fileRelativePath)
                # end for
            # end for
            outFile.close()
            self.log("\nZipping done (File: " + self.outputDirShort + ".zip" + ").")

            self.isRunning = False
        except:
            pass
        # end try

        self.isRunning = False

        if self.stoppedDone == False:
            try:
                pathStopped = os.path.join(self.outputDir, self.stoppedFilename)
                fileT = open(pathStopped, "w")
                fileT.write("SLALOM\nStopped\n")
                fileT.close()
                self.stoppedDone = True
            except:
                pass
            # end try
        # end if

        sys.exit(0 if (errorOccured == False) else 1)

    # end finish

    def guess(self):
        """ get the initial parameters set """

        self.guessParam = True
        self.bruteSimul = False

        paramNormalized0 = np.zeros(self.paramCount)
        for ii in range(0, self.paramCount):
            if self.paramLogscale[ii]:
                paramNormalized0[ii] = math.log10(self.paramInit[ii]) / math.log10(self.paramNorm[ii])
            else:
                paramNormalized0[ii] = self.paramInit[ii] / self.paramNorm[ii]
            # end if
        # end for

        self.guessParam = False
        return paramNormalized0

    # end guess

    def isErrorOccurred(self):
        """ check if a simulator error has occurred """

        maxLines = 16383
        curLine = 0
        simulatorError = None
        try:
            pathV = os.path.join(self.outputDir + self.verboseFilename)
            if not os.path.isfile(pathV):
                return  None
            # end if
            iLines = 0;
            fileT = open(self.outputDir + self.verboseFilename, "r")
            for lineT in fileT:
                if (simulatorError is not None):
                    simulatorError += lineT + '\n'
                    iLines += 1
                    if iLines >= 12:
                        return simulatorError
                    # end if
                else:
                    for (name, descr) in self.simulator.error:
                        if lineT.find(name) != -1:
                            simulatorError = name + ': ' + descr + '\n'
                        # end if
                    # end for
                # end if
                curLine += 1
                if curLine >= maxLines:
                    return simulatorError
                # end if
            # end for
            fileT.close()
        except:
            pass
        # end try

        return simulatorError

    # end isErrorOccurred

    def printOutput(self):
        """ print out the simulator output """

        maxLines = 16383
        curLine = 0
        try:
            pathV = os.path.join(self.outputDir + self.verboseFilename)
            if not os.path.isfile(pathV):
                return
            # end if
            fileT = open(self.outputDir + self.verboseFilename, "r")
            strT = "\n# ---------------------- SIMULATOR OUTPUT: ----------------------\n\n"
            print strT
            for lineT in fileT:
                strT += "# " + lineT
                print lineT
                curLine += 1
                if curLine >= maxLines:
                    strT += "\n# SIMULATOR OUTPUT TOO LONG\n"
                    break
                # end if
            # end for
            fileT.close()
            strTT = "\n\n# ---------------------------------------------------------------\n"
            print strTT
            strT += strTT
        except:
            strT = "\n# ----------------------- SIMULATOR ERROR: -----------------------\n"
            strT += "# Check the simulator output for details.\n"
            strT += "\n# ---------------------------------------------------------------\n"
            pass
        # end try

        return strT

    # end printOutput

    def stopSet(self):
        """ check is the user has required the optimization to stop """

        isStopSet = False
        pathStop = os.path.join(self.outputDir, self.stopFilename)
        try:
            if os.path.isfile(pathStop):
                isStopSet = True
                shutil.move(self.outputDir + self.stopFilename, self.outputDir + "_" + self.stopFilename)
            # end if
            if isStopSet:
                pathOf = os.path.join(self.currentDir, "ofname.txt")
                if os.path.isfile(pathOf):
                    os.unlink(pathOf)
                # end if
            # end if
        except:
            pass
        # end try
        return isStopSet

    # end stopSet

    def getOptimizeJac(self, optimFunc):
        """ Construct the Jacobian approximation function. Adapted from the SLSQSP code source (scipy/optimize/slsqp.py) """

        def optimizeJac(x, *args):
            x0 = np.asfarray(x)
            self.inJac = False
            f0 = np.atleast_1d(optimFunc(*((x0,)+args)))
            self.inJac = True
            ixcount = len(x0)
            ifcount = len(f0)
            jac = np.zeros([ixcount, ifcount])
            dx = np.zeros(ixcount)
            for ii in range(ixcount):
                self.log("\nJacobian approximation [%d / %d]..." % (ii + 1, ixcount))
                dx[ii] = self.jaceps[ii]
                jac[ii] = (optimFunc(*((x0+dx,)+args)) - f0) / self.jaceps[ii]
                dx[ii] = 0.0
            # end for
            self.jacCounter += ixcount
            self.inJac = False
            return jac.transpose()
        # end optimizeJac

        return optimizeJac
    # end getOptimizeJac

    def getWeight(self, paramIndex, paramNormalized):
        """ weight/cost function for future use (giving each parameter a weight...) """
        if (self.paramWeight == False) or (self.weightFunc is None) or (self.paramBounds is None) or (paramIndex < 0) or (paramIndex >= self.paramCount):
            return 1.0
        # end if
        icw = len(self.weightFunc)
        if (icw < 7):
            return 1.0
        # end if
        (paramMin, paramMax) = self.paramBounds[paramIndex]
        if (paramMax <= paramMin) or (paramNormalized < paramMin) or (paramNormalized > paramMax):
            return 0.0
        # end if
        tdw = (paramMax - paramMin)
        idx = int(((paramNormalized - paramMin) * float(icw)) / tdw)
        if (idx < 0):
            idx = 0
        elif (idx >= icw):
            idx = icw - 1
        # end if
        return self.weightFunc[idx]
    # end if

    def optimizeFunc(self, paramNormalized):
        """ the optimizer minimization function """

        bShowOutput = ((self.inJac == False) or (self.optimType == "Brute"))

        # If stopFilename exists, stop optimization
        if self.stopSet():
            try:
                self.finish(errorOccured=False, userStopped=True)
            except:
                self.isRunning = False
                sys.exit(1)
            # end try
            return 0.0
        # end if

        for ii in range(0, self.paramCount):
            if self.paramLogscale[ii]:
                self.paramNatural[ii] = math.pow(10.0, (paramNormalized[ii] * math.log10(self.paramNorm[ii])))
            else:
                self.paramNatural[ii] = paramNormalized[ii] * self.paramNorm[ii]
            # end if
        # end for

        # A cache strategy is implemented to avoid redundant calculation.
        try:
            if (self.funcCounter >= 1) and (len(self.lastParam) >= 1):
                tParam = ""
                for ii in range(0, self.paramCount - 1):
                    tParam += (self.paramFormat[ii] % self.paramNatural[ii]) + "\t"
                # end for
                tParam += (self.paramFormat[self.paramCount - 1] % self.paramNatural[self.paramCount - 1])
                if (tParam in self.lastParam):
                    return self.lastOutput[self.lastParam.index(tParam)]
                # end if
            # end if
        except:
            pass
        # end try

        strT = ""

        if (bShowOutput == True):
            if self.guessParam:
                strT = "\n-------------------- GUESS " + (self.counterFormat.format(self.optimCounter)) + " RUNNING -----------------------\n"
            else:
                strT = "\n----------------- OPTIMIZATION " + (self.counterFormat.format(self.optimCounter)) + " RUNNING -------------------\n"
            # end if

            strT += self.title + ": Optimization (" + self.optimType
            if self.optimType == "Optim":
                strT += " " + self.minimizeMethod
            # end if

            strT += ") "
            dateT = datetime.datetime.now()
            dateStr = dateT.strftime("%Y-%m-%d %H:%M:%S")
            strT += (dateStr + "\n")

            strT += "Parameter:\t"
            for ii in range(0, self.paramCount - 1):
                if ((self.paramPoints[ii] > 1) or (self.bruteSimul == False)):
                    strT += "@" + self.paramName[ii] + "\t"
                else:
                    strT += self.paramName[ii] + "\t"
                # end if
            # end for
            if ((self.paramPoints[self.paramCount - 1] > 1) or (self.bruteSimul == False)):
                strT += "@" + self.paramName[self.paramCount - 1] + "\n"
            else:
                strT += self.paramName[self.paramCount - 1] + "\n"
            # end if

            strT += "Natural:\t"
            for ii in range(0, self.paramCount - 1):
                strT += (self.paramFormat[ii] % self.paramNatural[ii]) + "\t"
            # end for
            strT += (self.paramFormat[self.paramCount - 1] % self.paramNatural[self.paramCount - 1]) + "\n"

            strT += "Normalized:\t"
            for ii in range(0, self.paramCount - 1):
                strT += (self.paramFormatNormalized[ii] % paramNormalized[ii]) + "\t"
            # end for
            strT += (self.paramFormatNormalized[self.paramCount - 1] % paramNormalized[self.paramCount - 1])

            strT += "\n---------------------------------------------------------------\n"

            self.log(strT)
        # end if bShowOutput

        ticT = time.time()

        pathIn = os.path.join(self.outputDir, self.inputFilename)
        if not os.path.isfile(pathIn):
            dispError("cannot open input: file not found", doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if

        fileContent = ""

        fileT = open(self.outputDir + self.inputFilename, "r")
        for lineT in fileT:
            # Normalize line ending (Silvaco do not run input file if contains CRLF terminated lines)
            lineT = lineT.rstrip("\r\n")
            lineX = lineT.lstrip("\t ")
            nSpaces = len(lineT) - len(lineX)
            prefixT = lineT[0:nSpaces]

            if (self.simulator.name == "atlas") and lineX.startswith("tonyplot"):
                # skip tonyplot commands
                continue
            # endif

            if not lineX.startswith("#"):
                for ii in range(0, self.paramCount):
                    setparamT = self.simulator.vardeclpre % self.paramName[ii]
                    if lineX.startswith(setparamT):
                        # Need to format parameter to match simulator floating representation
                        strT = self.paramFormatShort[ii] % self.paramNatural[ii]
                        fT = float(strT)
                        lineT = self.simulator.vardecl % (self.paramName[ii], fT)
                        break
                    # end if
                # end for
            # end if

            fileContent += (lineT + "\n")
        # end for

        fileT.close()

        fileT = open(self.outputDir + self.inputFilename, "w")
        fileT.write(fileContent)
        fileT.close()

        # format model files
        if self.modelCount > 0:
            for ii in range(0, self.modelCount):
                if self.modelFilename[ii] == "":
                    break
                # end if
                pathCC = os.path.join(self.outputDir, self.modelFilename[ii])
                if not os.path.isfile(pathCC):
                    dispError("cannot open model file: " + self.modelFilename[ii], doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
                # end if

                fileContent = ""

                fileT = open(self.outputDir + self.modelFilename[ii], "r")
                for lineT in fileT:
                    # Normalize line ending (Silvaco do not run input file if contains CRLF terminated lines)
                    lineT = lineT.rstrip("\r\n")
                    lineX = lineT.lstrip("\t ")
                    nSpaces = len(lineT) - len(lineX)
                    prefixT = lineT[0:nSpaces]

                    bFound = False

                    nn = len(self.paramName)
                    bFound = False
                    if nn > 0:
                        for jj in range(0, nn):
                            setparamT = "double " + self.paramName[jj] + " = "
                            if lineX.startswith(setparamT):
                                strT = self.paramFormat[jj] % self.paramNatural[jj]
                                fT = float(strT)
                                lineT = prefixT + setparamT + ("%g" % fT) + ";"
                                bFound = True
                                break
                            # end if
                        # end for
                    # end if

                    fileContent += (lineT + "\n")
                # end while
                fileT.close()

                fileT = open(self.outputDir + self.modelFilename[ii], "w")
                fileT.write(fileContent)
                fileT.close()
            # end for
        # end if

        # remove the simulator verbose output file before starting optimization
        pathT = os.path.join(self.outputDir, self.verboseFilename)
        try:
            if os.path.isfile(pathT):
                os.unlink(pathT)
            # end if
        except:
            pass
        # end try

        # run optimization
        try:
            tEnv = dict(os.environ)
            subprocess.check_call([self.outputDir + self.commandFilename, ""], shell=True, env=tEnv)
        except subprocess.CalledProcessError, excT:
            try:
                strT = self.printOutput()
                fileOptim = open(self.outputDir + self.outputOptimizedFilename, "a")
                fileOptim.write(strT)
                fileOptim.close()
            except:
                pass
            # end try
            dispError(traceback.format_exc(), doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
            return 0.0
        # end try

        simulatorError = self.isErrorOccurred()
        if (simulatorError is not None):
            try:
                fileOptim = open(self.outputDir + self.outputOptimizedFilename, "a")
                fileOptim.write(simulatorError)
                fileOptim.close()
            except:
                pass
            # end try
            dispError(simulatorError, doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
            return 0.0
        # end if

        # Calculate the efficiency (Very important to be as precise for the optimization algorithm)
        LinesToSkip = 4
        arrVoltage = np.array([])
        arrCurrent = np.array([])
        arrPower = np.array([])
        iLine = 0
        iPoints = 0
        iPVPoints = 0

        pathJV = os.path.join(self.outputDir, self.outputFilename[self.outputCount - 1])
        if not os.path.isfile(pathJV):
            # do not necessarily exit, since the simulator can sometimes diverge for a set of parameters choosen by the optimizer
            dispError("cannot evaluate efficiency: J-V file not found: check the simulator output file (%s)" % self.verboseFilename, doExit = False)
            return 0.0
        # end if

        try:

            iVpos = 0
            fVocx = 0.0
            fV = 0.0
            fVprev = 0.0
            fJ = 0.0
            fJprev = 0.0
            fP = 0.0
            fPprev = 0.0
            DblPrecision = 1e-13
            bStarted = False
            bFirstV = False

            fileT = open(self.outputDir + self.outputFilename[self.outputCount - 1], "r")
            for lineT in fileT:

                if (lineT.startswith("#")):
                    continue
                # end if

                if iLine < LinesToSkip:
                    iLine += 1
                    continue
                # end if

                arrLine = []
                try:
                    arrLine = lineT.split(self.simulator.dataSeparator)
                except:
                    break
                # end try

                if (len(arrLine) < 2):
                    continue
                # end if

                fV = float(arrLine[0])
                fJ = float(arrLine[1])
                fP = math.fabs(fV * fJ)

                if (False == bStarted):
                    bStarted = True
                    fVprev = fV
                    fJprev = fJ
                    fPprev = fP
                    continue
                # end if

                # voltage should be in increasing order
                if (fV <= fVprev):
                    fVprev = fV
                    fJprev = fJ
                    fPprev = fP
                    continue
                # end if

                if (math.fabs(fV) < DblPrecision):
                    fV = 0.0
                # end if

                if (False == bFirstV):
                    bFirstV = True
                    arrVoltage = np.append(arrVoltage, fVprev)
                    arrCurrent = np.append(arrCurrent, fJprev)
                    arrPower = np.append(arrPower, fPprev)
                    continue
                # end if

                arrVoltage = np.append(arrVoltage, fV)
                arrCurrent = np.append(arrCurrent, fJ)
                arrPower = np.append(arrPower, fP)
                iPoints = len(arrVoltage)

                if (iPoints != len(arrCurrent)) or (iPoints != len(arrPower)):
                    # do not necessarily exit, since the simulator can sometimes diverge for a set of parameters choosen by the optimizer
                    dispError("cannot evaluate efficiency: J-V file content not valid: check the simulator output file (%s)" % self.verboseFilename, doExit = False)
                    return 0.0
                # end if

                if ((fV > 0.0) and (fJ > 0.0)):
                    if (iVpos == 0):
                        fVocx = fVprev
                    # end if
                    iVpos += 1
                    if (iVpos > 2):
                        break
                    # end if
                # end if

                if ((fV * fJ) < 0.0):
                    iPVPoints += 1
                #end if

                fVprev = fV

                iLine += 1
            # end for

            fileT.close()

        except:
            dispError("cannot evaluate efficiency: check the simulator output file (%s)" % self.verboseFilename, doExit = True)
            pass
        # end try

        outputT = 0.0
        outputO = 0.0

        # max current in mA/cm2
        fJm = 0.0

        # max voltage in Volts
        fVm = 0.0

        # Fill Factor
        fFF = 0.0

        # Short-circuit current in mA/cm2
        fJsc = 0.0

        # Open-circuit voltage in Volts
        fVoc = 0.0

        # Maximal power in mW/cm2
        Pmax = 0.0

        doCalc = True

        if (iPVPoints < 12):
            doCalc = False
            # do not necessarily exit, since the simulator can sometimes diverge for a set of parameters choosen by the optimizer
            dispError("Cannot evaluate efficiency: J-V curve has less than 12 points with V*J < 0", doExit = False)
            return 0.0
        # end if

        try:
            if doCalc == True:

                windowLen = 8

                # interpolate the J-V data to accurately calculate the efficiency
                funcCurrent = interpolate.interp1d(arrVoltage, arrCurrent, kind='slinear')
                funcPower = interpolate.interp1d(arrVoltage, arrPower, kind='cubic')
                iPointsNew = iPoints * windowLen
                #

                dV = (arrVoltage[iPoints - 1] - arrVoltage[0]) / float(iPointsNew - 1)
                arrVoltageNew = np.arange(arrVoltage[0], arrVoltage[iPoints - 1] + dV, dV)
                iPointsNew = len(arrVoltageNew)

                iC = iPointsNew
                for ii in range(iPointsNew - 1, iPointsNew - windowLen - 1, -1):
                    if (arrVoltageNew[ii] > arrVoltage[iPoints - 1]):
                        iC -= 1
                    else:
                        break
                    # end if
                # end for
                if iC < iPointsNew:
                    arrVoltageNew = np.delete(arrVoltageNew, np.arange(iC, iPointsNew, 1))
                    iPointsNew = len(arrVoltageNew)
                # end for

                arrCurrentNew = funcCurrent(arrVoltageNew)
                arrPowerNew = funcPower(arrVoltageNew)
                dV = arrVoltageNew[1] - arrVoltageNew[0]

                bFoundJsc = False
                bFoundVoc = False
                bFoundPmax = False

                # Find PV parameters
                for ii in range(0, iPointsNew - 1):

                    # Short-circuit current (mA/cm2)
                    if (bFoundJsc == False):
                        if ((arrVoltageNew[ii] < 0.0) and (arrVoltageNew[ii + 1] > 0.0)):
                            fJsc = 0.5 * (arrCurrentNew[ii] + arrCurrentNew[ii + 1])
                            bFoundJsc = True
                            if (bFoundJsc == True) and (bFoundVoc == True) and (bFoundPmax == True):
                                break
                            # end if
                        elif ((arrVoltageNew[ii] >= 0.0) and (arrVoltageNew[ii] <= dV)):
                            fJsc = arrCurrentNew[ii]
                            bFoundJsc = True
                            if (bFoundJsc == True) and (bFoundVoc == True) and (bFoundPmax == True):
                                break
                            # end if
                        # end if
                    # end if

                    # Open-circuit voltage (V)
                    if (bFoundVoc == False):
                        if ((arrCurrentNew[ii] < 0.0) and (arrCurrentNew[ii + 1] > 0.0)):
                            fVoc = 0.5 * (arrVoltageNew[ii] + arrVoltageNew[ii + 1])
                            bFoundVoc = True
                            if (bFoundJsc == True) and (bFoundVoc == True) and (bFoundPmax == True):
                                break
                        elif ((arrCurrentNew[ii] < 0.0) and (arrCurrentNew[ii + 1] >= 0.0)):
                            fVoc = arrVoltageNew[ii + 1]
                            bFoundVoc = True
                            if (bFoundJsc == True) and (bFoundVoc == True) and (bFoundPmax == True):
                                break
                            # end if
                        # end if
                    # end if

                    # Maximum power (mW/cm2)
                    if ((bFoundPmax == False) and (ii >= windowLen) and (ii <= (iPointsNew - windowLen))):
                        if ((arrPowerNew[ii - 2] < arrPowerNew[ii - 1]) and (arrPowerNew[ii - 1] < arrPowerNew[ii]) and (arrPowerNew[ii] > arrPowerNew[ii + 1]) and (arrPowerNew[ii + 1] > arrPowerNew[ii + 2])):
                            fJm = arrCurrentNew[ii]
                            fVm = arrVoltageNew[ii]
                            Pmax = arrPowerNew[ii]
                            bFoundPmax = True
                            if (bFoundJsc == True) and (bFoundVoc == True) and (bFoundPmax == True):
                                break
                            # end if
                        # end if
                    # end if

                    # Direct polarization
                    if (((arrVoltageNew[ii] > 0.0) and (arrCurrentNew[ii] > 0.0)) or ((arrVoltageNew[ii] < 0.0) and (arrCurrentNew[ii] < 0.0))) and bFoundPmax:
                        break
                    # end if
                # end for (Find PV parameters)

                outputT = 0.0

                if (bFoundJsc == False):
                    if ((arrCurrentNew[0] < 0.0) and (arrVoltageNew[0] > 0.0)):
                        fJsc = -arrCurrentNew[0]
                    # end if
                else:
                    fJsc = -fJsc
                # end if

                if (bFoundVoc == False):
                    if ((arrCurrentNew[iPointsNew - 1] < 0.0) and (arrVoltageNew[iPointsNew - 1] > 0.0)):
                        fVoc = arrVoltageNew[iPointsNew - 1]
                    else:
                        if (fVocx > 0.01):
                            fVoc = fVocx
                            bFoundVoc = True
                        # end if
                    # end if
                # end if

                if ((bFoundJsc == True) and (bFoundVoc == True) and (bFoundPmax == True)):
                    fFF = 100.0 * Pmax / math.fabs(fJsc * fVoc)
                # end if

                if ((bFoundJsc == False) or (bFoundVoc == False) or (bFoundPmax == False)):
                    strT = "Cannot evaluate efficiency: "
                    if bFoundJsc:
                        strT += ("  JSC = %.5f mA/cm2" % fJsc)
                    else:
                        strT += "  JSC not found"
                    # end if
                    if bFoundVoc:
                        strT += ("  VOC = %.5f V" % fVoc)
                    else:
                        strT += "  VOC not found"
                    # end if
                    if bFoundPmax:
                        strT += ("  Pmax = %.5f mW/cm2" % Pmax)
                    else:
                        strT += "  Pmax not found"
                        Pmax = 0.0
                    # end if
                    strT += "\n -> increase V-range and/or decrease V-step"
                    dispError(strT, doExit = False)
                # end if

                # AM 1.5 power density ~ 100 mW/cm2 (Atlas default AM 1.5 spectrum gives 100.037 mW/cm2)
                Psolar = 100.037
                outputT = 100.0 * Pmax / Psolar
                if (outputT == 0.0):
                    fJsc = 0.0
                    fVoc = 0.0
                    fFF = 0.0
                # end if

                # efficiency as calculated by the simulator
                if ((bFoundJsc == True) and (bFoundVoc == True) and (bFoundPmax == True)):
                    pathEE = os.path.join(self.outputDir, self.outputFilename[self.outputCount - 2])
                    if not os.path.isfile(pathEE):
                        dispError("cannot evaluate efficiency: '%s' file not found" % pathEE, doExit = False)
                    # end if
                    outputO = 0.0
                    try:
                        fileO = open(self.outputDir + self.outputFilename[self.outputCount - 2], "r")
                        lineO = ""
                        iLT = len("Efficiency=20.123456789123456789123456789")
                        for lineOT in fileO:
                            if lineOT.startswith("Efficiency=") and (len(lineOT) <= iLT):
                                lineO = lineOT
                            # end if
                        # end for
                        fileO.close()
                        if lineO.startswith("Efficiency=") and (len(lineO) <= iLT):
                            outputO = float(lineO.split("=")[1].rstrip(" \t\r\n").lstrip(" \t\r\n"))
                        # end if
                        os.unlink(self.outputDir + self.outputFilename[self.outputCount - 2])
                    except:
                        outputO = 0.0
                        pass
                    # end try
                # end if

                if outputT > self.outputOptimized:
                    self.outputOptimized = outputT
                    self.paramOptim = np.zeros(self.paramCount)
                    for ii in range(0, self.paramCount):
                        self.paramOptim[ii] = self.paramNatural[ii]
                    # end if
                # end if

                if math.fabs(fJsc) > self.outputOptimizedx:
                    self.outputOptimizedx = math.fabs(fJsc)
                # end if

                if math.fabs(fVoc) > self.outputOptimizedy:
                    self.outputOptimizedy = math.fabs(fVoc)
                # end if

                if fFF > self.outputOptimizedz:
                    self.outputOptimizedz = fFF
                # end if

            # end if doCalc
        except:
            dispError(traceback.format_exc(), doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
            pass
        # end try

        durationT = time.time() - ticT
        self.elapsedTime += durationT
        if self.funcCounter == 1:
            self.delayMean = float(durationT)
        else:
            self.delayMean = float(self.elapsedTime) / float(self.funcCounter)
        # end if

        if (self.delayMin == 0) or (durationT < self.delayMin):
            self.delayMin = durationT
        if (self.delayMax == 0) or (durationT > self.delayMax):
            self.delayMax = durationT

        try:
            # Timing information
            pathDelay = os.path.join(self.outputDir, self.delayFilename)
            fileT = open(pathDelay, "w")
            fileT.write("DelayMin = %.1f" % self.delayMin)
            fileT.write("\nDelayMax = %.1f" % self.delayMax)
            fileT.write("\nDelayMean = %.1f" % self.delayMean)
            fileT.close()
        except:
            pass

        strT = ""

        if (bShowOutput == True):
            if self.guessParam:
                strT = "\n---------------------- GUESS " + (self.counterFormat.format(self.optimCounter)) + " DONE ------------------------\n"
            else:
                strT = "\n------------------- OPTIMIZATION " + (self.counterFormat.format(self.optimCounter)) + " DONE --------------------\n"
            # end if

            strT += self.title + ": Optimization (" + self.optimType
            if self.optimType == "Optim":
                strT += " " + self.minimizeMethod
            # end if

            strT += ") "
            dateT = datetime.datetime.now()
            dateStr = dateT.strftime("%Y-%m-%d %H:%M:%S")
            strT += (dateStr + "\n")

            strT += "Parameter:\t"
            for ii in range(0, self.paramCount - 1):
                strT += self.paramName[ii] + "\t"
            # end for
            strT += self.paramName[self.paramCount - 1] + "\n"

            strT += "Natural:\t"
            tParam = ""
            for ii in range(0, self.paramCount - 1):
                strT += (self.paramFormat[ii] % self.paramNatural[ii]) + "\t"
                tParam += (self.paramFormat[ii] % self.paramNatural[ii]) + "\t"
            # end for
            strT += (self.paramFormat[self.paramCount - 1] % self.paramNatural[self.paramCount - 1]) + "\n"
            tParam += (self.paramFormat[self.paramCount - 1] % self.paramNatural[self.paramCount - 1])
            if (len(self.lastParam) >= self.lastParamLimit):
                self.lastParam.pop(0)
            # end if
            self.lastParam.append(tParam)

            strT += "Normalized:\t"
            for ii in range(0, self.paramCount - 1):
                strT += (self.paramFormatNormalized[ii] % paramNormalized[ii]) + "\t"
            # end for
            strT += (self.paramFormatNormalized[self.paramCount - 1] % paramNormalized[self.paramCount - 1])

            strT += "\nPRESENT Efficiency: " + ("%g %%" % outputT) + " (Simulator: " + ("%g %%" % outputO) + ")"
            strT += "\nPRESENT " + ("FF = %08.5f %%" % fFF) + (" ; Jsc = %08.5f mA/cm2" % fJsc) + (" ; Voc = %08.5f V" % fVoc)
            strT += "\nMAXIMUM Efficiency: %g %%" % self.outputOptimized
            strT += "\nThis run duration: " + self.printTime(float(durationT)) + " (mean: " + self.printTime(self.delayMean) + ")"
            strT += "\nElapsed time: " + self.printTime(float(self.elapsedTime))
            strT += "\nNumber of function evaluations: %d" % self.funcCounter
            if self.bruteSimul:
                if self.funcCounter < (self.paramCountTotal - 1):
                    remainingT = (float(self.paramCountTotal) * self.delayMean) - float(self.elapsedTime)
                    strT += "\nEstimated remaining time: " + self.printTime(remainingT)
                # end if
            # end if
            strT += "\n---------------------------------------------------------------\n"

            self.log(strT)

            dateStrCompact = None

            if not self.guessParam:
                dateT = datetime.datetime.now()
                dateStrCompact = dateT.strftime("%Y%m%d-%H%M%S")

                strT = (self.counterFormat.format(self.optimCounter)) + "\t" + dateStrCompact + "\t"

                for ii in range(0, self.paramCount):
                    strT += (self.paramFormat[ii] % self.paramNatural[ii]) + "\t"
                # end for

                strT += ("%08.5f\t" % math.fabs(fJm)) + ("%08.5f\t" % fVm) + ("%08.5f\t" % fFF) + ("%08.5f\t" % fJsc) + ("%08.5f\t" % fVoc) + ("%08.5f" % outputT) + "\n"
                fileOptim = open(self.outputDir + self.outputOptimizedFilename, "a")
                fileOptim.write(strT)
                fileOptim.close()
            # end if

            # in updateOutput, output files are moved
            self.updateOutput(dateStrCompact)
        else:
            # delete output files before the next run
            self.deleteOutput()
        # end if bShowOutput

        if self.inJac == False:
            self.optimCounter += 1
        # end if

        self.funcCounter += 1

        if not self.guessParam:

            if self.paramWeight and self.isBound:
                # Parameters Weight: decreases near the bounds
                fa = 0.0
                fb = 0.0
                for ii in range(0, self.paramCount):
                    ft = (paramNormalized[ii] * paramNormalized[ii])
                    fa += ft
                    fw = self.getWeight(ii, paramNormalized[ii])
                    fb += ft * (fw * fw)
                # end for
                if (fa > 0.0):
                    outputT = outputT * (fb / fa)
                # end if
            # end if

            tOutput = (1.0 - (outputT / 100.0))

            if (len(self.lastOutput) >= self.lastParamLimit):
                self.lastOutput.pop(0)
            # end if
            self.lastOutput.append(tOutput)

            return tOutput

        else:
            return outputT
        # end if

    # end optimizeFunc

    @staticmethod
    def removeOutputFiles(outputDirT):
        """ delete the output directory content (everything in that directory will be deleted!) """
        for fileT in os.listdir(outputDirT):
            pathT = os.path.join(outputDirT, fileT)
            try:
                if os.path.isfile(pathT):
                    os.unlink(pathT)
                elif os.path.isdir(pathT):
                    shutil.rmtree(pathT)
                # end if
            except:
                pass
            # end try
        # end for

        return

    # end removeOutputFiles

    def updateOutputFile(self, outputFilenameOld, outputComment, outputFilenameSuffix):
        """ update/rename the output files"""

        outputFilenameNew = ""

        # Files in the output directory
        try:
            pathOld = os.path.join(self.outputDir, outputFilenameOld)
            if not os.path.isfile(pathOld):
                return
            # end if
            fileT = open(self.outputDir + outputFilenameOld, "r")
            fileT.close()
            # Exists... change filename and shutil.move it to the outpur dir
            strT1 = outputFilenameOld.split(".")[0]
            strT2 = outputFilenameOld.split(".")[1]
            outputFilenameNew = strT1 + "_" + (self.counterFormat.format(self.optimCounter)) + "_" + outputFilenameSuffix + "." + strT2
            shutil.move(self.outputDir + outputFilenameOld, self.outputDir + outputFilenameNew)
        except:
            return
        # end try

        try:
            # Save optimization infos
            fileHeader = "# " + self.title + "\n# "
            fileHeader += outputComment + "\n# "
            for ii in range(0, self.paramCount):
                fileHeader += self.paramName[ii]
                if (ii < (self.paramCount - 1)):
                    fileHeader += "\t"
                # end if
            # end for
            fileHeader += "\n# "
            for ii in range(0, self.paramCount):
                fileHeader += (self.paramFormat[ii] % self.paramNatural[ii])
                if (ii < (self.paramCount - 1)):
                    fileHeader += "\t"
                # end if
            # end for
            fileHeader += "\n"

            fileT = open(self.outputDir + outputFilenameNew, "r")
            lll = False
            fileContent = ""
            for lineT in fileT:
                if lll == False:
                    if lineT.startswith(self.simulator.header):
                        fileContent = lineT + fileHeader
                    else:
                        fileContent = fileHeader + lineT
                    lll = True
                    continue
                # end if
                fileContent += lineT
            # end for
            fileT.close()
            fileContent += "\n"
            fileT = open(self.outputDir + outputFilenameNew, "w")
            fileT.write(fileContent)
            fileT.close()
        except Exception as excT:
            # catch only Exception (since sys.exit raise BaseException)
            dispError(traceback.format_exc(), doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
            pass
        # end try

        return

    # end updateOutputFile

    def updateOutput(self, dateStrCompact):
        """ update the simulator output files """

        if dateStrCompact is None:
            dateT = datetime.datetime.now()
            dateStrCompact = dateT.strftime("%Y%m%d-%H%M%S")
        # end if

        for ii in range(0, self.outputCount):
            self.updateOutputFile(self.outputFilename[ii], self.outputComment[ii], dateStrCompact)
        # end for

        return

    # end updateOutput

    def deleteOutput(self):
        """ delete the simulator output files """

        for ii in range(0, self.outputCount):
            pathT = os.path.join(self.outputDir, self.outputFilename[ii])
            try:
                if os.path.isfile(pathT):
                    os.unlink(pathT)
                # end if
            except:
                pass
            # end try
        # end for

        return

    # end deleteOutput

    def prepare(self):
        """ prepare the optimization """

        if self.isRunning:
            return False
        # end if

        if not self.isChecked():
            dispError("Simulator path and parameters not up to date",
                        doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if

        if not self.updatePath():
            dispError("Simulator path cannot be updated", doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if

        self.optimCounter = 1
        self.funcCounter = 1
        self.jacCounter = 0
        self.elapsedTime = 0
        self.isRunning = True

        self.stopSet()

        # remove the simulator verbose output file
        pathT = os.path.join(self.outputDir, self.verboseFilename)
        try:
            if os.path.isfile(pathT):
                os.unlink(pathT)
            # end if
        except:
            pass
        # end try

        # remove the simulator output files
        for ii in range(0, self.outputCount):
            pathT = os.path.join(self.outputDir, self.outputFilename[ii])
            try:
                if os.path.isfile(pathT):
                    os.unlink(pathT)
                # end if
            except:
                pass
            # end try
        # end for

        self.optimCounter = 1
        self.funcCounter = 1
        self.elapsedTime = 0
        dateT = datetime.datetime.now()
        dateStr = dateT.strftime("%Y-%m-%d %H:%M:%S")

        strT = "# ---------------------------------------------------------------\n"
        strT += "# " + self.title + "\n# Optimization (" + self.optimType
        if self.optimType == "Optim":
            strT += " " + self.minimizeMethod
        # end if
        strT += ") started @ "
        strT += dateStr
        if self.optimType == "Optim":
            strT += ("\n# With tolerance = %g" % self.tolerance)
            strT += (" and jaceps = [ %.5f" % self.jaceps[0])
            if self.paramCount > 1:
                strT += ("  %.5f" % self.jaceps[1])
            # end if
            if self.paramCount > 2:
                strT += ("  %.5f" % self.jaceps[2])
            # end if
            if self.paramCount > 3:
                strT += ("  %.5f" % self.jaceps[3])
            # end if
            if self.paramCount > 4:
                strT += ("  %.5f" % self.jaceps[4])
            # end if
            if self.paramCount > 5:
                strT += " ..."
            # end if
            strT += " ]"
            if self.paramWeight and self.isBound:
                strT += " Weighted"
            # end if
        # end if
        strT += "\n# Parameter:\t"
        for ii in range(0, self.paramCount - 1):
            strT += self.paramName[ii] + "\t"
        # end for
        strT += self.paramName[self.paramCount - 1] + "\n"
        strT += "# StartValue:\t"
        for ii in range(0, self.paramCount - 1):
            strT += (self.paramFormat[ii] % self.paramStart[ii]) + "\t"
        # end for
        strT += (self.paramFormat[self.paramCount - 1] % self.paramStart[self.paramCount - 1]) + "\n"
        strT += "# EndValue:  \t"
        for ii in range(0, self.paramCount - 1):
            strT += (self.paramFormat[ii] % self.paramEnd[ii]) + "\t"
        # end for
        strT += (self.paramFormat[self.paramCount - 1] % self.paramEnd[self.paramCount - 1]) + "\n"
        strT += "# InitValue: \t"
        for ii in range(0, self.paramCount - 1):
            strT += (self.paramFormat[ii] % self.paramInit[ii]) + "\t"
        # end for
        strT += (self.paramFormat[self.paramCount - 1] % self.paramInit[self.paramCount - 1]) + "\n"
        strT += "# NormValue: \t"
        for ii in range(0, self.paramCount - 1):
            strT += (self.paramFormat[ii] % self.paramNorm[ii]) + "\t"
        # end for
        strT += (self.paramFormat[self.paramCount - 1] % self.paramNorm[self.paramCount - 1])
        if self.optimType == "Brute":
            strT += "\n# Points:   \t"
            for ii in range(0, self.paramCount - 1):
                strT += ("%9s" % self.paramPoints[ii]) + "\t"
            # end for
            strT += ("%9s" % self.paramPoints[self.paramCount - 1])
        # end if
        strT += "\n# ---------------------------------------------------------------\n\n"
        self.log(strT)

        fileOptim = open(self.outputDir + self.outputOptimizedFilename, "w")
        fileOptim.write(strT)
        fileOptim.close()

        return True

    # end prepare

    def start(self, optimType):
        """ start the optimization """

        if optimType == "Snap":
            self.startSnapshot()
        elif optimType == "Brute":
            self.startBrute()
        elif optimType == "Optim":
            self.startOptim()
        else:
            dispError("Specify the optimType to \"Brute\", \"Snap\" or \"Optim\"", doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        #end if

    # end start

    def startOptim(self):
        """ start the optimization """

        self.optimType = "Optim"

        self.setCounterFormat(maxcount = 2 * self.optimPoints)

        tStart = 0.0
        tEnd = 0.0
        tRangeMin = 0.0
        tEps = 5.0 * self.tolerance

        self.jaceps = np.zeros(self.paramCount)

        self.paramBounds = list() if self.isBound else None

        if self.paramWeight and self.isBound:
            # Tukey Window (Parameters Weight: decreases near the bounds)
            # If optimum is near the bounds, disable this feature or enlarge domain
            nn = self.weightPoints
            aa = self.weightAlpha
            wn = np.arange(0, nn)
            wm = nn % 2
            ww = int(np.floor(aa * (float(nn - 1)) / 2.0))
            wn1 = wn[0 : ww + 1]
            wn2 = wn[ww + 1 : nn - ww - 1]
            wn3 = wn[nn - ww - 1 :]
            ww1 = 0.5 * (1.0 + np.cos(np.pi * (-1.0 + (2.0 * wn1 / aa / (nn - 1)))))
            ww2 = np.ones(wn2.shape)
            ww3 = 0.5 * (1.0 + np.cos(np.pi * ((-2.0 / aa) + 1.0 + (2.0 * wn3 / aa / (nn - 1)))))
            self.weightFunc = np.concatenate((ww1, ww2, ww3))

            # Save the weight window
            try:
                icw = len(self.weightFunc)
                if (icw >= 7):
                    fileT = open(self.outputDir + self.weightFilename, "w")
                    strT = "# " + self.title + "\n"
                    strT += "# Tukey Window (Parameters Weight)\n"
                    for ii in range(0, icw):
                        strT += ("\n%d\t%g" % (ii, self.weightFunc[ii]))
                    # end for
                    fileT.write(strT)
                    fileT.close()
                # end if
            except:
                pass
            # end try

        else:
            self.weightFunc = None
        # end if

        strT = "Index\tTime\t"

        for ii in range(0, self.paramCount):
            if self.paramLogscale[ii]:
                tStart = math.log10(self.paramStart[ii]) / math.log10(self.paramNorm[ii])
                tEnd = math.log10(self.paramEnd[ii]) / math.log10(self.paramNorm[ii])
            else:
                tStart = self.paramStart[ii] / self.paramNorm[ii]
                tEnd = self.paramEnd[ii] / self.paramNorm[ii]
            # end if
            if (ii == 0) or ((tEnd - tStart) < tRangeMin):
                tRangeMin = tEnd - tStart
            # end if

            self.jaceps[ii] = (tEnd - tStart) / float(self.optimPoints - 1)

            # tolerance should be kept less than eps
            if self.jaceps[ii] <= self.tolerance:
                self.tolerance = 0.2 * self.jaceps[ii]
            # end if

            if self.isBound:
                self.paramBounds.append((tStart, tEnd))
            # end if
            strT += self.paramName[ii] + "\t"
        # end for

        if tRangeMin < 1e-9:
            return False
        # end if

        tEps = tRangeMin / float(self.optimPoints - 1)

        # tolerance should be kept less than eps
        if tEps <= self.tolerance:
            self.tolerance = 0.2 * tEps
        # end if

        if not self.prepare():
            return False
        # end if

        strT += "Jm(mA/cm2)\tVm(V)\tFF(%)\tJsc(mA/cm2)\tVoc(V)\tEfficiency\n"
        fileOptim = open(self.outputDir + self.outputOptimizedFilename, "a")
        fileOptim.write(strT)
        fileOptim.close()

        self.optimCounter = 1
        self.funcCounter = 1
        self.jacCounter = 0
        self.guessParam = False
        self.bruteSimul = False

        outX = None
        outSuccess = None
        outMessage = None
        outNit = None

        # Choose the initial values
        paramNormalized0 = self.guess()

        if self.isBound:
            try:
                outResult = optimize.minimize(self.optimizeFunc, paramNormalized0, method=self.minimizeMethod, jac=self.getOptimizeJac(self.optimizeFunc), bounds=self.paramBounds, tol=self.tolerance, options={ 'eps': tEps, 'maxiter': self.maxIter, 'disp': False, 'ftol': self.tolerance })
                outX = outResult.x
                outSuccess = outResult.success
                outMessage = outResult.message
                outNit = outResult.nit
            except Exception as excT:
                # catch only Exception (since sys.exit raise BaseException)
                if self.stoppedDone is False:
                    dispError(traceback.format_exc(), doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
                # end if
            # end try
        else:
            # not bound methods
            try:
                outResult = optimize.minimize(self.optimizeFunc, paramNormalized0, method=self.minimizeMethod, jac=False, tol=self.tolerance, options={ 'maxiter': self.maxIter, 'disp': False })
                outX = outResult.x
                outSuccess = outResult.success
                outMessage = outResult.message
                outNit = outResult.nit
            except Exception as excT:
                # catch only Exception (since sys.exit raise BaseException)
                dispError(traceback.format_exc(), doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
            # end try
        # end if

        self.finish(errorOccured=False, userStopped=False, x=outX, success=outSuccess, message=outMessage, nit=outNit)

        return True

    # end startOptim

    def startSnapshot(self):
        """ start the optimization (Snap: one calculation for the initial parameters set) """

        self.optimType = "Snap"

        self.setCounterFormat(maxcount = 2)

        if not self.prepare():
            return False
        # end if

        strT = "Index\tTime\t"
        for ii in range(0, self.paramCount):
            strT += self.paramName[ii] + "\t"
        # end for

        strT += "Jm(mA/cm2)\tVm(V)\tFF(%)\tJsc(mA/cm2)\tVoc(V)\tEfficiency\n"
        fileOptim = open(self.outputDir + self.outputOptimizedFilename, "a")
        fileOptim.write(strT)
        fileOptim.close()

        self.optimCounter = 1
        self.funcCounter = 1
        self.jacCounter = 0
        self.guessParam = False
        self.bruteSimul = True

        paramNormalized = np.zeros(self.paramCount)

        for ii in range(0, self.paramCount):
            self.paramNatural[ii] = self.paramInit[ii]
            if self.paramLogscale[ii]:
                paramNormalized[ii] = math.log10(self.paramNatural[ii]) / math.log10(self.paramNorm[ii])
            else:
                paramNormalized[ii] = self.paramNatural[ii] / self.paramNorm[ii]
            # end if
        # end for

        # Run the optimization
        self.optimizeFunc(paramNormalized)

        self.finish(errorOccured=False, userStopped=False)

    # end startSnapshot

    # create the grid for the brute force iterations
    def doGrid(self, arrP, tR, tGrid):
        ns = arrP.shape[0]
        ms = tGrid.shape[0] // (tR * ns)
        for n in range(ns):
            tVal = arrP[n]
            for k in range(tR):
                for m in range(ms):
                    idx = (k * ns * ms) + (n * ms) + m
                    tGrid[idx] = tVal
                # end for
            # end for
        # end for
    # end doGrid

    def getGrid(self, arrParams):
        arrParams = [np.array(tt) for tt in arrParams]
        arrShapes = [tt.shape[0] for tt in arrParams]
        tType = arrParams[0].dtype
        na = len(arrParams)
        ns = np.prod(arrShapes)
        tGrid = np.zeros((ns, na), dtype=tType)
        tRep = np.cumprod([1] + arrShapes[:-1])
        for ii in range(na):
            self.doGrid(arrParams[ii], tRep[ii], tGrid[:, ii])
        # end for
        iCount = 10 * ns * na
        if iCount < 10:
            iCount = 10
        # end if
        self.setCounterFormat(iCount)
        return tGrid
    # end getGrid

    def startBrute(self):
        """ start the optimization (brute force) """

        self.optimType = "Brute"

        if not self.prepare():
            return False
        # end if

        strT = "Index\tTime\t"
        for ii in range(0, self.paramCount):
            strT += self.paramName[ii] + "\t"
        # end for

        strT += "Jm(mA/cm2)\tVm(V)\tFF(%)\tJsc(mA/cm2)\tVoc(V)\tEfficiency\n"
        fileOptim = open(self.outputDir + self.outputOptimizedFilename, "a")
        fileOptim.write(strT)
        fileOptim.close()

        self.optimCounter = 1
        self.funcCounter = 1
        self.jacCounter = 0
        self.guessParam = False
        self.bruteSimul = True

        paramNormalized = np.zeros(self.paramCount)

        dateT = datetime.datetime.now()
        dateStr = dateT.strftime("%Y-%m-%d %H:%M:%S")

        # For ... for all parameters, if not fixed
        # Limited to 5 parameters
        if self.paramCount > 5:
            strT = "\n---------------------------------------------------------------\n"
            strT += " The number of parameters is limited to 5 in the Brute optimization"
            strT += dateStr
            strT += "\n---------------------------------------------------------------\n"
            self.log(strT)
            try:
                pathStopped = os.path.join(self.outputDir, self.stoppedFilename)
                fileT = open(pathStopped, "w")
                fileT.write("SLALOM\nStopped\n")
                fileT.close()
            except:
                pass
            # end try
            sys.exit(0)
        # end if

        self.paramBounds = list()
        tStart = 0.0
        tEnd = 0.0
        tInit = 0.0
        tStep = 0.0
        for ii in range(0, self.paramCount):
            if self.paramLogscale[ii]:
                tStart = math.log10(self.paramStart[ii]) / math.log10(self.paramNorm[ii])
                tEnd = math.log10(self.paramEnd[ii]) / math.log10(self.paramNorm[ii])
                tInit = math.log10(self.paramInit[ii]) / math.log10(self.paramNorm[ii])
            else:
                tStart = self.paramStart[ii] / self.paramNorm[ii]
                tEnd = self.paramEnd[ii] / self.paramNorm[ii]
                tInit = self.paramInit[ii] / self.paramNorm[ii]
            # end if
            if self.paramPoints[ii] > 1:
                tStep = (tEnd - tStart) / float(self.paramPoints[ii] - 1)
                arr = np.array([])
                for jj in range(0, self.paramPoints[ii]):
                    arr = np.append(arr, tStart + float(jj) * tStep)
                # end for
                self.paramBounds.append(arr)
            else:
                self.paramBounds.append(np.array([tInit]))
            # end if
        # end for

        paramNormalizedGrid = self.getGrid(self.paramBounds)
        for paramNormalized in paramNormalizedGrid:
            self.optimizeFunc(paramNormalized)
        # end for

        self.finish(errorOccured=False, userStopped=False)
        self.bruteSimul = False

        return True

    # end startBrute

    def getMinimizeMethod(self):
        return self.minimizeMethod
    # end getMinimizeMethod

    def setMinimizeMethod(self, minimizeMethod, maxIter = 100, tolerance = 1e-3, optimPoints = 51):
        """ set the optimization method ('L-BFGS-B' or 'SLSQP') """
        
        if (maxIter >= 2) and (maxIter <= 1024):
            self.maxIter = maxIter
        # end if

        if (tolerance >= 1e-6) and (tolerance <= 1.0):
            self.tolerance = tolerance
        # end if

        # optimPoints is used to approximate the jacobian. If increased, the optimisation time will dramatically increase. The default value is 51 and the maximum value is 201.
        if (optimPoints < 11):
            self.optimPoints = 11
        elif (optimPoints > 201):
            self.optimPoints = 201
        else:
            self.optimPoints = optimPoints
        # end if

        self.weightPoints = self.optimPoints * 2

        if minimizeMethod in self.minimizeMethodList:
            self.minimizeMethod = minimizeMethod
            if (self.minimizeMethod == "L-BFGS-B") or (self.minimizeMethod == "SLSQP"):
                self.isBound = True
            else:
                self.isBound = False
            # end if
        else:
            strT = minimizeMethod + " unknown. Supported algorithms: "
            for ii in range(0, len(self.minimizeMethodList)):
                strT += self.minimizeMethodList[ii] + "  "
            # end for
            dispError(strT, doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if
    # end setMinimizeMethod

    def getRunning(self):
        return self.isRunning
    # end getRunning

    def getParamOptim(self):
        return self.paramOptim
    # end getParamOptim

    def getOutputOptimized(self):
        return self.outputOptimized
    # end getOutputOptimized

    def setTitle(self, title):
        """ set the optimization title """

        if self.isRunning:
            return
        # end if

        self.title = title
        return

    # end setTitle

    def setPath(self, Device):
        """ set directory and optimization files information """

        if self.isRunning:
            return False
        #end if

        self.currentDir = Device.currentDir
        dirT = os.path.dirname(self.currentDir)
        if not os.path.exists(dirT):
            dispError("Directory not found: " + self.currentDir, doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if

        # Output directory
        self.outputDir = Device.outputDir
        self.outputRoot = self.outputDir
        self.outputDirSuffix = "_" + (Device.deviceType if Device.deviceType else "User")
        dateT = datetime.datetime.now()
        outputDirName = dateT.strftime("%Y%m%d_%H%M")
        if self.outputDirSuffix is not None:
            outputDirName += self.outputDirSuffix
        # end if
        self.outputDirShort = outputDirName
        self.outputDir += outputDirName + self.dirSepChar
        dirT = os.path.dirname(self.outputDir)
        if not os.path.exists(dirT):
            os.makedirs(dirT)
        # end if
        if not os.path.exists(dirT):
            dispError("Directory not found and cannot be created: " + self.outputDir, doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if

        self.inputFilename = Device.inputFilename
        if not os.path.exists(self.currentDir + self.inputFilename):
            dispError("File not found: " + (self.currentDir + self.inputFilename), doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if

        fileT = open(Device.currentDir + "ofname.txt", "w")
        fileT.write(self.outputDir + self.outputOptimizedFilename)
        fileT.close()

        return self.checkInput()

    # end setPath

    def getOutputDir(self):
        return self.outputDir
    # end getOutputDir

    # outputOptimizedFilename is used to plot in 'realtime' the variation of the efficiency during the optimization
    def getOptimizedFilename(self):
        return os.path.join(self.outputDir, self.outputOptimizedFilename)
    # end getOptimizedFilename

    def setParam(self, Device, pythonInterpreter):
        """ set the main optimization parameters """

        if self.isRunning:
            return False
        # end if

        self.setInterpreter(pythonInterpreter)

        self.setTitle(Device.mainTitle)

        if self.setPath(Device) == False:
            return False
        # end if

        lenT = len(Device.paramName)
        if (lenT < 1) or (lenT > 20) or (lenT != len(Device.paramFormat)) or (lenT != len(Device.paramStart)) or (
            lenT != len(Device.paramEnd)) or (lenT != len(Device.paramInit)) or (lenT != len(Device.paramLogscale)):
            dispError("Invalid parameters (setParam)", doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if

        self.paramCount = lenT

        self.paramOptim = np.zeros(self.paramCount)
        self.paramNatural = np.zeros(self.paramCount)

        self.paramName = []
        self.paramUnit = []
        self.paramFormat = []
        self.paramFormatShort = []
        self.paramFormatNormalized = []
        self.paramNorm = np.array([])
        self.paramStart = np.array([])
        self.paramEnd = np.array([])
        self.paramPoints = []
        self.paramInit = np.array([])
        self.paramLogscale = []
        for ii in range(0, self.paramCount):
            self.paramName.append(Device.paramName[ii])
            self.paramUnit.append(Device.paramUnit[ii])
            self.paramFormat.append(Device.paramFormat[ii])
            self.paramFormatShort.append(Device.paramFormatShort[ii])
            self.paramFormatNormalized.append(Device.paramFormatNormalized[ii])
            self.paramNorm = np.append(self.paramNorm, Device.paramNorm[ii])
            self.paramStart = np.append(self.paramStart, Device.paramStart[ii])
            self.paramEnd = np.append(self.paramEnd, Device.paramEnd[ii])
            if (Device.paramPoints[ii] >= 1) and (Device.paramPoints[ii] <= 100):
                self.paramPoints.append(Device.paramPoints[ii])
            # end if
            self.paramInit = np.append(self.paramInit, Device.paramInit[ii])
            self.paramLogscale.append(Device.paramLogscale[ii])
        # end for

        self.paramWeight = Device.paramWeight

        self.paramFormatOutput = Device.paramFormatOutput

        if Device.modelFilename:
            self.modelCount = len(Device.modelFilename)
            if self.modelCount < 1:
                dispError("modelFilename array size not valid", doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
            # end if
            self.modelFilename = []
            nn = 0
            for ii in range(0, self.modelCount):
                self.modelFilename.append(Device.modelFilename[ii])
                if self.modelFilename[ii] == "":
                    continue
                # end if
                if not os.path.exists(self.currentDir + self.modelFilename[ii]):
                    dispError("File not found: " + (self.currentDir + self.modelFilename[ii]), doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
                # end if
            # end for
        else:
            self.modelFilename = None
            self.modelCount = 0
        # end if

        self.isParamUpdated = True

        return self.isParamUpdated

    # end setParam

    def setParamInit(self, paramInit):
        """ set main initial parameters """

        if self.isRunning:
            return False
        # end if

        lenT = len(paramInit)
        if (lenT < 1) or (lenT > 20) or (lenT != len(self.paramFormat)) or (lenT != len(self.paramStart)) or (
            lenT != len(self.paramEnd)) or (lenT != len(self.paramName)) or (lenT != len(self.paramLogscale)):
            dispError("Invalid parameters (setParamInit)", doExit = True, atExit = self.finish, errFilename = self.currentDir + 'errlog.txt')
        # end if

        self.paramInit = np.array([])
        for ii in range(0, self.paramCount):
            self.paramInit = np.append(self.paramInit, paramInit[ii])
        # end for

        return True

    # end setParam

    @staticmethod
    def maxDim():
        return 1024
    # end maxDim

# end slalomCore

# class to disable standard output buffering
class UnbufferedStdout(object):

    def __init__(self, stream):
        self.stream = stream
    # end __init__

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
    # end __getattr__

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    # end write

# end UnbufferedStdout
