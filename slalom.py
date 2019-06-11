#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================================
# SLALOM - Open-Source Solar Cell Multivariate Optimizer
# Copyright(C) 2012-2019 Sidi OULD SAAD HAMADY (1,2,*) and Nicolas FRESSENGEAS (1,2). All rights reserved.
# (1) Université de Lorraine, Laboratoire Matériaux Optiques, Photonique et Systèmes, Metz, F-57070, France
# (2) Laboratoire Matériaux Optiques, Photonique et Systèmes, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France
# (*) sidi.hamady@univ-lorraine.fr
# SLALOM source code is available to download from:
# https://github.com/sidihamady/SLALOM
# https://hal.archives-ouvertes.fr/hal-01897934
# http://www.hamady.org/photovoltaics/slalom_source.zip
# Cite as: S Ould Saad Hamady and N Fressengeas, EPJ Photovoltaics, 9:13, 2018.
# See Copyright Notice in COPYRIGHT
# ======================================================================================================

# ------------------------------------------------------------------------------------------------------
# File:           slalom.py
# Type:           Module
# Purpose:        Startup module:
#                 * set the parameters to optimize
#                 * set the optimization method
# ------------------------------------------------------------------------------------------------------

from slalomCore import *
from slalomDevice import *

import getopt

print('\nSLALOM - Open-Source Solar Cell Multivariate Optimizer\n'
    +   'Copyright(C) 2012-2019 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.\n'
    +   '(1) Universite de Lorraine, LMOPS, Metz, F-57070, France\n'
    +   '(2) LMOPS, CentraleSupelec, Universite Paris-Saclay, Metz, F-57070, France\n'
    +   '(*) sidi.hamady@univ-lorraine.fr\n'
    +   slalomVersion + '\n'
    +   'SLALOM source code is available to download here: https://github.com/sidihamady/SLALOM \n'
    +   'Cite as: S Ould Saad Hamady and N Fressengeas, EPJ Photovoltaics, 9:13, 2018. \n'
    +   'See Copyright Notice in COPYRIGHT\n')

# ======================================================================================================
# The device parameters are grouped here
# <START-Parameters>

# the used backend solar cell simulator.
# by default set to "atlas", the simulator from Silvaco(r) company,...
# ... or "tibercad", the simulator from TiberLAB(r)
deviceSimulator = "atlas"

# currentDir is the name of the directory where the simulator input files remain:
# it can be set to a permanent directory name for a specific project.
# the dir name should be ended with the path separator ('/' under Linux)
#currentDir = "/home/sidi/TCAD/SLALOM/Device/Silvaco/"
currentDir = "N:\\TCAD\\SLALOM\\Device\\Silvaco\\"

# remoteDir is the name of the remote directory used when using SSH to connect...
# ...to a remote server where the simulator is installed.
# the dir name should be ended with the path separator ('/' under Linux)
remoteDir = ""#"/home/sidi/SLALOM/Device/Silvaco/"

# the SSH host used to connect to the server where the Silvaco, tiberCAD or other simulator tools are installed
# set remoteSSHhost to None if the Silvaco, tiberCAD or other simulator tools are installed locally...
# ...or something like "user@remoteserver".
# the SSH connexion should use auth keys, not password, for security reasons.
# refer to the guide (Guide/slalom_guide.pdf) on how to configure SSH.
remoteSSHhost = ""#"sidi@efprimix"

# It is useful, for every project, to define a set of devices
# (e.g. "InGaN_PN", CZTS", etc.) for easier and more robust optimization work.
# The devices are defined in the slalomDevice class.
# Set deviceType to a predefined device (included in slalomDevice.py)...
# ...or set it to None and define the parameters in the optimizer GUI.
deviceType = "InGaN_Schottky"

# The optimization mode: "Brute" (brute force), "Optim" (optimization) or "Snap" (one point)
optimType = "Optim"

