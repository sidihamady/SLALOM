# -*- coding: utf-8 -*-

# ======================================================================================================
# SLALOM - Open-Source Solar Cell Multivariate Optimizer
# Copyright(C) 2012-2019 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.
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
# File:           slalomDeviceGui.py
# Type:           Class
# Use:            The slalomDeviceGui class is used by the SLALOM module.
#                 slalomDeviceGui provides a useful interface to select one of the...
#                  ...predefined devices.
#                  slalomDeviceGui uses tkinter that is already installed on the client...
#                  (this is generally the case, except for some CentOS or RedHat machines)
# ------------------------------------------------------------------------------------------------------

from slalomCore import *
from slalomDevice import *
import re

TkFound = False

try:
    if sys.version_info[0] < 3:
        import Tkinter as Tk
        import ttk
    else:
        import tkinter as Tk
        import tkinter.ttk as ttk
    # end if
    from ttk import *
    import tkMessageBox
    import tkFileDialog
    TkFound = True
except ImportError as ierr:
    # tkinter related modules not found. Just warn and skip this part.
    # just install or update python/numpy/scipy/matplotlib/tk modules
    dispError("{0}".format(ierr), doExit = False)
    # catch only Exception (since sys.exit raise BaseException)
    pass
except:
    pass
# end try