# The optimization method: "L-BFGS-B", "SLSQP" or "Bayes"
minimizeMethod = "SLSQP"

# The maximum number of iterations
maxIter = 100

# Set to True to start the optimization with a random point
randomInit = False

# Set to True to delete the output directory and all its content before optimization
clearOutputDir = False

# slalomMonitor:
# set monitorRemoteSSHhost to None to monitor locally (client=monitor and server=optimizer on the same machine)...
# ...or something like "user@remoteserver" to monitor remotely (client and server on different machines).
# the ssh connexion should use auth keys, not password, for security reasons.
monitorRemoteSSHhost = None

dirSepChar = '\\' if ('\\' in currentDir) else '/'

# set to True to enable the SLALOM GUI
enableGUI = True

# command line arguments: python slalom.py --enableGUI --currentDir ... --remoteDir ... --remoteSSH ... --deviceType ... --optimType ... --minimizeMethod ...
# examples:
# python slalom.py --enableGUI No
# python slalom.py --currentDir "N:\\TCAD\\SLALOM\\Device\\Silvaco\\" --remoteDir "/home/sidi/SLALOM/Device/Silvaco/" --remoteSSH user@slalom --deviceType InGaN_PN --optimType Optim --minimizeMethod SLSQP

argc = len(sys.argv) - 1

if argc >= 1:
    isValid = True
    errMsg = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], None, ["enableGUI=", "deviceSimulator=", "currentDir=", "remoteDir=", "remoteSSH=", "deviceType=", "optimType=", "minimizeMethod="])
        print ("\n# ------------------ Command Line Arguments ---------------------")
        for opt, arg in opts:
            if opt == "--enableGUI":
                arg = arg.lower()
                enableGUI = False if ((arg == "no") or (arg == "false")) else True
                print("# enableGUI: " + str(enableGUI))
            elif opt == "--deviceSimulator":
                if arg.lower() in ("atlas", "tibercad"):
                    deviceSimulator = "atlas" if (arg.lower() == "atlas") else "tibercad"
                    print("deviceSimulator: " + deviceSimulator)
                # end if
            elif opt == "--currentDir":
                if os.path.isdir(arg):
                    currentDir = arg
                    dirSepChar = '\\' if ('\\' in currentDir) else '/'
                    if not currentDir.endswith(dirSepChar):
                        currentDir += dirSepChar
                    #end if
                    print("currentDir: " + currentDir)
                else:
                    isValid = False
                    errMsg = "currentDir: invalid directory '%s'\n" % arg
                # end if
            elif opt == "--remoteDir":
                # the remote directory should belongs to a user account in the home directory
                # the remote server is always under Linux
                if arg.startswith("C:/Program Files/Git"):
                    # gitbash under Windows prepend the local Git dir to the home path. Remove it.
                    arg = arg[len("C:/Program Files/Git"):]
                # end if
                if arg.startswith("/home/"):
                    remoteDir = arg
                    if not remoteDir.endswith('/'):
                        remoteDir += '/'
                    #end if
                    print("remoteDir " + remoteDir)
                else:
                    isValid = False
                    errMsg = "remoteDir: invalid directory '%s'\n" % arg
                # end if
                #end if
            elif opt == "--remoteSSH":
                if ('@' in arg) and (len(arg) >= 5):
                    remoteSSHhost = arg
                    print("remoteSSHhost: " + remoteSSHhost)
                else:
                    isValid = False
                    errMsg = "remoteDir: invalid host '%s'\n" % arg
                # end if
                #end if
            elif opt == "--deviceType":
                deviceType = arg
                print("deviceType: " + deviceType)
            elif opt == "--optimType":
                if arg in ("Brute", "Optim", "Snap"):
                    optimType = arg
                    print("optimType: " + optimType)
                else:
                    isValid = False
                    errMsg = "optimType: invalid option '%s'\n" % arg
                # end if
            elif opt == "--minimizeMethod":
                if arg in ("L-BFGS-B", "SLSQP"):
                    minimizeMethod = arg
                    print("minimizeMethod: " + minimizeMethod)
                else:
                    isValid = False
                    errMsg = "minimizeMethod: invalid option '%s'\n" % arg
                # end if
            # end if
        # end for
        print ("# ---------------------------------------------------------------\n")
        if not isValid:
            raise Exception(errMsg)
        # end if
    except Exception as excT:
        errMsg = str(excT) + '\nSLALOM usage:\n python slalom.py [args]\n  Examples:\n' + '   python slalom.py\n   python slalom.py --deviceType InGaN_PN --optimType Optim --minimizeMethod SLSQP\n   python slalom.py --deviceSimulator atlas --currentDir "N:\\TCAD\\SLALOM\\Device\\Silvaco\\" --remoteDir "/home/sidi/SLALOM/Device/Silvaco/" --remoteSSH sidi@efprimix --deviceType InGaN_PN --optimType Optim --minimizeMethod SLSQP'
        dispError(errMsg, doExit = True)
        # never reached
        pass
    # end try
# end if

# Create a new device of type deviceType
# NB: if deviceType is not found, Device.deviceType will be set to None...
# ... and the parameters must be entered below.
Device = slalomDevice(deviceType, currentDir)

# if deviceType set to None, define here the parameters to optimize.
# put always one line per parameter to let the optimizer build the...
# code for the remote server.
if Device.deviceType is None:
    # Device type as defined by the user
    Device.deviceType = "UserDefined"
    # Deckbuild input filename
    Device.inputFilename = "InGaN_PN.in"
    # Device description
    Device.mainTitle = "PN InGaN PV Cell"
    # Output directory
    Device.outputDir = Device.currentDir + "output" + Device.dirSepChar + Device.deviceType + Device.dirSepChar
    # Parameters name, as defined is the Deckbuild input
    Device.paramName = ["PLayerThick", "PLayerDop", "NLayerThick", "NLayerDop", "AlloyComp"]
    # Parameters unit
    Device.paramUnit = ["um", "1/cm3", "um", "1/cm3", ""]
    # Parameters format string (e.g. for doping use "%.6e")
    Device.paramFormat = ["%.8f", "%.6e", "%.8f", "%.6e", "%.8f"]
    # Parameters short format string for console output (e.g. for doping use "%.4e")
    Device.paramFormatShort = ["%.6f", "%.4e","%.6f",  "%.4e", "%.6f"]
    # Normalized parameters format string for console output
    Device.paramFormatNormalized = ["%.8f", "%.8f", "%.8f", "%.8f", "%.8f"]
    # Normalization value for each parameter
    Device.paramNorm = np.array([1.000, 1e17, 1.000, 1e17, 1.00])
    # Parameters range limit (Start)
    Device.paramStart = np.array([0.001, 1e15, 0.100, 1e15, 0.20])
    # Parameters range limit (End)
    Device.paramEnd = np.array([1.000, 1e19, 1.000, 1e18, 0.80])
    # Parameters initial values (used as a starting point or when optimType is set to "Snap")
    # should be in the [paramStart, paramEnd] range
    Device.paramInit = np.array([0.100, 1e17, 0.500, 1e15, 0.30])
    # Parameters number of points (used as when optimType is set to "Brute")
    Device.paramPoints = [1, 1, 1, 1, 1]
    # Parameters variation type (True for logarithmic variation (e.g. for doping), and False for linear)
    Device.paramLogscale = [False, True, False, True, False]
    Device.paramWeight = False
# end if

(bOK, errMsg) = Device.validate()
if not bOK:
    dispError(errMsg, doExit = True)
# end if

# </END-Parameters>
# ======================================================================================================

# ======================================================================================================
# <START-DeviceGui>

# the device GUI window is shown, if the solar cell parameters were not defined, to let the user...
# ...define the optimizer parameters in a more easier way.
showDeviceGui = enableGUI
deviceGuiValidated = False