try:

    class slalomDeviceGui(object):

        def __init__(self, device, remoteDir, remoteHost, optimType, minimizeMethod, *args, **kwargs):

            self.__version__ = slalomVersion

            self.device = device
            self.device.deviceType = 'User'

            self.parcount = 6
            self.rowcount = 8

            self.remoteDir = remoteDir
            self.remoteHost = remoteHost

            self.optimType = optimType
            self.minimizeMethod = minimizeMethod

            self.validated = False

        # end __init__

        def show(self):

            self.root = Tk.Tk()
            self.root.withdraw()
            self.root.wm_title("SLALOM - Device Parameters")
            self.root.protocol("WM_DELETE_WINDOW", self.onClose)

            self.frame = Tk.Frame(self.root)
            self.frame.pack(expand=1, fill="both", padx=10, pady=10)

            irow = 0
            ipadx = 5
            ipady = 5

            validateDirname = (self.frame.register(self.onEntryValidateDirname), '%P')
            validateFilename = (self.frame.register(self.onEntryValidateFilename), '%P')
            validateHostname = (self.frame.register(self.onEntryValidateHostname), '%P')

            Tk.Label(self.frame, text='Current Dir:', justify=Tk.RIGHT).grid(row=irow, column=0, sticky=Tk.E, padx=ipadx, pady=ipady)
            self.currentDirWidget = Tk.Entry(self.frame, validate="key", vcmd=validateDirname)
            self.currentDirWidget.grid(row=irow, column=1, columnspan=4, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)
            Tk.Label(self.frame, text='Input file:', justify=Tk.RIGHT).grid(row=irow, column=5, sticky=Tk.E, padx=ipadx, pady=ipady)
            self.inputFilenameWidget = Tk.Entry(self.frame, validate="key", vcmd=validateFilename)
            self.inputFilenameWidget.grid(row=irow, column=6, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)
            irow += 1

            Tk.Label(self.frame, text='Remote Dir:', justify=Tk.RIGHT).grid(row=irow, column=0, sticky=Tk.E, padx=ipadx, pady=ipady)
            self.remoteDirWidget = Tk.Entry(self.frame, validate="key", vcmd=validateDirname)
            self.remoteDirWidget.grid(row=irow, column=1, columnspan=4, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)
            Tk.Label(self.frame, text='SSH host:', justify=Tk.RIGHT).grid(row=irow, column=5, sticky=Tk.E, padx=ipadx, pady=ipady)
            self.remoteHostWidget = Tk.Entry(self.frame, validate="key", vcmd=validateHostname)
            self.remoteHostWidget.grid(row=irow, column=6, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)
            irow += 1

            Tk.Label(self.frame, text='Device type:', justify=Tk.RIGHT).grid(row=irow, column=0, sticky=Tk.E, padx=ipadx, pady=ipady)
            validateParam = (self.frame.register(self.onEntryValidateParam), '%P')
            self.deviceTypeWidget = Tk.Entry(self.frame, validate="key", vcmd=validateParam)
            self.deviceTypeWidget.grid(row=irow, column=1, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)

            validateOptim = (self.frame.register(self.onEntryValidateOptim), '%P')
            validateMethod = (self.frame.register(self.onEntryValidateMethod), '%P')
            Tk.Label(self.frame, text='Optimization:', justify=Tk.RIGHT).grid(row=irow, column=3, sticky=Tk.E, padx=ipadx, pady=ipady)
            self.optimWidget = Tk.Entry(self.frame, validate="key", vcmd=validateOptim)
            self.optimWidget.grid(row=irow, column=4, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)
            Tk.Label(self.frame, text='Method:', justify=Tk.RIGHT).grid(row=irow, column=5, sticky=Tk.E, padx=ipadx, pady=ipady)
            self.methodWidget = Tk.Entry(self.frame, validate="key", vcmd=validateMethod)
            self.methodWidget.grid(row=irow, column=6, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)
            irow += 1

            Tk.Label(self.frame, text='Models:', justify=Tk.RIGHT).grid(row=irow, column=0, sticky=Tk.E, padx=ipadx, pady=ipady)
            self.modelWidget = list()
            for ii in range(0, 2):
                for jj in range(0, self.parcount):
                    self.modelWidget.append(Tk.Entry(self.frame, validate="key", vcmd=validateFilename))
                    self.modelWidget[(ii * self.parcount) + jj].grid(row=irow, column=1+jj, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)
                # end for
                irow += 1
            # end for

            self.paramWidget = [ list(), list(), list(), list(),
                                 list(), list(), list(), list() ]
            self.label = ['Parameter:', 'Format:', 'Norm:', 'Start:',
                          'End:', 'Init:', 'Points:', 'LogScale:']
            self.type = ['string', 'format', 'float', 'float',
                         'float', 'float', 'int', 'bool']
            self.deviceparam = [ self.device.paramName, self.device.paramFormat, self.device.paramNorm, self.device.paramStart,
                                 self.device.paramEnd, self.device.paramInit, self.device.paramPoints, self.device.paramLogscale ]
            validateFormat = (self.frame.register(self.onEntryValidateFormat), '%P')
            validateFloat = (self.frame.register(self.onEntryValidateFloat), '%P')
            validateInteger = (self.frame.register(self.onEntryValidateInteger), '%P')
            validateBoolean = (self.frame.register(self.onEntryValidateBoolean), '%P')
            self.paramvalidator = [validateParam, validateFormat, validateFloat, validateFloat,
                                   validateFloat, validateFloat, validateInteger, validateBoolean]

            for ii in range(0, self.rowcount):
                Tk.Label(self.frame, text=self.label[ii], justify=Tk.RIGHT).grid(row=irow+ii, column=0, sticky=Tk.E, padx=ipadx, pady=ipady)
                for jj in range(0, self.parcount):
                    self.paramWidget[ii].append(Tk.Entry(self.frame, validate="key", vcmd=self.paramvalidator[ii]) if (self.paramvalidator[ii] is not None) else Tk.Entry(self.frame))
                    self.paramWidget[ii][jj].grid(row=irow+ii, column=1+jj, padx=ipadx, pady=ipady)
                # end for
            # end for
            irow += self.rowcount

            ttk.Button(self.frame, text="Optimize", command=self.onOptimize).grid(row=irow, column=self.parcount-1, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)
            ttk.Button(self.frame, text="Cancel", command=self.onCancel).grid(row=irow, column=self.parcount, sticky=Tk.W+Tk.E, padx=ipadx, pady=ipady)

            self.root.deiconify()

            if (os.name == "nt"):
                self.root.iconbitmap(r'Images/slalomg.ico')
            else:
                iconSlalom = Tk.PhotoImage(file='Images/slalomg.gif')
                self.root.tk.call('wm', 'iconphoto', self.root._w, iconSlalom)
            # end if

            self.updateGui()

            self.root.mainloop()

        # end __init__

        def onEntryValidateDirname(self, sp):
            try:
                if (not sp) or (len(sp) <= 255):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateDirname

        def onEntryValidateFilename(self, sp):
            try:
                if (not sp) or (len(sp) <= 63):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateFilename

        def onEntryValidateHostname(self, sp):
            try:
                if (not sp) or (len(sp) <= 63):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateHostname

        def onEntryValidateParam(self, sp):
            try:
                if (not sp) or ((len(sp) <= 31) and (re.match(r'^\w+$', sp))):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateParam

        def onEntryValidateFormat(self, sp):
            try:
                if (not sp) or ((len(sp) <= 7) and (re.match(r'^[0-9\%\.efgd]*$', sp))):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateFormat

        def onEntryValidateFloat(self, sp):
            try:
                if (not sp) or ((len(sp) <= 15) and (re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', sp))):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateFloat

        def onEntryValidateInteger(self, sp):
            try:
                if (not sp) or ((len(sp) <= 3) and (re.match('^\d+$', sp))):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateInteger

        def onEntryValidateBoolean(self, sp):
            try:
                if (not sp) or ((len(sp) <= 5) and ('True'.startswith(sp) or 'False'.startswith(sp))):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateBoolean

        def onEntryValidateOptim(self, sp):
            try:
                if (not sp) or ((len(sp) <= 5) and ('Brute'.startswith(sp) or 'Snap'.startswith(sp) or 'Optim'.startswith(sp))):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateOptim

        def onEntryValidateMethod(self, sp):
            try:
                if (not sp) or ((len(sp) <= 8) and ('L-BFGS-B'.startswith(sp) or 'SLSQP'.startswith(sp))):
                    return True
                # end if
                return False
            except:
                return True
            # end try
        # end onEntryValidateOptim

        def updateGui(self):

            try:

                self.currentDirWidget.delete(0, Tk.END)
                self.currentDirWidget.insert(0, self.device.currentDir)
                self.inputFilenameWidget.delete(0, Tk.END)
                self.inputFilenameWidget.insert(0, self.device.inputFilename)

                self.remoteDirWidget.delete(0, Tk.END)
                self.remoteDirWidget.insert(0, self.remoteDir)
                self.remoteHostWidget.delete(0, Tk.END)
                if self.remoteHost is not None:
                    self.remoteHostWidget.insert(0, self.remoteHost)
                # end if

                self.deviceTypeWidget.delete(0, Tk.END)
                self.deviceTypeWidget.insert(0, self.device.deviceType)

                self.optimWidget.delete(0, Tk.END)
                self.optimWidget.insert(0, self.optimType)
                self.methodWidget.delete(0, Tk.END)
                self.methodWidget.insert(0, self.minimizeMethod)

                if self.device.modelFilename:
                    iCnt = len(self.device.modelFilename)
                    for ii in range(0, 2):
                        for jj in range(0, self.parcount):
                            self.modelWidget[(ii * self.parcount) + jj].delete(0, Tk.END)
                            if (((ii * self.parcount) + jj) < iCnt):
                                self.modelWidget[(ii * self.parcount) + jj].insert(0, self.device.modelFilename[jj])
                            # end if
                        # end for
                    # end for
                 # end if

                paramCount = len(self.deviceparam[0])
                for ii in range(0, self.rowcount):
                    for jj in range(0, self.parcount):
                        self.paramWidget[ii][jj].delete(0, Tk.END)
                        self.paramWidget[ii][jj].insert(0, str(self.deviceparam[ii][jj]) if (jj < paramCount) else '')
                    # end for
                # end for

            except:
               pass
            # end try

        # end updateGui

        def updateDevice(self):

            try:

                self.device.currentDir = self.currentDirWidget.get()
                self.device.inputFilename = self.inputFilenameWidget.get()

                self.remoteDir = self.remoteDirWidget.get()
                self.remoteHost = self.remoteHostWidget.get()
                if len(self.remoteHost) < 3:
                    self.remoteHost = None
                # end if

                self.device.deviceType = self.deviceTypeWidget.get()

                self.optimType = self.optimWidget.get()
                self.minimizeMethod = self.methodWidget.get()

                bFlag = False

                if self.device.modelFilename:
                    iCnt = len(self.device.modelFilename)
                    for ii in range(0, 2):
                        for jj in range(0, self.parcount):
                            modelT = self.modelWidget[(ii * self.parcount) + jj].get()
                            if (not modelT) or (len(modelT) < 3):
                                break
                            # end if
                            if (((ii * self.parcount) + jj) < iCnt):
                                self.device.modelFilename[jj] = modelT
                            else:
                                if modelT not in self.device.modelFilename:
                                    self.device.modelFilename.append(modelT)
                                # end if
                            # end if
                        # end for
                    # end for
                # end if

                iCnt = len(self.deviceparam[0])
                for ii in range(0, self.rowcount):
                    for jj in range(0, self.parcount):
                        paramT = self.paramWidget[ii][jj].get()
                        if (not paramT) or (len(paramT) < 1):
                            break
                        # end if
                        if self.type[ii] == 'string' or self.type[ii] == 'format':
                            if (jj < iCnt):
                                self.deviceparam[ii][jj] = paramT
                            else:
                                self.deviceparam[ii].append(paramT)
                            # end if
                        elif self.type[ii] == 'float':
                            if (jj < iCnt):
                                self.deviceparam[ii][jj] = float(paramT)
                            else:
                                self.deviceparam[ii] = np.append(self.deviceparam[ii], float(paramT))
                            # end if
                        elif self.type[ii] == 'int':
                            if (jj < iCnt):
                                self.deviceparam[ii][jj] = int(paramT)
                            else:
                                self.deviceparam[ii].append(int(paramT))
                            # end if
                        elif self.type[ii] == 'bool':
                            if (jj < iCnt):
                                self.deviceparam[ii][jj] = True if (paramT == 'True') else False
                            else:
                                self.deviceparam[ii].append(True if (paramT == 'True') else False)
                            # end if
                        # end if
                    # end for
                # end for

                (self.validated, message) = self.device.validate()
                if not self.validated:
                    tkMessageBox.showwarning("SLALOM", message, parent=self.root)
                # end if

            except Exception as excT:
               tkMessageBox.showwarning("SLALOM", "Device data not valid: " + str(excT), parent=self.root)
               pass
            # end try

        # end updateDevice

        def onOptimize(self):
            self.updateDevice()
            self.onClose()
        # end onOptimize

        def onCancel(self):
            self.validated = False
            self.onClose()
        # end onCancel

        def onClose(self):
            if self.root is not None:
                self.root.quit()
                self.root.destroy()
                self.root = None
            # end if
        # end onClose

        # end onDevicelistBox

    # end slalomDeviceGui

except Exception as excT:

    excType, excObj, excTb = sys.exc_info()
    excFile = os.path.split(excTb.tb_frame.f_code.co_filename)[1]
    strErr  = "\n! cannot initialize GUI:\n  %s\n  in %s (line %d)\n" % (str(excT), excFile, excTb.tb_lineno)
    print(strErr)
    os._exit(1)
    # never reached
    pass

# end try