try:
    if showDeviceGui and (Device.deviceType is None):
        #if Device.deviceType is None:
        from slalomDeviceGui import *
        # tkinter is not always installed by default (e.g. in RedHat Enterprise Linux 7+ or CentOS 6.x)...
        # ...if not installed, the optimizer device GUI cannot be started...
        # ...(just (re)install it or install a more recent python/numpy/scipy/matplotlib/tk version...
        # ... and restart Optimizer).
        if TkFound:
            if (not Device.inputFilename) or (not Device.paramName):
                Device.reset("InGaN_PN")
            # end if
            deviceGui = slalomDeviceGui(Device, remoteDir, remoteSSHhost, optimType, minimizeMethod)
            deviceGui.show()
            deviceGuiValidated = deviceGui.validated
            if not deviceGui.validated:
                dispError("Optimizer not started (parameters not validated in the GUI)", doExit = True)
            # end if
            remoteDir = deviceGui.remoteDir
            remoteSSHhost = deviceGui.remoteHost
            optimType = deviceGui.optimType
            minimizeMethod = deviceGui.minimizeMethod
        # end if
    # end if
except Exception:
    # catch only Exception (since sys.exit raise BaseException)
    pass
# end try

# </END-DeviceGui>
# ======================================================================================================


# ======================================================================================================
# Woking directory validation
# <START-CurrentDir>

# disable the standard output buffering
sys.stdout = UnbufferedStdout(sys.stdout)

if os.path.isdir(Device.currentDir) == False:
    dispError("cannot start the optimizer: Deckbuild input directory not found: " + Device.currentDir, doExit = True)
# end if

if (Device.currentDir.endswith('/') == False) and (Device.currentDir.endswith('\\') == False):
    Device.currentDir += dirSepChar
# end if

# <END-CurrentDir>
# ======================================================================================================


# ======================================================================================================
# <START-Output>

if clearOutputDir:
    slalomCore.removeOutputFiles(Device.outputDir)
# end if

# <END-Output>
# ======================================================================================================


# ======================================================================================================
# <START-Random>

# Choose randomly a starting point for the optimizer.
# Starting the optimizer with a random point could be a way...
# ...to check the uniqueness of the optimized set of parameters.
if randomInit:
    Device.randomInit(printOut = True)
# end if

# <END-Random>
# ======================================================================================================


# ======================================================================================================
# <START-Optimizer>

pythonInterpreter = "python"

def startMonitor(enable = True, dataFilename = None, remoteHost = None, simulator = "atlas"):
    """ start the optimizer monitor (only on the client-side) """
    
    if not enable:
        return
    # end if

    try:
        import slalomWindow

        # tkinter is not always installed by default (e.g. in RedHat Enterprise Linux 7+ or CentOS 6.x)...
        # ...if not installed, the optimizer monitor cannot be started...
        # ...(just (re)install it or install a more recent python/numpy/scipy/matplotlib/tk version...
        # ... and restart OptimizerMonitor).
        if not slalomWindow.TkFound:
            return
        # end if

        cmdT = [pythonInterpreter, "slalomMonitor.py"]
        if dataFilename is not None:
            cmdT.append(dataFilename)
            if remoteHost is not None:
                cmdT.append(remoteHost)
            #end if
        #end if
        cmdT.append(simulator)
        curDir = os.path.dirname(os.path.realpath(__file__))
        subprocess.Popen(cmdT, shell=False, cwd=curDir)
    except:
        pass
    # end try

# end startMonitor

# ...and start the optimization
remoteMon = (remoteDir is not None) and (len(remoteDir) > 2) and (remoteSSHhost is not None) and ("@" in remoteSSHhost)

if remoteMon:
    # Silvaco, tiberCAD or other simulator tools are installed on a remote server (the most common case)

    # copy the needed files and launch the optimizer on the remote server
    # Remote dir only used by the optimizer. do not store files there.
    try:
        tmpDir = os.path.dirname(os.path.realpath(__file__))
        if not tmpDir.endswith(dirSepChar):
            tmpDir += dirSepChar
        # end if
        optDir = tmpDir
        tmpDir += 'Remote' + dirSepChar
        if not os.path.exists(tmpDir):
            os.makedirs(tmpDir)
        # end if
        if not os.path.exists(tmpDir):
            dispError("Remote directory not found and cannot be created: " + tmpDir, doExit = True)
        # end if

        pythonFiles = ['slalom.py', 'slalomCore.py', 'slalomDevice.py', 'slalomSimulator.py']
        for fileName in pythonFiles:
            shutil.copyfile(optDir + fileName, tmpDir + fileName)
        # end if

        if Device.modelFilename:
            for fileName in Device.modelFilename:
                shutil.copyfile(currentDir + fileName, tmpDir + fileName)
            # end if
        # end if

        shutil.copyfile(currentDir + Device.inputFilename, tmpDir + Device.inputFilename)

        shutil.copyfile(optDir + 'COPYRIGHT', tmpDir + 'COPYRIGHT')

        # build the SLALOM code with the updated device parameters
        fileT = open(tmpDir + 'slalom.py', 'r')
        fileContent = ""
        for lineT in fileT:
            lineT = lineT.rstrip("\r\n")
            lineX = lineT.lstrip("\t ")
            nSpaces = len(lineT) - len(lineX)
            prefixT = lineT[0:nSpaces]
            if lineX.startswith('currentDir ='):
                fileContent += prefixT + 'currentDir = \'' + remoteDir + '\'\n'
                continue
            elif lineX.startswith('remoteDir ='):
                fileContent += prefixT + 'remoteDir = None' + '\n'
                continue
            elif lineX.startswith('remoteSSHhost ='):
                fileContent += prefixT + 'remoteSSHhost = None' + '\n'
                continue
            elif lineX.startswith('showDeviceGui ='):
                fileContent += prefixT + 'showDeviceGui = False' + '\n'
                continue
            elif lineX.startswith('enableMonitor ='):
                fileContent += prefixT + 'enableMonitor = False' + '\n'
                continue
            # end if

            if showDeviceGui and deviceGuiValidated:
                if lineX.startswith('deviceType ='):
                    fileContent += prefixT + 'deviceType = None\n'
                    continue
                elif lineX.startswith('optimType = '):
                    fileContent += prefixT + 'optimType = ' + '\"' + optimType + '\"\n'
                    continue
                elif lineX.startswith('minimizeMethod = '):
                    fileContent += prefixT + 'minimizeMethod = ' + '\"' + minimizeMethod + '\"\n'
                    continue
                elif lineX.startswith('Device.'):
                    if lineX.startswith('Device.inputFilename ='):
                        fileContent += prefixT + 'Device.deviceType = ' + '\"' + Device.deviceType + '\"\n'
                        fileContent += prefixT + 'Device.inputFilename = ' + '\"' + Device.inputFilename + '\"\n'
                        continue
                    elif lineX.startswith('Device.mainTitle ='):
                        fileContent += prefixT + 'Device.mainTitle = ' + '\"' + Device.deviceType + '\"\n'
                        continue
                    elif lineX.startswith('Device.outputDir ='):
                        fileContent += prefixT + 'Device.outputDir = currentDir + \"output\" + dirSepChar + \"' + Device.deviceType + '\" + dirSepChar\n'
                        continue
                    elif lineX.startswith('Device.modelFilename ='):
                        if Device.modelFilename:
                            iCount = len(Device.modelFilename)
                            if iCount > 0:
                                fileContent += prefixT + 'Device.modelFilename = ['
                                for ii in range(0, len(Device.modelFilename)):
                                    fileContent += '\"' + Device.modelFilename[ii] + '\"'
                                    if ii < (iCount - 1):
                                        fileContent += ', '
                                    # end if
                                # end for
                                fileContent += ']\n'
                            # end if
                        else:
                            fileContent += prefixT + 'Device.modelFilename = None\n'
                        # end if
                        continue
                    # end if

                    listName = ['Device.paramName =', 'Device.paramFormat =', 'Device.paramUnit =', 'Device.paramFormatShort =', 'Device.paramFormatNormalized =', 'Device.paramNorm =', 'Device.paramStart =', 'Device.paramEnd =', 'Device.paramInit =', 'Device.paramPoints =', 'Device.paramLogscale =']
                    listType = ['string', 'string', 'string', 'string', 'string', 'float', 'float', 'float', 'float', 'int', 'bool']
                    listVal = [Device.paramName, Device.paramFormat, Device.paramUnit, Device.paramFormatShort, Device.paramFormatNormalized, Device.paramNorm, Device.paramStart, Device.paramEnd, Device.paramInit, Device.paramPoints, Device.paramLogscale]
                    bFound = False
                    for pp in range(0, len(listName)):
                        if lineX.startswith(listName[pp]):
                            fileContent += prefixT + listName[pp]
                            if listType[pp] == 'float':
                                fileContent += ' np.array(['
                            else:
                                fileContent += ' ['
                            # end if
                            iCount = len(listVal[pp])
                            for ii in range(0, iCount):
                                if listType[pp] == 'string':
                                    fileContent += '\"' + str(listVal[pp][ii]) + '\"'
                                else:
                                    fileContent += str(listVal[pp][ii])
                                # end if
                                if ii < (iCount - 1):
                                    fileContent += ', '
                                # end if
                            # end for
                            fileContent += ']'
                            if listType[pp] == 'float':
                                fileContent += ')'
                            # end if
                            fileContent += '\n'
                            bFound = True
                            break
                        # end if
                    # end for
                    if bFound:
                        continue
                    # end if
                # end if
            # end if (deviceGui)

            fileContent += lineT + '\n'
        # end for

        fileT.close()
        fileT = open(tmpDir + 'slalom.py', 'w')
        fileT.write(fileContent)
        fileT.close()

        print '\nfiles copied to the local directory: ' + tmpDir

        STDDEVNULL = open(os.devnull, 'w')

        subprocess.check_call(['ssh', remoteSSHhost, 'mkdir', '-p', remoteDir], shell=False, stdout=STDDEVNULL, stderr=STDDEVNULL)

        # scp (under Linux) or (under gitbash on Windows): normalize path (but keep an unmodified copy)
        tmpDirRaw = tmpDir
        if not tmpDir.startswith('/'):
            tmpDir = '/' + tmpDir
            tmpDir = tmpDir.replace('\\', '/').replace(':', '')
        # end if

        try:
            subprocess.check_call(['scp', '-r', tmpDir + '*', remoteSSHhost + ':' + remoteDir], shell=False, stdout=STDDEVNULL, stderr=STDDEVNULL)
        except:
            # retry with shell=True (rarely needed, e.g. for some CentOS 6.5 with Python 2.7.12 configs)
            try:
                subprocess.check_call(['scp -r ' + tmpDir + '* ' + remoteSSHhost + ':' + remoteDir], shell=True, stdout=STDDEVNULL, stderr=STDDEVNULL)
            except:
                pass
            # end try
            pass
        # end try

        print '\nfiles copied to the remote server: ' + remoteSSHhost + ':' + remoteDir

        # remove the temporary files
        for fileT in os.listdir(tmpDirRaw):
            pathT = os.path.join(tmpDirRaw, fileT)
            try:
                if os.path.isfile(pathT):
                    os.unlink(pathT)
                # end if
            except:
                pass
            # end try
        # end for

        subprocess.Popen(['ssh', remoteSSHhost, pythonInterpreter, remoteDir + 'slalom.py'], shell=False, stdout=STDDEVNULL, stderr=STDDEVNULL)

        bFound = False

        for ii in range(0, 5):

            time.sleep(0.500)

            optimFilename = remoteDir
            try:
                sshT = subprocess.Popen(['ssh', remoteSSHhost, 'cat', remoteDir + 'ofname.txt'], shell=False, stdout=subprocess.PIPE, stderr=STDDEVNULL)
                fileT = sshT.stdout
                optimFilename = fileT.read()
                bFound = optimFilename and (len(optimFilename) >= 12)
            except:
                pass
            # end try

            errMsg = None
            try:
                sshT = subprocess.Popen(['ssh', remoteSSHhost, 'cat', remoteDir + 'errlog.txt'], shell=False, stdout=subprocess.PIPE, stderr=STDDEVNULL)
                fileT = sshT.stdout
                errMsg = fileT.read()
            except:
                pass
            # end try

            if errMsg and (len(errMsg) > 3):
                dispError(errMsg, doExit = True)
            # end if

            if bFound:
                break
            # end if

        # end for

        strT =  "\n-------------- SLALOM started on the remote server ------------\n"
        strT += "remote SSH host:\n   " + remoteSSHhost + "\n"
        strT += "remote directory:\n   " + remoteDir + "\n"
        strT += "remote data filename:\n   " + (optimFilename if bFound else "not found (check server status)")
        strT += "\n---------------------------------------------------------------\n"
        print strT

        # set enableMonitor to True to start the optimizer monitor
        enableMonitor = enableGUI
        if enableMonitor and bFound:
            # update the monitor parameters
            fileT = open("Settings/slalomMonitor.params", "w")
            fileT.write("dataFilename = " + optimFilename)
            fileT.write("\nremoteHost = " + remoteSSHhost)
            fileT.write("\nremoteHostEnabled = 1")
            fileT.write("\nupdateDelay = 30")
            fileT.write("\nupdateDelayAuto = 1")
            fileT.close()
            startMonitor(enable = enableMonitor, dataFilename = optimFilename, remoteHost = remoteSSHhost, simulator=deviceSimulator)
        # end if

    except Exception as excT:
        # catch only Exception (since sys.exit raise BaseException)
        dispError("Cannot copy the optimizer files to the remote server: " + str(excT), doExit = True)
        pass

else:
    # Silvaco, tiberCAD or other simulator tools are installed on this machine

    # enable logging for debugging purpose
    errFilename = currentDir + 'errlog.txt'

    try:

        try:
            os.unlink(errFilename)
        except:
            pass
        # end try

        Optimizer = slalomCore(Device, pythonInterpreter, deviceSimulator)

        if optimType == "Optim":
            # optimPoints is used to approximate the jacobian. If increased, the optimisation time will dramatically increase. The default value is 21 and the maximum value is 201.
            Optimizer.setMinimizeMethod(minimizeMethod, maxIter = maxIter, tolerance = 1e-3, optimPoints = 21)
        # end if

        # set enableMonitor to True to start the optimizer monitor
        enableMonitor = enableGUI
        if enableMonitor:
            dirSepCharFrom = '/' if ('\\' in currentDir) else '/'
            dirSepCharTo = '\\' if ('\\' in currentDir) else '/'
            optimizedFilename = Optimizer.getOptimizedFilename()
            optimizedFilename = optimizedFilename.replace(dirSepCharFrom, dirSepCharTo)
            startMonitor(enable = enableMonitor, dataFilename = optimizedFilename, remoteHost = None, simulator=deviceSimulator)
        # end if

        # save the current process id...
        fileProc = open(Optimizer.getOutputDir() + "proc.txt", "w")
        fileProc.write(str(os.getpid()))
        fileProc.close()

        # ...and start the optimization
        Optimizer.start(optimType)

    except Exception as excT:
        fileErr = open(errFilename, 'w')
        fileErr.write(traceback.format_exc())
        fileErr.close()
        pass
    # end try

# end if (remoteMon)

# <END-Optimizer>
# ======================================================================================================
