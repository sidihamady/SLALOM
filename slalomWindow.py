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
# File:           slalomWindow.py
# Type:           Class
# Use:            The slalomWindow class and related classes are used by the slalomMonitor module.
#                 slalomWindow provides visualisation and control functionality...
#                  either in client/server configuration using ssh...
#                  ... or locally if it runs on the same machine than the optimizer.
#                  slalomWindow uses tkinter that is already installed on the client...
#                  (this is generally the case, except for some CentOS or RedHat machines)
# ------------------------------------------------------------------------------------------------------

from slalomCore import *

import threading
import re

# tkinter is not always installed by default (e.g. in RedHat Enterprise Linux 7+ or CentOS 6.x)...
# ...if not installed, the graphic part of the optimizer cannot be started...
# ...(just (re)install it or install a more recent python/numpy/scipy/matplotlib/tk version...
# ....and restart slalomMonitor).
TkFound = False

import matplotlib
matplotlib.use('Agg')

try:
    matplotlib.use('TkAgg')
    import matplotlib.backends.backend_tkagg
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
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
    import matplotlib.pyplot as pl
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.ticker import MaxNLocator
    TkFound = True
except ImportError as ierr:
    # tkinter related modules not found. Just warn and skip this part.
    # just install or update python/numpy/scipy/matplotlib/tk modules
    dispError("{0}".format(ierr), doExit = False)
    # catch only Exception (since sys.exit raise BaseException)
    pass
except:
    pass

try:

    class NavigationToolbar(NavigationToolbar2TkAgg):
        """ custom toolbar including an Autoscale and PDF save buttons """
        def __init__(self, chart):
            NavigationToolbar2TkAgg.__init__(self, chart.canvas, chart.root)
            self.chart = chart
        # end __init__

        try:
            toolitems = [tt for tt in NavigationToolbar2TkAgg.toolitems if tt[0] in ('Home', 'Back', 'Forward', 'Pan', 'Zoom')]
            toolitems.append(('AutoScale', 'Auto scale the plot', 'hand', 'onAutoScale'))
            toolitems.append(('Save', 'Save the plot as PDF', 'filesave', 'onSave'))
        except:
            pass
        # end try

        def onAutoScale(self):
            self.chart.onAutoScale()
        # end onAutoScale

        def onSave(self):
            self.chart.onSave()
        # end onAutoScale

    # end NavigationToolbar
except:
    pass

import tkFont

# :REV:1:20181115: suppress a nonrelevant warning from matplotlib
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class OptimizerViewer(Tk.Frame):
    """ view the optimization data file in realtime """

    def __init__(self, parent, *args, **kwargs):

        Tk.Frame.__init__(self, parent, *args, **kwargs)

        self.root = parent

        xscrollbar = ttk.Scrollbar(self, orient=Tk.HORIZONTAL)
        xscrollbar.pack(side=Tk.BOTTOM, fill=Tk.X)

        yscrollbar = ttk.Scrollbar(self, orient=Tk.VERTICAL)
        yscrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)

        # colorize some optimizer specific keywords
        self.text = Tk.Text(self, spacing1=2, spacing3=2, wrap='none', selectbackground="#B7DCFF", selectforeground="#000000", inactiveselectbackground="#B7DCFF")
        self.boldFont = tkFont.Font(self.text, self.text.cget("font"))
        self.boldFont.configure(weight="bold")
        self.text.tag_configure("keyword", foreground="#414AF3")
        self.text.tag_configure("keyword2", foreground="#41A30B")
        self.text.tag_configure("bold", font=self.boldFont)
        self.text.tag_configure("selectedline", background="#B7DCFF")
        self.text.pack(side=Tk.LEFT, fill="both", expand=1)
        self.text['xscrollcommand'] = xscrollbar.set
        self.text['yscrollcommand'] = yscrollbar.set

        xscrollbar.config(command=self.text.xview)
        yscrollbar.config(command=self.text.yview)

        self.selectedline = -1

        self.count = Tk.IntVar()
        self.listKeyword = None
        self.listKeyword2 = None

        self.text.bind("<1>", lambda event: self.text.focus_set())
        self.text.bind('<Button-3>', self.onRightClick, add='')
        self.text.bind("<Control-c>", lambda event: self.onCopy())
        self.text.bind("<Control-a>", lambda event: self.onSelectAll())
        self.text.bind("<Control-s>", lambda event: self.onSave())

    # end __init__

    def setText(self, strText, listKeyword, listKeyword2):
        """ update the viewer colorize the optimizer specific keywords """

        try:
            self.config(cursor="wait")
            self.update()
        except:
            pass

        wfocus = self.text.focus_get()

        self.text.config(state=Tk.NORMAL)

        try:
            self.text.delete("1.0", "end")
        except:
            pass
        # end try
        try:
            self.text.insert("end", strText)
            self.listKeyword = list(listKeyword)
            self.listKeyword2 = list(listKeyword2)
            if wfocus == self.text:
                self.text.focus()
            # end if
            for strK in self.listKeyword:
                self.colorize(strK, "keyword", "bold")
            # end for
            for strK in self.listKeyword2:
                self.colorize(strK, "keyword2", "bold")
            # end for
        except:
            pass
        # end try

        self.text.config(state=Tk.DISABLED)

        self.config(cursor="")
    # end setText

    def colorize(self, keyword, taga, tagb):
        start = self.text.index("1.0")
        end = self.text.index("end")
        self.text.mark_set("matchStart", start)
        self.text.mark_set("matchEnd", start)
        self.text.mark_set("searchEnd", end)

        while True:
            index = self.text.search(keyword, "matchEnd","searchEnd", count=self.count)
            if (index == "") or (self.count.get() == 0):
                break
            # end while
            self.text.mark_set("matchStart", index)
            self.text.mark_set("matchEnd", "%s+%dc" % (index, self.count.get()))
            self.text.tag_add(taga, "matchStart", "matchEnd")
            self.text.tag_add(tagb, "matchStart", "matchEnd")
        # end while
    # end colorize

    def onSelectAll(self):
        self.text.tag_add(Tk.SEL, "1.0", Tk.END)
        self.text.mark_set(Tk.INSERT, "1.0")
        self.text.see(Tk.INSERT)
        return 'break'
    # end onCopy

    # offset corresponds to the data file header and non-numeric part
    def selectLine(self, index, offset = 12):
        index += offset
        if self.selectedline >= 0:
            self.text.tag_remove("selectedline", "%d.0" % (1 + self.selectedline), "%d.end" % (1 + self.selectedline))
        # end if
        self.text.tag_add("selectedline", "%d.0" % (1 + index), "%d.end" % (1 + index))
        self.selectedline = index
    # end onCopy

    def onCopy(self):
        self.text.clipboard_clear()
        strC = self.text.get("sel.first", "sel.last")
        self.text.clipboard_append(strC)
        return 'break'
    # end onCopy

    def onRightClick(self, event):
        popmenu = Tk.Menu(None, tearoff=0)
        popmenu.add_command(label='Select All', command=self.onSelectAll)
        if self.text.tag_ranges("sel"):
            popmenu.add_command(label='Copy', command=self.onCopy)
        # end if
        popmenu.add_separator()
        popmenu.add_command(label='Save', command=self.onSave)
        popmenu.add_separator()
        popmenu.add_command(label='Close', command=self.onClose)
        popmenu.tk_popup(event.x_root, event.y_root, 0)
        return "break"
    # end onRightClick

    def onSave(self):
        fileopt = {}
        fileopt['defaultextension'] = '.txt'
        fileopt['filetypes'] = [('Text files', '.txt')]
        fileopt['initialfile'] = ''
        fileopt['parent'] = self.root
        fileopt['title'] = 'Save data'
        dataFilename = tkFileDialog.asksaveasfilename(**fileopt)
        if dataFilename:
            try:
                fileT = open(dataFilename, "w")
                fileT.write(self.text.get(1.0, Tk.END))
                fileT.close()
            except:
                pass
            # end try
        # end if
    # end onRestart

# end OptimizerViewer

class OptimizerThread(threading.Thread):

    def __init__(self, id, func):
        threading.Thread.__init__(self)
        self.id = id
        self.func = func
    # end __init__

    def run(self):
        self.func()
    # end run

# end OptimizerThread

class OptimizerReport(Tk.Frame):

    def __init__(self, owner, index, report, *args, **kwargs):

        Tk.Frame.__init__(self, report, *args, **kwargs)

        self.listParam = list()
        self.listOptim = list()
        self.listOptimout = list()
        self.count = 0

        self.fontsize = 10

        self.index = index

        self.owner = owner

        self.root = report

        self.figure = matplotlib.figure.Figure(figsize=(8,5), dpi=100, facecolor='#F1F1F1', linewidth=1.0, frameon=True)
        self.figure.subplots_adjust(top = 0.95, bottom = 0.12, left = 0.09, right = 0.95, wspace = 0.0, hspace = 0.1)
        self.plot = self.figure.add_subplot(111)
        self.plot.set_xlabel("$\mathregular{Voltage\ (V)}$" if (self.index == 0) else "$\mathregular{Wavelength\ (\mu m)}$", fontsize=self.fontsize)
        self.plot.set_ylabel("$\mathregular{Current\ (mA/cm^{2})}$" if (self.index == 0) else "$\mathregular{EQE}$", fontsize=self.fontsize)
        self.plot.format_coord = self.formatCoord

        try:
            self.plot.tick_params(axis='x', labelsize=self.fontsize)
            self.plot.tick_params(axis='y', labelsize=self.fontsize)
        except:
            [tx.label.set_fontsize(self.fontsize) for tx in self.plot.xaxis.get_major_ticks()]
            [ty.label.set_fontsize(self.fontsize) for ty in self.plot.yaxis.get_major_ticks()]
            pass

        try:
            if self.index == 0:
                self.plot.axhline(0.0, linestyle='-', linewidth=2, color='g', zorder=3)
                self.plot.axvline(0.0, linestyle='-', linewidth=2, color='g', zorder=3)
            else:
                self.plot.axhline(1.0, linestyle='-', linewidth=2, color='g', zorder=3)
            # end if
            self.plot.xaxis.major.locator.set_params(nbins=10)
            self.plot.yaxis.major.locator.set_params(nbins=5)
            self.plot.grid(True)
        except:
            pass

        self.plot.mlinex = None
        self.plot.mliney = None

        self.indexm = 0

        self.currentsign = 1.0

        paramFrame = Tk.Frame(self.root)
        paramFrame.pack(fill=Tk.X, padx=5, pady=5)
        self.paramlistBox = ttk.Combobox(paramFrame, state='readonly')
        self.paramlistBox.pack(side=Tk.LEFT, padx=(5, 5), fill=Tk.X, expand=1)
        self.paramlistBox['state'] = 'readonly'
        self.paramlistBox.bind('<<ComboboxSelected>>', self.onParamlistBox)

        self.paramlistCurrent = 0

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas._tkcanvas.config(highlightthickness=0)

        try:
            self.toolbar = NavigationToolbar(self)
        except:
            self.toolbar = None
            pass
        self.toolbar.pack(side=Tk.BOTTOM, fill=Tk.X)

        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

        self.canvas.show()

        self.linecolor = 'b'
        self.linecolorm = '#FF7F00'
        self.linestyle = '-'
        self.linesize = 2.0
        self.markersm = 'o'
        self.markerhg = 'None'
        self.markersizesm = 6.0
        self.markersizehg = 3.0
        self.line = None

        self.dataSep = ' '

        self.datax = list()
        self.datay = list()

        self.root.bind('<Button-3>', self.onRightClick, add='')
        self.root.bind("<Control-s>", lambda event: self.onSave())
        self.root.bind("<Prior>", self.onPageDown)
        self.root.bind("<Next>", self.onPageUp)

    # end __init__

    def reset(self, listParam, listOptim, listOptimout, listFileContent):

        if (listParam is None) or (listOptim is None) or (listOptimout is None):
            return False
        # end if

        del self.listParam[:]
        self.listParam = list(listParam)

        del self.listOptim[:]
        self.listOptim = list(listOptim)

        del self.listOptimout[:]
        self.listOptimout = list(listOptimout)

        if self.count > 0:
            for ida in range(0, self.count):
                self.datax[ida] = np.delete(self.datax[ida], np.s_[:])
                self.datay[ida] = np.delete(self.datay[ida], np.s_[:])
            # end for
            del self.datax[:]
            self.datax = list()
            del self.datay[:]
            self.datay = list()
        # end if

        self.count = 0

        dataValid = self.isDataValid(listFileContent)

        if dataValid:
            self.paramlistBox['values'] = self.listParam
            self.paramlistBox.set(self.listParam[self.count - 1])
            self.paramlistCurrent = self.paramlistBox.current()
        # end if

        return dataValid

    # end reset

    def isDataValid(self, listFileContent = None):

        try:
            iParamLen = len(self.listParam)
            if iParamLen < 1:
                return False
            # end if
            if listFileContent is not None:
                iFcontentLen = len(listFileContent)
                if (iFcontentLen < 1) or (iParamLen != iFcontentLen):
                    return False
                # end if
            # end if
            self.count = iParamLen
        except:
            return False
        # end try

        return True

    # end isDataValid

    def formatCoord(self, x, y):
        return ('Voltage: %08.5f V  ;  Current: %09.5f mA/cm²' if (self.index == 0) else 'Wavelength: %8.5f µm  ;  EQE: %8.5f') % (x, y)
    # end formatCoord

    def onPageMove(self, event, idir):
        if self.owner.isRunning():
            return
        # end if

        try:
            indexT = self.paramlistBox.current() + idir
            indexMax = len(self.paramlistBox["values"])
            if (indexT < 0) or (indexT >= indexMax):
                return
            # end if
            self.updatePlot(index = indexT)
            self.paramlistBox.current(newindex = indexT)
            if (self.owner is not None):
                self.owner.updateSel(index = indexT)
                self.owner.paramlistBox.current(newindex = indexT)
            # end if
            self.paramlistCurrent = self.paramlistBox.current()
        except:
            pass
    # end onPageDown

    def onPageDown(self, event):
        return self.onPageMove(event, -1)
    # end onPageDown

    def onPageUp(self, event):
        return self.onPageMove(event, 1)
    # end onPageUp

    def updatePlot(self, index = None, autoscale = False):

        if (index is None) or (index < 0) or (index >= self.count):
            index = self.count - 1
        # end if

        try:

            if self.line is None:
                self.line, = self.plot.plot(self.datax[index], self.datay[index], self.linestyle, linewidth=self.linesize, zorder=4)
                self.line.set_markerfacecolor(self.linecolor)
                self.line.set_markeredgecolor(self.linecolor)
            else:
                self.line.set_xdata(self.datax[index])
                self.line.set_ydata(self.datay[index])
            # end if
            strTX = ""
            try:
                strTX = self.listOptim[index]
            except:
                pass

            self.line.set_color(self.linecolorm if (self.indexm == index) else self.linecolor)
            self.plot.set_title(strTX, fontsize=self.fontsize)
            self.line.set_marker(self.markerhg if (len(self.datax[index]) > 20) else self.markersm)
            self.line.set_markersize(self.markersizehg if (len(self.datax[index]) > 20) else self.markersizesm)

            if (self.index == 0):
                (Jm, Vm, FF, Jsc, Voc, Eff) = self.listOptimout[index]
                if (self.plot.mlinex is not None):
                    self.plot.mlinex.remove()
                # end if
                if (self.plot.mliney is not None):
                    self.plot.mliney.remove()
                # end if
                self.plot.mlinex = self.plot.hlines(y=Jm * self.currentsign, xmin=0.0, xmax=Vm, linewidth=1, colors='g', linestyles='dashed', zorder=4)
                self.plot.mliney = self.plot.vlines(x=Vm, ymin=Jm * self.currentsign, ymax=0.0, linewidth=1, colors='g', linestyles='dashed', zorder=4)
                # end if
            # end if

            if autoscale:
                self.plot.relim()
                self.plot.autoscale()
                if (self.index == 1):
                    ylim = self.plot.get_ylim()
                    self.plot.set_ylim([0.0, ylim[1]])
                # end if
            # end if
            self.canvas.draw()

        except:
            pass

        # end try

    # end updatePlot

    def setParam(self, listParam, listOptim, listOptimout, listFileContent):

        if not self.reset(listParam, listOptim, listOptimout, listFileContent):
            tkMessageBox.showwarning("SLALOM", "Report data not valid", parent=self.root)
            return
        # end if

        try:
            self.config(cursor="wait")
            self.update()
        except:
            pass

        arrLine = list()

        try:
            (Jmr, Vmr, FFr, Jscr, Vocr, Effr) = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            self.indexm = self.count - 1
            linestoskip = 8
            prevPoints = 0

            for ida in range(0, self.count):
                (Jm, Vm, FF, Jsc, Voc, Eff) = self.listOptimout[ida]
                if (Eff > Effr):
                    (Jmr, Vmr, FFr, Jscr, Vocr, Effr) = (Jm, Vm, FF, Jsc, Voc, Eff)
                    self.indexm = ida
                # end if
                arrLine = listFileContent[ida].split("\n")
                arrlen = len(arrLine)
                if (arrlen <= linestoskip):
                    break
                # end if
                self.datax.append(np.array([]))
                self.datay.append(np.array([]))
                xprev = None
                xval = 0.0
                yval = 0.0
                curPoints = 0
                for ii in range(linestoskip, arrlen):
                    tLine = arrLine[ii].replace("\r", "").replace("\n", "").split(self.dataSep)
                    dlen = len(tLine)
                    if dlen != 2:
                        break
                    # end if
                    try:
                        xval = float(tLine[0])
                        yval = float(tLine[1])
                    except:
                        pass
                    if xprev is None:
                        xprev = xval
                    elif xval > xprev:
                        # :REV:1:20181115: keep only (voltage or wavelength) that are monotically increasing
                        # but do not break (sometimes the simulator saves the same point)
                        self.datax[ida] = np.append(self.datax[ida], xval)
                        self.datay[ida] = np.append(self.datay[ida], yval)
                        xprev = xval
                        curPoints += 1
                    # end if
                # end for

                if ida == 0:
                    prevPoints = curPoints
                elif (curPoints < 3):
                    tkMessageBox.showwarning("SLALOM", "Report data not valid (number of points: %d)" % curPoints, parent=self.root)
                    return
                # end if

                self.currentsign = 1.0 if (self.datay[ida][0] > 0.0) else -1.0

                del arrLine[:]
                arrLine = list()
            # end for

            self.updatePlot(index = self.indexm, autoscale = True)

        except:
            tkMessageBox.showwarning("SLALOM", "Report data not valid", parent=self.root)
            return

        self.config(cursor="")
    # end setParam

    def onParamlistBox(self, event):

        if self.owner.isRunning():
            self.paramlistBox.current(newindex = self.paramlistCurrent)
            return
        # end if

        try:
            self.paramlistBox.selection_clear()
            indexT = self.paramlistBox.current()
            self.updateSel(index = indexT)
            if (self.owner is not None):
                self.owner.updateSel(index = indexT)
                self.owner.paramlistBox.current(newindex = indexT)
                for ii in range(0, len(self.owner.report)):
                    if (self.owner.report[ii] is not None) and (ii != self.index):
                        self.owner.report[ii].frame.paramlistBox.current(newindex = indexT)
                        self.owner.report[ii].frame.updateSel(index = self.owner.report[ii].frame.paramlistBox.current())
                    # end if
                # end for
                if (self.owner.viewer is not None):
                    self.owner.viewer.frame.selectLine(index = indexT)
                # end if
            # end if
            self.paramlistCurrent = indexT
        except:
            pass
        # end try

    # end onParamlistBox

    def updateSel(self, index=None):

        if not self.isDataValid():
            tkMessageBox.showwarning("SLALOM", "Report data not valid", parent=self.root)
            return
        # end if

        if (index is None) or (index < 0) or (index >= self.count):
            index = self.count - 1
        # end if

        self.updatePlot(index)

    # end updateSel

    def onRightClick(self, event):
        if self.owner.isRunning():
            return
        # end if

        popmenu = Tk.Menu(None, tearoff=0)
        popmenu.add_command(label='Auto scale', command=self.onAutoScale)
        popmenu.add_command(label='Save as PDF', command=self.onSave)
        popmenu.add_separator()
        popmenu.add_command(label='Close', command=self.onClose)
        popmenu.tk_popup(event.x_root, event.y_root, 0)
        return "break"
    # end onRightClick

    def onAutoScale(self):
        if self.owner.isRunning():
            return
        # end if

        for ida in range(0, self.count):
            curPoints = len(self.datax[ida])
            if (curPoints < 4):
                tkMessageBox.showwarning("SLALOM", "Report data not valid (number of points: %d)" % curPoints, parent=self.root)
                return
            # end if
        # end for

        if (self.plot is not None):
            self.plot.relim()
            self.plot.autoscale()
            if (self.index == 1):
                ylim = self.plot.get_ylim()
                self.plot.set_ylim([0.0, ylim[1]])
            # end if
            self.canvas.draw()
        # end if
    # end onAutoScale

    def onSave(self):
        if self.owner.isRunning():
            return
        # end if

        fileopt = {}
        fileopt['defaultextension'] = '.pdf'
        fileopt['filetypes'] = [('PDF files', '.pdf')]
        fileopt['initialfile'] = ''
        fileopt['parent'] = self.root
        fileopt['title'] = 'Save figure'
        dataFilename = tkFileDialog.asksaveasfilename(**fileopt)
        if dataFilename:
            try:
                pdfT = PdfPages(dataFilename)
                pdfT.savefig(self.figure)
                pdfT.close()
            except:
                pass
            # end try
        # end if
    # end onSave

# end OptimizerReport

# slalomWindow class, the main monitor window

class slalomWindow(object):
    """ main monitor window """

    def __init__(self, dataFilename, remoteHost = None, simulator = "atlas"):

        self.__version__ = "Version: 1.0 Build: 1711"

        self.deviceSimulator = simulator

        xIndex = 0
        y1Index = 0
        y2Index = 0
        y3Index = 0
        xLabel = None
        y1Label = None
        y2Label = None
        y3Label = None
        xType = 'int'
        dataSep = '\t'
        updateDelay = 30

        # in seconds
        self.updateDelay = 30
        self.delayMin = 30
        self.delayMax = 7200
        self.startTime = 0
        self.updateTime = 0
        self.updateCount = 0
        self.updateDelayMin = 0
        self.updateDelayMax = 0
        self.updateDelayMean = 0

        self.filemtime = 0

        self.fontsize = 10

        self.dataSep = dataSep

        self.count = 3

        self.datax = np.array([])
        self.dataxSel = np.array([])
        self.datay = {}
        self.dataySel = {}
        for idy in range(0, self.count):
            self.datay[idy] = np.array([])
            self.dataySel[idy] = np.array([])
        # end for

        self.xLabel = xLabel
        self.yLabel = {}
        self.yLabel[0] = y1Label if (y1Label is not None) else '$\mathregular{J_{SC}\ (mA/cm^{2})}$'
        self.yLabel[1] = y2Label if (y2Label is not None) else '$\mathregular{V_{OC}\ (V)}$'
        self.yLabel[2] = y3Label if (y3Label is not None) else '$\mathregular{Efficiency\ (\%)}$'

        self.xType = xType

        self.xIndex = xIndex if ((xIndex >= -1) and (xIndex <= 16)) else 0
        self.yIndex = [0, 0, 0]
        self.yIndex[0] = y1Index if ((y1Index >= 0) and (y1Index <= 16)) else 0
        self.yIndex[1] = y2Index if ((y2Index >= 0) and (y2Index <= 16)) else 0
        self.yIndex[2] = y3Index if ((y3Index >= 0) and (y3Index <= 16)) else 0

        self.root = Tk.Tk()
        self.root.bind_class("Entry","<Control-a>", self.onEntrySelectAll)
        self.root.bind_class("Entry","<Control-z>", self.onEntryUndo)
        self.root.bind_class("Entry","<Control-y>", self.onEntryRedo)
        self.root.withdraw()
        self.root.wm_title("SLALOM")

        self.figure = matplotlib.figure.Figure(figsize=(8,6), dpi=100, facecolor='#F1F1F1', linewidth=1.0, frameon=True)

        self.figure.subplots_adjust(top = 0.9, bottom = 0.1, left = 0.09, right = 0.95, wspace = 0.0, hspace = 0.25)

        self.plot = {}
        self.plot[0] = self.figure.add_subplot(311)
        self.plot[1] = self.figure.add_subplot(312, sharex=self.plot[0])
        self.plot[2] = self.figure.add_subplot(313, sharex=self.plot[0])

        for idy in range(0, self.count):
            self.plot[idy].format_coord = self.formatCoord
        # end for

        self.dataFilename = None
        self.dataDir = None
        self.dataZip = None

        self.dataFilenameLocal = None
        self.dataDirLocal = None
        self.dataZipLocal = None

        self.dataShortPath = None

        self.remoteHost = None

        self.threadrunning = False
        self.threadfinish = None
        self.thread = None

        self.killproc = 0

        self.iPoints = 0

        self.remoteHostEnabled = True

        self.updateDelayAuto = True

        # load the last used data filename, ssh host and update delay...
        # ... only loaded if no parameter is given as a command line argument
        if dataFilename is None:
            try:
                fileT = open("Settings/slalomMonitor.params", "r")
                # maximum number of line to read
                iMaxLine = 12
                iMaxParam = 5
                iLine = 0
                iParam = 0
                for lineT in fileT:
                    lineT = lineT.rstrip("\r\n")
                    if lineT.startswith("dataFilename = "):
                        dataFilename = lineT[len("dataFilename = "):]
                        if not dataFilename:
                            dataFilename = None
                        iParam += 1
                    elif lineT.startswith("remoteHost = ") and (remoteHost is None):
                        remoteHost = lineT[len("remoteHost = "):]
                        if not remoteHost:
                            remoteHost = None
                        iParam += 1
                    elif lineT.startswith("remoteHostEnabled = "):
                        try:
                            self.remoteHostEnabled = int(lineT[len("remoteHostEnabled = "):]) == 1
                        except:
                            self.remoteHostEnabled = False
                        iParam += 1
                    elif lineT.startswith("updateDelay = "):
                        updateDelay = lineT[len("updateDelay = "):]
                        if not updateDelay:
                            updateDelay = None
                        iParam += 1
                    elif lineT.startswith("updateDelayAuto = "):
                        try:
                            self.updateDelayAuto = int(lineT[len("updateDelayAuto = "):]) == 1
                        except:
                            self.updateDelayAuto = False
                        iParam += 1
                    # end if
                    iLine += 1
                    if (iLine >= iMaxLine) or (iParam >= iMaxParam):
                        break
                # end for
                fileT.close()
            except:
                pass
        # end if

        if remoteHost is None:
            self.remoteHostEnabled = False
        # end if

        topFrame = Tk.Frame(self.root)
        topFrame.pack(fill=Tk.X, padx=5, pady=5)
        self.dataFilenameLabel = Tk.Label(topFrame, width=10, text="Filename: ")
        self.dataFilenameLabel.pack(side=Tk.LEFT)
        dataFilenameValidate = (topFrame.register(self.onDataFilenameValidate), '%P')
        self.dataFilenameEdit = Tk.Entry(topFrame, validate="key", vcmd=dataFilenameValidate)
        self.dataFilenameEdit.pack(side=Tk.LEFT, fill=Tk.X, expand=1)
        self.dataFilenameEdit.insert(0, dataFilename if (dataFilename is not None) else "")
        self.dataFilenameEdit.prev = None
        self.dataFilenameEdit.next = None
        self.dataFilenameBrowse = ttk.Button(topFrame, width=4, text="...", command=self.onBrowse)
        self.dataFilenameBrowse.pack(side=Tk.LEFT, padx=(2, 2))

        self.sepLabel1 = Tk.Label(topFrame, text="|")
        self.sepLabel1.pack(side=Tk.LEFT)

        self.remoteHostLabel = Tk.Label(topFrame, text="SSH: ")
        self.remoteHostLabel.pack(side=Tk.LEFT)
        remoteHostValidate = (topFrame.register(self.onRemoteHostValidate), '%P')
        self.remoteHostEdit = Tk.Entry(topFrame, width=22, validate="key", vcmd=remoteHostValidate)
        self.remoteHostEdit.pack(side=Tk.LEFT)
        self.remoteHostEdit.insert(0, remoteHost if (remoteHost is not None) else "")
        self.remoteHostEdit.prev = None
        self.remoteHostEdit.next = None
        self.remoteHostVar = Tk.BooleanVar()
        self.remoteHostOpt = Tk.Checkbutton(topFrame, text="", variable=self.remoteHostVar, command=self.onRemoteHostOpt)
        self.remoteHostOpt.pack(side=Tk.LEFT)
        if self.remoteHostEnabled:
            self.remoteHostOpt.select()
        # end if

        self.buttonbar = Tk.Frame(self.root)
        self.buttonbar.pack(fill=Tk.X, padx=5, pady=5)

        self.updateDelayLabel = Tk.Label(self.buttonbar, width=10, text="Delay(s): ")
        self.updateDelayLabel.pack(side=Tk.LEFT)
        updateDelayValidate = (self.buttonbar.register(self.onDelayValidate), '%P')
        self.updateDelayEdit = Tk.Entry(self.buttonbar, width=6, validate="key", vcmd=updateDelayValidate)
        self.updateDelayEdit.pack(side=Tk.LEFT)
        self.updateDelayEdit.insert(0, updateDelay if (updateDelay is not None) else "30")
        self.updateDelayEdit.prev = None
        self.updateDelayEdit.next = None
        self.updateDelayVar = Tk.BooleanVar()
        self.updateDelayOpt = Tk.Checkbutton(self.buttonbar, text="Auto", variable=self.updateDelayVar, command=self.onUpdateDelayOpt)
        self.updateDelayOpt.pack(side=Tk.LEFT, padx=(0, 5))
        if self.updateDelayAuto:
            self.updateDelayOpt.select()
        # end if
        self.updateProgressVar = Tk.IntVar()
        self.updateProgress = ttk.Progressbar(self.buttonbar, length=120, orient='horizontal', mode='determinate', variable=self.updateProgressVar, maximum=(int(updateDelay) + 1) if (updateDelay is not None) else 31)
        self.updateProgress.pack(side=Tk.LEFT, padx=(0, 5))
        self.updateProgress.stopping = 0
        self.updateProgress.stoppingtime = None
        self.updateProgress.stopped = 0
        self.updateProgress.stoppedtime = None
        self.updateProgress.waiting = 0

        self.sepLabel2 = Tk.Label(self.buttonbar, text="|")
        self.sepLabel2.pack(side=Tk.LEFT)

        self.btnstyle_red = ttk.Style()
        self.btnstyle_red.configure("Red.TButton", foreground="#DE0015")
        self.btnstyle_black = ttk.Style()
        self.btnstyle_black.configure("Black.TButton", foreground="black")

        iconStart = Tk.PhotoImage(file='Images/iconstart.gif')
        self.btnStart = ttk.Button(self.buttonbar, width=10, text="Start", image=iconStart, compound=Tk.LEFT, command=self.onRestart)
        self.btnStart.pack(side=Tk.LEFT, padx=(5, 5))
        self.btnStart.configure(style="Black.TButton")

        iconStop = Tk.PhotoImage(file='Images/iconstop.gif')
        self.btnStop = ttk.Button(self.buttonbar, width=10, text="Stop", image=iconStop, compound=Tk.LEFT, command=self.onStop)
        self.btnStop.pack(side=Tk.LEFT, padx=(2, 5))
        self.btnStop.configure(style="Black.TButton")

        iconView = Tk.PhotoImage(file='Images/iconview.gif')
        self.btnView = ttk.Button(self.buttonbar, width=10, text="View data", image=iconView, compound=Tk.LEFT, command=self.onView)
        self.btnView.pack(side=Tk.LEFT, padx=(2, 5))
        self.btnView.configure(style="Black.TButton")

        iconReport = Tk.PhotoImage(file='Images/iconreport.gif')
        self.btnReport = ttk.Button(self.buttonbar, width=10, text="View JV", image=iconReport, compound=Tk.LEFT, command=self.onShowReport)
        self.btnReport.pack(side=Tk.LEFT, padx=(2, 5))
        self.btnReport.configure(style="Black.TButton")

        iconReportb = Tk.PhotoImage(file='Images/iconreportb.gif')
        self.btnReportb = ttk.Button(self.buttonbar, width=10, text="View SR", image=iconReportb, compound=Tk.LEFT, command=self.onShowReportb)
        self.btnReportb.pack(side=Tk.LEFT, padx=(2, 5))
        self.btnReportb.configure(style="Black.TButton")

        self.actionbutton = None
        self.timercount = 0.0
        self.timerdelay = 500 # milliseconds
        self.timerProgressVar = Tk.StringVar()
        self.timerProgress = Tk.Label(self.buttonbar, text=" ", textvariable=self.timerProgressVar)
        self.timerProgress.pack(side=Tk.LEFT, padx=(2, 0))

        self.labelFill = Tk.Label(self.buttonbar, text=" ")
        self.labelFill.pack(side=Tk.LEFT, fill=Tk.X, expand=1)

        self.btnClose = ttk.Button(self.buttonbar, width=10, text="Close", image=None, command=self.onClose)
        self.btnClose.pack(side=Tk.LEFT, padx=(0, 5))
        self.btnClose.configure(style="Black.TButton")

        iconAbout = Tk.PhotoImage(file='Images/iconabout.gif')
        self.btnAbout = ttk.Button(self.buttonbar, width=3, text="", image=iconAbout, command=self.onAbout)
        self.btnAbout.pack(side=Tk.LEFT, padx=(0, 5))
        self.btnAbout.configure(style="Black.TButton")

        paramFrame = Tk.Frame(self.root)
        paramFrame.pack(fill=Tk.X, padx=5, pady=5)

        self.paramSep = "  ;  "
        self.paramIndexFormat = '{0:05d}'
        self.paramName = None
        self.paramCount = 0
        self.paramlist = list()
        self.paramlistThread = list()
        self.paramlistBox = ttk.Combobox(paramFrame, state='readonly')
        self.paramlistBox.pack(side=Tk.LEFT, padx=(5, 5), fill=Tk.X, expand=1)
        self.paramlistBox['state'] = 'readonly'
        self.paramlistBox.bind('<<ComboboxSelected>>', self.onParamlistBox)
        self.paramlistCurrent = 0
        self.optimlist = list()
        self.optimout = list()

        self.efficiencyMin = 0.0
        self.efficiencyMax = 0.0
        self.efficiencySel = 0.0

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas._tkcanvas.config(highlightthickness=0)
        self.canvas.mpl_connect('button_press_event', self.onCanvasClick)

        try:
            self.toolbar = NavigationToolbar(self)
        except:
            self.toolbar = None
            pass
        self.toolbar.pack(side=Tk.BOTTOM, fill=Tk.X)

        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

        self.canvas.show()

        self.root.protocol('WM_DELETE_WINDOW', self.onClose)

        self.scattercolor = ['#8184FF', '#FF7D7D', '#3FFF3F']
        self.scattercolorborder = ['#00178C', '#BC0000', '#007806']
        self.scattermarkersize = [10.0, 10.0, 10.0]
        self.linecolor = ['b', 'r', 'g']
        self.linestyle = ['-', '-', '-']
        self.linesize = [1.0, 1.0, 1.0]
        self.markersm = ['o', 'o', 'o']
        self.markersizesm = [6.0, 6.0, 6.0]
        self.markerhg = ['.', '.', '.']
        self.markersizehg = [3.0, 3.0, 3.0]
        self.line = {}
        self.scatter = {}
        for idy in range(0, self.count):
            self.line[idy] = None
            self.scatter[idy] = None
        # end if

        # center the main window
        iw = self.root.winfo_screenwidth()
        ih = self.root.winfo_screenheight()
        isize = (940, 600)
        ix = (iw - isize[0]) / 2
        iy = (ih - isize[1]) / 2
        self.root.geometry("%dx%d+%d+%d" % (isize + (ix, iy)))

        self.root.deiconify()

        self.root.minsize(800, 600)

        for idy in range(0, self.count):
            try:
                self.plot[idy].tick_params(axis='x', labelsize=self.fontsize)
                self.plot[idy].tick_params(axis='y', labelsize=self.fontsize)
            except:
                [tx.label.set_fontsize(self.fontsize) for tx in self.plot[idy].xaxis.get_major_ticks()]
                [ty.label.set_fontsize(self.fontsize) for ty in self.plot[idy].yaxis.get_major_ticks()]
                pass

            if self.yLabel[idy] is not None:
                self.plot[idy].set_ylabel(self.yLabel[idy], fontsize=self.fontsize)
            if (self.xType == 'int'):
                self.plot[idy].xaxis.set_major_locator(MaxNLocator(integer=True))

            self.plot[idy].yaxis.label.set_color(self.linecolor[idy])
            try:
                if idy < (self.count - 1):
                    pl.setp(self.plot[idy].get_xticklabels(), visible=False)
                # end if
                self.plot[idy].tick_params(axis='y', colors=self.linecolor[idy])
                self.plot[idy].spines['left'].set_color(self.linecolor[idy])
                self.plot[idy].spines['top'].set_color(self.linecolor[idy])
                self.plot[idy].spines['right'].set_color(self.linecolor[idy])
                self.plot[idy].spines['bottom'].set_color(self.linecolor[idy])
                self.plot[idy].xaxis.major.locator.set_params(nbins=20)
                self.plot[idy].yaxis.major.locator.set_params(nbins=5)
                self.plot[idy].grid(True)
            except:
                [ty.set_color(self.linecolor[idy]) for ty in self.plot[idy].yaxis.get_ticklines()]
                [ty.set_color(self.linecolor[idy]) for ty in self.plot[idy].yaxis.get_ticklabels()]
                pass
        # end for

        self.strViewerFileContent = None
        self.viewer = None
        self.listKeyword = ['Optimization', 'Optim', 'Brute', 'Snap', 'tolerance', 'jaceps',
                            'Parameter', 'StartValue', 'EndValue', 'InitValue',
                            'NormValue', 'Points', 'L-BFGS-B', 'SQLP', 'Index', 'Time',
                            'Jm(mA/cm2)', 'Vm(V)', 'FF(%)', 'Jsc(mA/cm2)', 'Voc(V)',
                            'Efficiency']
        self.listKeyword2 = None

        self.strReportFileName = [list(), list()]
        self.strReportFileContent = [list(), list()]
        self.report = [None, None]

        self.strReportFileNameLocal = [list(), list()]

        self.popmenu = Tk.Menu(self.root, tearoff=0)
        self.popmenu.add_command(label="Restart the optimizer", command=self.onRestart)
        self.popmenu.add_command(label="Stop the optimizer", command=self.onStop)
        self.popmenu.add_command(label="Kill the optimizer", command=self.onKill)
        self.popmenu.add_separator()
        self.popmenu.add_command(label="View data file", command=self.onView)
        self.popmenu.add_command(label="View J-V characteristics", command=self.onShowReport)
        self.popmenu.add_command(label="View Spectral Response", command=self.onShowReportb)
        self.popmenu.add_separator()
        self.popmenu.add_command(label="Auto scale", command=self.onAutoScale)
        self.popmenu.add_separator()
        self.popmenu.add_command(label="Save as PDF", command=self.onSave)
        self.popmenu.add_separator()
        self.popmenu.add_command(label="Close", command=self.onClose)
        self.popmenu.add_separator()
        self.popmenu.add_command(label="About...", command=self.onAbout)
        self.root.bind("<Button-3>", self.onPopmenu)

        self.root.bind("<Prior>", self.onPageDown)
        self.root.bind("<Next>", self.onPageUp)

        if (os.name == "nt"):
            self.root.iconbitmap(r'Images/slalom.ico')
        else:
            iconSlalom = Tk.PhotoImage(file='Images/slalom.gif')
            self.root.tk.call('wm', 'iconphoto', self.root._w, iconSlalom)
        # end if

        self.onUpdateData(force = True)

        self.root.mainloop()

        return
    # end __init__

    def formatCoord(self, x, y):
        fx = round(x)
        if (x < (fx - 0.1)) or (x > (fx + 0.1)):
            return ""
        # end if

        idx = int(fx)
        return 'Index: %03d ; Value: %08.5f' % (idx, y)
    # end formatCoord

    def onPageMove(self, event, idir):
        try:
            if self.isRunning():
                return
            # end if

            indexT = self.paramlistBox.current() + idir
            indexMax = len(self.paramlistBox["values"])
            if (indexT < 0) or (indexT >= indexMax):
                return
            # end if
            # self.canvas.draw() called in updateSel
            self.paramlistBox.current(newindex = indexT)
            self.updateSel(index = indexT)
            for report in self.report:
                if (report is not None):
                    report.frame.paramlistBox.current(newindex = indexT)
                    report.frame.updateSel(index = report.frame.paramlistBox.current())
                # end if
            # end for
            if (self.viewer is not None):
                self.viewer.frame.selectLine(index = indexT)
            # end if
            self.paramlistCurrent = self.paramlistBox.current()
        except:
            pass
    # end onPageDown

    def onPageDown(self, event):
        return self.onPageMove(event, -1)
    # end onPageDown

    def onPageUp(self, event):
        return self.onPageMove(event, 1)
    # end onPageUp

    def onRestart(self):
        self.onUpdateData(force = True)
    # end onRestart

    def onSave(self):
        if self.isRunning():
            return
        # end if

        fileopt = {}
        fileopt['defaultextension'] = '.pdf'
        fileopt['filetypes'] = [('PDF files', '.pdf')]
        fileopt['initialfile'] = ''
        fileopt['parent'] = self.root
        fileopt['title'] = 'Save figure'
        dataFilename = tkFileDialog.asksaveasfilename(**fileopt)
        if dataFilename:
            try:
                pdfT = PdfPages(dataFilename)
                pdfT.savefig(self.figure)
                pdfT.close()
            except:
                pass
            # end try
        # end if
    # end onSave

    def onAutoScale(self):
        if self.isRunning():
            return
        # end if

        if (self.iPoints >= 1):
            for idy in range(0, self.count):
                self.plot[idy].relim()
                self.plot[idy].autoscale()
            # end for
            self.canvas.draw()
            return
        # end if
    # end onAutoScale

    def checkFile(self, filename):

        tFilename = self.dataDir + filename
        remoteMon = self.remoteHostEnabled and (self.remoteHost is not None) and ("@" in self.remoteHost)

        try:
            self.root.config(cursor="wait")
            self.root.update()
        except:
            pass

        bCheck = False
        updateTime = None

        if not remoteMon:
            try:
                if os.path.exists(tFilename):
                    statT = os.stat(tFilename)
                    updateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(statT.st_mtime))
                    bCheck = True
                # end if
            except:
                pass
            # end try
        else:
            try:
                STDDEVNULL = open(os.devnull, 'w')
                strT = subprocess.check_output(['ssh', self.remoteHost, "stat", "--printf=%Y", tFilename], stderr=STDDEVNULL)
                updateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(strT)))
                bCheck = True
            except:
                pass
            # end try
        # end if

        self.root.config(cursor="")

        return (bCheck, updateTime)
    # end checkFile

    def isStopped(self):
        if (self.updateProgress.stopped >= 1):
            return True
        # end if

        (bStopped, updateTime) = self.checkFile("stopped.txt")
        if bStopped:
            self.updateProgress.stopped = 1
            self.updateProgress.stoppedtime = updateTime
        # end if
        return bStopped
    # end isStopped

    def isStopping(self):
        if (self.updateProgress.stopping >= 1):
            return True
        # end if

        (bStopping, updateTime) = self.checkFile("stop.txt")
        if bStopping:
            self.updateProgress.stopping = 1
            self.updateProgress.stoppingtime = updateTime
        # end if
        return bStopping
    # end isStopping

    def onKill(self):

        if self.isRunning():
            return False
        # end if

        if (self.updateProgress.stopped >= 1):
            return True
        # end if

        # first, try to kindly stop the optimizer... if it doesn't work, kill it (! the last data will then be lost)
        if self.killproc < 1:
            self.killproc += 1
            return self.onStop()
        # end if
        self.killproc = 0

        bStopped = self.isStopped()
        if bStopped:
            tkMessageBox.showinfo("SLALOM", "The optimization was stopped @ "
                                  + (self.updateProgress.stoppedtime if (self.updateProgress.stoppedtime is not None)
                                     else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            return True
        # end if

        remoteMon = self.remoteHostEnabled and (self.remoteHost is not None) and ("@" in self.remoteHost)

        procFilename = self.dataDir + "proc.txt"
        stoppedFilename = self.dataDir + "stopped.txt"

        if not tkMessageBox.askyesno("SLALOM", "Kill the optimization process?\n", default=tkMessageBox.NO, parent=self.root):
            return False
        # end if

        try:
            self.root.config(cursor="wait")
            self.root.update()
        except:
            pass

        STDDEVNULL = open(os.devnull, 'w')

        fileT = None
        try:
            if remoteMon:
                procId = subprocess.check_output(['ssh', self.remoteHost, 'cat', procFilename], stderr=STDDEVNULL)
            else:
                fileT = open(procFilename, "r")
                procId = str(fileT.read())
                fileT.close()
            # end if
        except:
            self.root.config(cursor="")
            tkMessageBox.showwarning("SLALOM", "Optimization process not found", parent=self.root)
            return False
        # end try

        lenId = len(procId)
        if (lenId < 1) or (lenId > 64):
            self.root.config(cursor="")
            tkMessageBox.showwarning("SLALOM", "Optimization process not found", parent=self.root)
            return False
        # end try

        try:
            cmdT = ['ssh', self.remoteHost, 'kill', procId] if remoteMon else ['kill', procId]
            try:
                subprocess.Popen(cmdT, stderr=STDDEVNULL, stdout=STDDEVNULL)
            except:
                pass
            # end try
            iT = 2 if remoteMon else 0
            cmdT[iT] = 'pkill'
            arSim = ['deckbuild.exe', 'deckbld.exe', 'atlas.exe', 'atlas.exe2', 'atlas.exe3', 'atlas2.exe', 'atlas3.exe']
            for tSim in arSim:
                try:
                    cmdT[iT + 1] = tSim
                    subprocess.Popen(cmdT, stderr=STDDEVNULL, stdout=STDDEVNULL)
                except:
                    pass
                # end try
            # end for
        except:
            pass
        # end try

        try:
            if remoteMon:
                STDDEVNULL = open(os.devnull, 'w')
                subprocess.Popen(['ssh', self.remoteHost, 'touch', stoppedFilename], stdout=STDDEVNULL)
                self.updateProgress.stopped = 1
            else:
                fileT = open(stoppedFilename, "w")
                fileT.write("SLALOM\nStopped from the monitor\n")
                fileT.close()
                self.updateProgress.stopped = 1 if os.path.exists(stoppedFilename) else 0
            # end if
        except:
            pass
        # end try

        if self.updateProgress.stopped == 1:
            self.updateProgressVar.set(0)
            self.updateProgress.stop()
            tkMessageBox.showinfo("SLALOM", "The optimization process was killed", parent=self.root)
        # end if

        self.root.config(cursor="")

    def onStop(self):

        if self.isRunning():
            return False
        # end if

        bStopped = self.isStopped()
        if bStopped:
            self.updateProgressVar.set(0)
            self.updateProgress.stop()
            tkMessageBox.showinfo("SLALOM", "The optimization was stopped @ "
                                  + (self.updateProgress.stoppedtime if (self.updateProgress.stoppedtime is not None)
                                     else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            return True
        # end if

        bStopping = self.isStopping()
        if bStopping:
            tkMessageBox.showinfo("SLALOM", "The optimization is being stopped since "
                                  + (self.updateProgress.stoppingtime if (self.updateProgress.stoppingtime is not None)
                                     else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                     parent=self.root)
            return True
        # end if

        stopFilename = self.dataDir + "stop.txt"

        remoteMon = self.remoteHostEnabled and (self.remoteHost is not None) and ("@" in self.remoteHost)

        if not tkMessageBox.askyesno("SLALOM", "Stop the optimization?", default=tkMessageBox.NO, parent=self.root):
            return False
        # end if

        try:
            self.root.config(cursor="wait")
            self.root.update()
        except:
            pass

        try:
            self.updateProgress.stopping = 0
            if remoteMon:
                STDDEVNULL = open(os.devnull, 'w')
                subprocess.Popen(['ssh', self.remoteHost, 'touch', stopFilename], stdout=STDDEVNULL)
                self.updateProgress.stopping = 1
            else:
                fileT = open(stopFilename, "w")
                fileT.write("SLALOM\nStopped from the monitor\n")
                fileT.close()
                self.updateProgress.stopping = 1 if os.path.exists(stopFilename) else 0
            # end if
            if self.updateProgress.stopping == 1:
                tkMessageBox.showinfo("SLALOM", "The optimization will stop at the end of the running iteration", parent=self.root)
            # end if
        except:
            pass
        # end try

        self.root.config(cursor="")

        return True

    # end onStop

    def onEntryUndo(self, event):
        try:
            if event.widget.prev is not None:
                event.widget.next = event.widget.get()
                strT = event.widget.prev
                idx = event.widget.index(Tk.INSERT)
                event.widget.delete(0, Tk.END)
                event.widget.insert(0, strT)
                event.widget.prev = strT
                event.widget.icursor(idx + 1)
        except:
            pass
    # end onEntryUndo

    def onEntryRedo(self, event):
        try:
            if event.widget.next is not None:
                idx = event.widget.index(Tk.INSERT)
                strT = event.widget.prev
                event.widget.delete(0, Tk.END)
                event.widget.insert(0, event.widget.next)
                event.widget.prev = strT
                event.widget.icursor(idx + 1)
        except:
            pass
    # end onEntryRedo

    def onEntrySelectAll(self, event):
        try:
            event.widget.select_range(0, Tk.END)
        except:
            pass
    # end onEntrySelectAll

    def onDataFilenameValidate(self, sp):
        try:
            if (not sp) or (len(sp) <= 255):
                self.dataFilenameEdit.prev = sp
                return True
            # end if
            return False
        except:
            return True
        # end try
    # end onDataFilenameValidate

    def onDelayValidate(self, sp):
        try:
            if (not sp) or ((len(sp) <= 4) and (re.match("^[0-9]*$", sp))):
                self.updateDelayEdit.prev = sp
                return True
            # end if
            return False
        except:
            return True
        # end try
    # end onDelayValidate

    def onRemoteHostValidate(self, sp):
        try:
            if (not sp) or (len(sp) <= 63):
                self.remoteHostEdit.prev = sp
                return True
            # end if
            return False
        except Exception as excT:
            return True
        # end try
    # end onRemoteHostValidate

    def onRemoteHostOpt(self):
        try:
            self.remoteHostEnabled = self.remoteHostVar.get()
        except:
            pass
    # end onRemoteHostOpt

    def onUpdateDelayOpt(self):
        try:
            self.updateDelayAuto = self.updateDelayVar.get()
        except:
            pass
    # end onUpdateDelayOpt

    def onParamlistBox(self, event):

        if self.isRunning():
            self.paramlistBox.current(newindex = self.paramlistCurrent)
            return
        # end if

        try:
            self.paramlistBox.selection_clear()
            indexT = self.paramlistBox.current()
            self.updateSel(index=indexT)
            for report in self.report:
                if (report is not None):
                    report.frame.paramlistBox.current(newindex = indexT)
                    report.frame.updateSel(index = report.frame.paramlistBox.current())
                # end if
            # end for
            if (self.viewer is not None):
                self.viewer.frame.selectLine(index = indexT)
            # end if
            self.paramlistCurrent = indexT
        except:
            pass
    # end onParamlistBox

    def onPopmenu(self, event):
        try:
            self.popmenu.post(event.x_root, event.y_root)
        except:
            pass
    # end onPopmenu

    def onCanvasClick(self, event):
        try:
            if self.isRunning():
                return
            # end if

            if (event.button != 1) or (self.iPoints < 1):
                return
            # end if
            subplotbox = self.plot[0].get_window_extent().transformed(self.figure.dpi_scale_trans.inverted())
            iWidth, iHeight = subplotbox.width * self.figure.dpi, subplotbox.height * self.figure.dpi
            fDeltaX = 2.0 * float(self.scattermarkersize[0]) / float(iWidth)
            fDeltaY = 2.0 * float(self.scattermarkersize[0]) / float(iHeight)
            indexX = (np.abs(self.datax - event.xdata)).argmin()
            if (indexX < 0) or (indexX >= self.iPoints):
                return
            # end if
            fx = self.datax[indexX]
            fDeltaX *= math.fabs(fx)
            bXfound = ((fx > (event.xdata - fDeltaX)) and (fx < (event.xdata + fDeltaX)))
            if bXfound:
                idy = -1
                for ii in range(0, self.count):
                    if self.plot[ii] == event.inaxes:
                        idy = ii
                        break
                    # end if
                # end for
                if idy >= 0:
                    indexY = (np.abs(self.datay[idy] - event.ydata)).argmin()
                    if (indexY < 0) or (indexY >= self.iPoints):
                        return
                    # end if
                    fy = self.datay[idy][indexY]
                    fDeltaY *= math.fabs(fy)
                    bYfound = (fy > (event.ydata - fDeltaY)) and (fy < (event.ydata + fDeltaY))
                    if bYfound:
                        self.paramlistBox.current(newindex = indexX)
                        # self.canvas.draw() called in updateSel
                        self.updateSel(index = indexX)
                        for report in self.report:
                            if (report is not None):
                                report.frame.paramlistBox.current(newindex = indexX)
                                report.frame.updateSel(index = report.frame.paramlistBox.current())
                            # end if
                        # end for
                        if (self.viewer is not None):
                            self.viewer.frame.selectLine(index = indexX)
                        # end if
                        self.paramlistCurrent = self.paramlistBox.current()
                    # end if
                # end if
            # end if
        except:
            pass
    # end onCanvasClick

    def onBrowse(self):
        if self.isRunning():
            return
        # end if

        if self.remoteHostEnabled:
            if not tkMessageBox.askyesno("SLALOM", "SSH monitoring enabled. Switch to local monitoring?",
                                          default=tkMessageBox.NO, parent=self.root):
                return
            # end if
            self.remoteHostVar = 0
            self.remoteHostEnabled = False
        # end if

        fileopt = {}
        fileopt['defaultextension'] = ''
        fileopt['filetypes'] = [('SLALOM efficiency output file', 'simuloutput_optimized.txt')]
        fileopt['initialfile'] = 'simuloutput_optimized.txt'
        fileopt['parent'] = self.root
        fileopt['title'] = 'Open the SLALOM efficiency output filename'
        dataFilename = tkFileDialog.askopenfilename(**fileopt)
        if dataFilename:
            try:
                self.dataFilenameEdit.delete(0, Tk.END)
                self.dataFilenameEdit.insert(0, dataFilename)
                self.updateParam()
                self.onUpdateData(force = True)
            except:
                pass
        # end if
    # end onBrowse

    def onView(self):
        if self.isRunning():
            return
        # end if

        if self.viewer is not None:
            self.viewer.focus()
            return
        # end if

        if self.dataFilename is None:
            return
        # end if

        try:
            dataFilename = self.dataFilename

            self.updateParam()

            if dataFilename != self.dataFilename:
                if not tkMessageBox.askyesno("SLALOM", "The data filename has changed.\nSynchonize data?", default=tkMessageBox.NO, parent=self.root):
                    return
                # end if
                self.onUpdateData(force = True)
                return
            # end try

            if (self.strViewerFileContent is None) or (self.strViewerFileContent == ""):

                remoteMon = self.remoteHostEnabled and (self.remoteHost is not None) and ("@" in self.remoteHost)

                try:
                    self.root.config(cursor="wait")
                    self.root.update()
                except:
                    pass

                # get the file content locally (as it was already copied from the remote server).
                # the ssh connexion should use auth keys, not password, for obvious security reasons.

                fileT = None
                try:
                    fileT = open(self.dataFilenameLocal, "r")
                    self.strViewerFileContent = fileT.read()
                    fileT.close()
                except:
                    self.root.config(cursor="")
                    tkMessageBox.showwarning("SLALOM", "Optimization data file not found:\n%s" % self.dataFilenameLocal, parent=self.root)
                    return False
                # end try

                self.root.config(cursor="")
            # end if

            if (self.strViewerFileContent is None) or (len(self.strViewerFileContent) < 32):
                tkMessageBox.showwarning("SLALOM", "Optimization data file not found", parent=self.root)
                return False
            # end if

            self.viewer = Tk.Toplevel(self.root)
            self.viewer.protocol("WM_DELETE_WINDOW", self.onViewerClose)

            if (os.name == "nt"):
                self.viewer.iconbitmap('Images/slalomd.ico')
            else:
                iconSlalom = Tk.PhotoImage(file='Images/slalomd.gif')
                self.viewer.tk.call('wm', 'iconphoto', self.viewer._w, iconSlalom)
            # end if

            self.viewer.frame = OptimizerViewer(self.viewer)
            self.viewer.frame.onClose = self.onViewerClose
            self.viewer.frame.pack(expand=1, fill="both")
            self.viewer.frame.setText(self.strViewerFileContent, self.listKeyword, self.listKeyword2)
            self.root.wait_window(self.viewer)

        except:
            pass

    # end onView

    def onViewerClose(self):
        self.viewer.destroy()
        self.viewer = None
    # end onViewerClose

    def isRunning(self):
        if (self.thread is None):
            self.threadrunning = False
            return self.threadrunning
        # end if
        if (not self.thread.isAlive()):
            self.thread = None
            self.threadrunning = False
        # end if
        return self.threadrunning
    # end isRunning

    def setRunning(self, threadrunning = True, fromthread = False):
        self.threadrunning = threadrunning
        if fromthread:
            if not self.threadrunning:
                self.thread = None
            # end if
            # do not update gui from the working thread
            return
        # end if
        try:
            if self.threadrunning:
                if self.actionbutton is not None:
                    self.actionbutton.configure(style='Red.TButton')
                # end if
                self.timercount = 0.0
                self.timerProgress.configure(foreground='#DE0015')
                self.timerProgressVar.set('Running...')
            else:
                if self.actionbutton is not None:
                    self.actionbutton.configure(style='Black.TButton')
                # end if
                self.timerProgress.configure(foreground='black')
                self.timerProgressVar.set(' ')
                self.timercount = 0.0
                self.actionbutton = None
            # end if
        except:
            pass
    # end setRunning

    def onThreadMonitor(self):
        threadrunning = self.isRunning()
        try:
            if not threadrunning:
                self.setRunning(threadrunning = False, fromthread = False)
                if self.threadfinish is not None:
                    self.threadfinish()
                    self.threadfinish = None
                # end if
                return
            # end if
            self.timerProgressVar.set('Running... %04.1f' % self.timercount)
            timerdelay = float(self.timerdelay) / 1000.0
            self.timercount += timerdelay
            self.root.after(self.timerdelay, self.onThreadMonitor)
        except:
            pass
    # end onThreadMonitor

    def updateReport(self):

        for ii in range(0, len(self.report)):
            if (self.report[ii] is not None):
                try:
                    self.report[ii].frame.setParam(self.paramlist, self.optimlist, self.optimout, self.strReportFileContent[ii])
                except:
                    pass
                # end try
            # end if
        # end for

    # end updateReport

    def showReport(self, index = 0):

        if self.isRunning():
            return
        # end if

        if (index < 0) or (index >= len(self.report)):
            return
        # end if

        if self.report[index] is not None:
            self.report[index].focus()
            return
        # end if

        dataFilename = self.dataFilename

        self.updateParam()

        if dataFilename != self.dataFilename:
            if not tkMessageBox.askyesno("SLALOM", "The data filename has changed.\nSynchonize data?", default=tkMessageBox.NO, parent=self.root):
                return
            # end if
            self.onUpdateData(force = True)
            return
        # end try

        strReportFileName = self.strReportFileName[index]
        strReportFileContent = self.strReportFileContent[index]

        dataNV = (self.dataFilename is None) or (strReportFileName is None) or (strReportFileContent is None)
        if dataNV == False:
            iFnameLen = len(strReportFileName)
            iFcontentLen = len(strReportFileContent)
            dataNV = (iFnameLen < 1) or (iFcontentLen < 1) or (iFcontentLen != iFnameLen) or (iFcontentLen != self.iPoints)
        # end if
        if dataNV:
            tkMessageBox.showwarning("SLALOM", "Report data files not found", parent=self.root)
            pass
        # end if

        try:
            self.report[index] = Tk.Toplevel(self.root)
            self.report[index].withdraw()
            self.report[index].protocol("WM_DELETE_WINDOW", self.onReportClose if (index == 0) else self.onReportCloseb)

            if (os.name == "nt"):
                self.report[index].iconbitmap(r'Images/slalomp.ico')
            else:
                iconSlalom = Tk.PhotoImage(file='Images/slalomp.gif')
                self.report[index].tk.call('wm', 'iconphoto', self.report._w, iconSlalom)
            # end if

            self.report[index].frame = OptimizerReport(self, index, self.report[index])
            self.report[index].frame.onClose = self.onReportClose if (index == 0) else self.onReportCloseb
            self.report[index].frame.pack(expand=1, fill="both")
            self.report[index].frame.setParam(self.paramlist, self.optimlist, self.optimout, strReportFileContent)

            # center the main window
            iw = self.report[index].winfo_screenwidth()
            ih = self.report[index].winfo_screenheight()
            isize = (800, 600)
            ix = (iw - isize[0]) / 2
            iy = (ih - isize[1]) / 2
            self.report[index].geometry("%dx%d+%d+%d" % (isize + (ix, iy)))

            self.report[index].deiconify()

            self.report[index].minsize(600, 400)

            self.root.wait_window(self.report[index])

        except:
            pass

        # end try

    # end showReport

    def onShowReport(self):

        self.showReport(index = 0)

    # end onShowReport

    def onShowReportb(self):

        self.showReport(index = 1)

    # end onShowReportb

    def onReportClose(self):
        if self.report[0] is not None:
            self.report[0].destroy()
            self.report[0] = None
        # end if
    # end onReportClose

    def onReportCloseb(self):
        if self.report[1] is not None:
            self.report[1].destroy()
            self.report[1] = None
        # end if
    # end onReportClose

    def updateParam(self):

        try:
            self.remoteHost = self.remoteHostEdit.get().strip("\t ")
            if not self.remoteHost:
                self.remoteHost = None
            # end if
        except:
            pass
        # end try

        remoteMon = self.remoteHostEnabled and (self.remoteHost is not None) and ("@" in self.remoteHost)

        try:
            updateDelay = int(self.updateDelayEdit.get())
            if (updateDelay >= self.delayMin) and (updateDelay <= self.delayMax):
                self.updateDelay = updateDelay
                self.updateProgress.configure(maximum=str(self.updateDelay + 3))
            # end if
        except:
            pass

        dataFilename = self.dataFilename

        sepFrom = '/' if (os.name == "nt") else '\\'
        sepTo = '\\' if (os.name == "nt") else '/'

        try:
            self.dataFilename = self.dataFilenameEdit.get().strip("\r\n\t ")

            if not self.dataFilename:

                self.dataFilename = None
                self.dataDir = None
                self.dataZip = None
                self.dataShortPath = None
                self.dataFilenameLocal = None
                self.dataDirLocal = None
                self.dataZipLocal = None

            elif dataFilename != self.dataFilename:

                if remoteMon:
                    # always normalize the server-side (always Linux) filenames
                    self.dataFilename = self.dataFilename.replace('\\', '/')
                else:
                    self.dataFilename = self.dataFilename.replace(sepFrom, sepTo)
                # end if

                dirSepChar = '/' if remoteMon else ('\\' if (os.name == "nt") else '/')

                iSep = self.dataFilename.rfind(dirSepChar)
                if iSep > 0:
                    self.dataDir = self.dataFilename[:iSep + 1]
                # end if

                iii = self.dataFilename.find(dirSepChar + 'output' + dirSepChar)
                if (iii >= 0):
                    self.dataShortPath = self.dataFilename[iii+8:]

                    iSep = self.dataFilename.rfind(dirSepChar)
                    if iSep > 0:
                        self.dataZip = self.dataFilename[:iSep] + '.zip'
                    # end if

                    if remoteMon:
                        # remote server
                        self.dataDirLocal = os.path.dirname(os.path.realpath(__file__))
                        if not self.dataDirLocal.endswith(dirSepChar):
                            self.dataDirLocal += dirSepChar
                        # end if
                        strDN = 'Device' + dirSepChar
                        strDN += ('Silvaco' + dirSepChar) if (self.deviceSimulator == "atlas") else ('TiberCAD' + dirSepChar)
                        self.dataDirLocal += (strDN + 'output' + dirSepChar) + self.dataShortPath
                        iSep = self.dataDirLocal.rfind(dirSepChar)
                        if iSep > 0:
                            self.dataDirLocal = self.dataDirLocal[:iSep + 1]
                            self.dataZipLocal = self.dataDirLocal[:iSep] + '.zip'
                            self.dataFilenameLocal = self.dataDirLocal
                            iSep = self.dataFilename.rfind(dirSepChar)
                            if iSep > 0:
                                self.dataFilenameLocal += self.dataFilename[iSep + 1:]
                            # end if
                        # end if
                        if not os.path.exists(self.dataDirLocal):
                            os.makedirs(self.dataDirLocal)
                        # end if
                    else:
                        # local server
                        self.dataFilenameLocal = self.dataFilename
                        self.dataDirLocal = self.dataDir
                        self.dataZipLocal = self.dataZip
                    # end if

                # end if

            # end if

        except:
            pass
        # end try

        if self.dataFilename is None:
            return
        # end if

        try:

            if remoteMon:
                # always normalize the server-side (always Linux) filenames
                self.dataDir = self.dataDir.replace('\\', '/')
                self.dataZip = self.dataZip.replace('\\', '/')
                self.dataShortPath = self.dataShortPath.replace('\\', '/')
            else:
                self.dataDir = self.dataDir.replace(sepFrom, sepTo)
                self.dataZip = self.dataZip.replace(sepFrom, sepTo)
                self.dataShortPath = self.dataShortPath.replace(sepFrom, sepTo)
            # end if

            self.dataFilenameLocal = self.dataFilenameLocal.replace(sepFrom, sepTo)
            self.dataDirLocal = self.dataDirLocal.replace(sepFrom, sepTo)
            self.dataZipLocal = self.dataZipLocal.replace(sepFrom, sepTo)

            if dataFilename != self.dataFilename:
                self.dataFilenameEdit.delete(0, Tk.END)
                self.dataFilenameEdit.insert(0, self.dataFilename)
                self.remoteHostEdit.delete(0, Tk.END)
                self.remoteHostEdit.insert(0, self.remoteHost if (self.remoteHost is not None) else '')
            # end if
 
        except:
            pass
        # end try

    # end updateParam

    def resetData(self):
        self.datax = np.delete(self.datax, np.s_[:])
        for idy in range(0, self.count):
            self.datay[idy] = np.delete(self.datay[idy], np.s_[:])
        # end for
        self.iPoints = 0
        del self.paramlistThread[:]
        self.paramlistThread = list()
        self.paramName = None
        self.paramCount = 0
        self.strViewerFileContent = None

        for strReportFileName in self.strReportFileName:
            del strReportFileName[:]
            strReportFileName = list()
        # end for
        for strReportFileContent in self.strReportFileContent:
            del strReportFileContent[:]
            strReportFileContent = list()
        # end for
        for strReportFileNameLocal in self.strReportFileNameLocal:
            del strReportFileNameLocal[:]
            strReportFileNameLocal = list()
        # end for

        del self.optimlist[:]
        self.optimlist = list()
        del self.optimout[:]
        self.optimout = list()
    # end resetData

    def updateDataThread(self):

        if self.dataFilename is None:
            self.setRunning(threadrunning = False, fromthread = True)
            return
        # end if

        remoteMon = self.remoteHostEnabled and (self.remoteHost is not None) and ("@" in self.remoteHost)

        filemtime = 0

        STDDEVNULL = open(os.devnull, 'w')

        if not remoteMon:
            try:
                if os.path.isfile(self.dataFilename) == False:
                    self.resetData()
                    self.setRunning(threadrunning = False, fromthread = True)
                    return
                # end if
                filemtime = os.path.getmtime(self.dataFilename)
            except:
                self.resetData()
                self.setRunning(threadrunning = False, fromthread = True)
                return
            # end try
        else:
            try:
                strT = subprocess.check_output(['ssh', self.remoteHost, "stat", "--printf=%Y", self.dataFilename], stderr=STDDEVNULL)
                filemtime = int(strT)
            except:
                self.resetData()
                self.setRunning(threadrunning = False, fromthread = True)
                return
            # end try
        # end if

        if (self.filemtime > 0) and (filemtime <= self.filemtime):
            self.setRunning(threadrunning = False, fromthread = True)
            return True
        # end if

        if (self.filemtime > 0):
            iDelta = filemtime - self.filemtime
        else:
            iDelta = 0
        # end if

        self.filemtime = filemtime

        self.updateDelayMin = self.updateDelayMax = self.updateDelayMean = 0

        arrT = list()

        try:
            iMaxLine = 12
            iMaxParam = 3
            iLine = 0
            iParam = 0

            pathDelay = self.dataDir + "delay.txt"
            if remoteMon:
                # always normalize the server-side filename
                pathDelay = pathDelay.replace("\\", "/")
                strT = subprocess.check_output(['ssh', self.remoteHost, 'cat', pathDelay], stderr=STDDEVNULL)
                arrT = strT.split('\n')
            else:
                fileT = open(pathDelay, "r")
                strT = fileT.read()
                fileT.close()
                arrT = strT.split('\n')
            # end if

            for lineT in arrT:
                if (not lineT):
                    break
                # end if

                lineT = lineT.rstrip("\r\n")
                if lineT.startswith("DelayMin = "):
                    self.updateDelayMin = int(float(lineT[len("DelayMin = "):]))
                    iParam += 1
                # end if
                elif lineT.startswith("DelayMax = "):
                    self.updateDelayMax = int(float(lineT[len("DelayMax = "):]))
                    iParam += 1
                # end if
                elif lineT.startswith("DelayMean = "):
                    self.updateDelayMean = int(float(lineT[len("DelayMean = "):]))
                    iParam += 1
                # end if
                iLine += 1
                if (iLine >= iMaxLine) or (iParam >= iMaxParam):
                    break
                # end if
            # end for

        except Exception as excT:
            pass
        # end try

        iLine = 0

        try:
            del arrT[:]
            arrT = list()
        except:
            pass
        # end try

        # get the file content from remote server or locally.
        # the ssh connexion should use auth keys, not password, for obvious security reasons.

        fileT = None
        try:
            if remoteMon:
                subprocess.check_call(['scp', self.remoteHost + ':' + self.dataFilename, self.dataFilenameLocal], stderr=STDDEVNULL, stdout=STDDEVNULL)
            # end if
        except:
            # check if the data file is locally store
            if not os.path.isfile(self.dataFilenameLocal):
                self.resetData()
                self.setRunning(threadrunning = False, fromthread = True)
                return False
            # end if
            pass
        # end try

        self.resetData()

        bAuto = (self.xIndex == self.yIndex[0])

        paramlistItem = ""

        self.strViewerFileContent = ""

        self.efficiencyMin = 0.0
        self.efficiencyMax = 0.0
        self.efficiencySel = 0.0

        try:
            fileT = open(self.dataFilenameLocal, "r")

            for lineT in fileT:

                self.strViewerFileContent += lineT

                if (self.paramName is None) and lineT.startswith("# Parameter:"):
                    try:
                        self.paramName = lineT[len("# Parameter:"):].lstrip("\t").rstrip("\r\n").replace("\t", self.paramSep)
                        self.paramCount = len(self.paramName.split(self.paramSep)) + 1
                    except:
                        self.paramName = ""
                        self.paramCount = 0
                    # end if
                    iLine += 1
                    continue
                # end if

                if lineT.startswith("#") or ((lineT[0].isdigit() == False) and (lineT[0].isspace() == False)):
                    iLine += 1
                    continue
                # end if

                if bAuto == True:
                    iSep = lineT.count(self.dataSep)
                    if iSep > (self.count - 1):
                        self.xIndex = 0
                        for idy in range(0, self.count):
                            self.yIndex[idy] = iSep - (self.count - 1) + idy
                        # end for
                        bAuto = False
                    else:
                        iLine += 1
                        continue
                    # end if
                # end if

                arrLine = []
                try:
                    arrLine = lineT.split(self.dataSep)
                except:
                    continue
                # end try

                arrlen = len(arrLine)
                if (arrlen < (self.xIndex + 1)) or (arrlen < (self.yIndex[0] + 1)) or (arrlen < (self.yIndex[1] + 1)) or (arrlen < (self.yIndex[2] + 1)):
                    continue
                # end if

                if (self.xIndex >= 0):
                    self.datax = np.append(self.datax, float(arrLine[self.xIndex]))
                else:
                    self.datax = np.append(self.datax, float(self.iPoints))
                # end if

                for idy in range(0, self.count):
                    self.datay[idy] = np.append(self.datay[idy], float(arrLine[self.yIndex[idy]]))
                # end for

                # optimized input parameters
                paramlistItem = self.paramIndexFormat.format(self.iPoints + 1)
                paramlistItem += "   [ " + self.paramName + " ]   =   [ "
                for ll in range(2, 1 + self.paramCount):
                    paramlistItem += '{0}'.format(float(arrLine[ll]))
                    if ll < self.paramCount:
                        paramlistItem += self.paramSep
                    else:
                        paramlistItem += " ]"
                    # end if
                # end for
                self.paramlistThread.append(paramlistItem)

                # optimized output values (FF, Jsc, Voc, Eff)
                try:
                    iopt = self.yIndex[0] - 1
                    if iopt >= 2:
                        optimlistItem = (("$\mathregular{FF\ =\ %6.3f\ \%%}$" % float(arrLine[iopt])) + self.paramSep
                                       + ("$\mathregular{J_{SC}\ =\ %6.3f\ mA/cm^{2}}$" % float(arrLine[iopt+1])) + self.paramSep
                                       + ("$\mathregular{V_{OC}\ =\ %6.3f\ V}$" % float(arrLine[iopt+2])) + self.paramSep
                                       + ("$\mathregular{Eff\ =\ %6.3f\ \%%}$" % float(arrLine[iopt+3])))
                        self.optimlist.append(optimlistItem)
                        self.optimout.append((math.fabs(float(arrLine[iopt-2])), float(arrLine[iopt-1]), float(arrLine[iopt]), float(arrLine[iopt+1]), float(arrLine[iopt+2]), float(arrLine[iopt+3])))
                    # end if
                except:
                    pass

                # report file names (J-V characteristics)
                self.strReportFileName[0].append(self.dataDir + "simuloutput_jvp_" + arrLine[0] + "_" + arrLine[1] + ".log")
                self.strReportFileNameLocal[0].append(self.dataDirLocal + "simuloutput_jvp_" + arrLine[0] + "_" + arrLine[1] + ".log")

                # report file names (External quantum efficiency)
                self.strReportFileName[1].append(self.dataDir + "simuloutput_spectralresponse_eqe_" + arrLine[0] + "_" + arrLine[1] + ".log")
                self.strReportFileNameLocal[1].append(self.dataDirLocal + "simuloutput_spectralresponse_eqe_" + arrLine[0] + "_" + arrLine[1] + ".log")

                self.iPoints += 1
                iLine += 1
            # end for

            fileT.close()

            self.updateCount += 1

        except:
            pass

        try:
            if self.listKeyword2 is None:
                self.listKeyword2 = list()
                for strK in self.paramName.split(self.paramSep):
                    self.listKeyword2.append(strK)
                # end for
            # end if
        except:
            pass

        if self.iPoints >= 1:
            self.efficiencyMin = np.min(self.datay[self.count - 1])
            self.efficiencyMax = np.max(self.datay[self.count - 1])
            self.efficiencySel = self.datay[self.count - 1][self.iPoints - 1]
        # end if

        for rr in range(0, len(self.strReportFileName)):
            if self.strReportFileName[rr] is None:
                continue
            # end if

            iFnameLen = len(self.strReportFileName[rr])
            iFcontentLen = len(self.strReportFileContent[rr])
            if (iFnameLen != self.iPoints) or (iFcontentLen >= iFnameLen):
                self.setRunning(threadrunning = False, fromthread = True)
                return
            # end if

            for ii in range(iFcontentLen, iFnameLen):
                # get the files from the remote server and store them locally.
                # the ssh connexion should use auth keys, not password, for obvious security reasons.
                try:
                    if remoteMon and (not os.path.exists(self.strReportFileNameLocal[rr][ii])):
                        subprocess.check_call(['scp', self.remoteHost + ':' + self.strReportFileName[rr][ii], self.strReportFileNameLocal[rr][ii]], stderr=STDDEVNULL, stdout=STDDEVNULL)
                    # end if
                    fileT = open(self.strReportFileNameLocal[rr][ii], "r")
                    self.strReportFileContent[rr].append(fileT.read())
                    fileT.close()
                except:
                    self.setRunning(threadrunning = False, fromthread = True)
                    return
                # end try

                if (self.isRunning() == False):
                    break
                # end if

            # end for
        # end for

        # At the optimization end, get the zipped files from remote server.
        # the ssh connexion should use auth keys, not password, for obvious security reasons.
        if remoteMon:

            isStopped = False
            stoppedFilename = self.dataDir + "stopped.txt"
            stoppedFilename = stoppedFilename.replace("\\", "/")
            try:
                strT = subprocess.check_output(['ssh', self.remoteHost, "stat", "--printf=%Y", stoppedFilename], stderr=STDDEVNULL)
                updateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(strT)))
                isStopped = True
            except:
                pass
            # end try

            if isStopped:
                try:
                    subprocess.check_call(['scp', self.remoteHost + ':' + self.dataZip, self.dataZipLocal], stderr=STDDEVNULL, stdout=STDDEVNULL)
                    with zipfile.ZipFile(self.dataZipLocal, 'r') as zipT:
                        zipT.extractall(self.dataDirLocal)
                    # end if
                except:
                    pass
                # end try
            # end if
        # end if

        self.setRunning(threadrunning = False, fromthread = True)

    # end updateDataThread

    def updateTitleEfficiency(self):
        try:
            strTX = ""
            if ((self.iPoints >= 1) and (self.efficiencyMin <= self.efficiencyMax)
                and (self.efficiencyMin <= self.efficiencyMax)):
                strTX = ("Efficiency: min = " + ("%06.3f" % self.efficiencyMin)
                    + " ; max = " + ("%06.3f" % self.efficiencyMax)
                    + " ; selected = " + ("%06.3f" % self.efficiencySel)
                    + ">")
            # end if
            self.plot[self.count - 1].set_title(strTX, fontsize=self.fontsize, color=self.linecolor[self.count - 1])
        except:
            pass
        # end try
    # end updateTitleEfficiency

    def updateSel(self, index=None):

        if self.isRunning():
            return
        # end if

        self.dataxSel = np.delete(self.dataxSel, np.s_[:])
        for idy in range(0, self.count):
            self.dataySel[idy] = np.delete(self.dataySel[idy], np.s_[:])
        # end for

        if (self.iPoints < 1):
            for idy in range(0, self.count):
                if self.scatter[idy] is not None:
                    self.scatter[idy].set_xdata(self.dataxSel)
                    self.scatter[idy].set_ydata(self.dataySel[idy])
                    self.plot[idy].relim()
                    self.plot[idy].autoscale()
                # end if
            # end for
            self.updateTitleEfficiency()
            self.canvas.draw()
            return
        # end if

        if (index is None) or (index < 0) or (index >= self.iPoints):
            index = self.iPoints - 1
        # end if

        self.dataxSel = np.append(self.dataxSel, self.datax[index])
        for idy in range(0, self.count):
            self.dataySel[idy] = np.append(self.dataySel[idy], self.datay[idy][index])
        # end if
        self.efficiencySel = self.datay[self.count - 1][index]
        self.updateTitleEfficiency()

        for idy in range(0, self.count):
            if self.scatter[idy] is None:
                self.scatter[idy], = self.plot[idy].plot(self.dataxSel, self.dataySel[idy], self.markersm[idy], zorder=4)
                self.scatter[idy].set_color(self.scattercolor[idy])
                self.scatter[idy].set_markerfacecolor(self.scattercolor[idy])
                self.scatter[idy].set_markeredgecolor(self.scattercolorborder[idy])
                self.scatter[idy].set_markersize(self.scattermarkersize[idy])
            # end if
            self.scatter[idy].set_xdata(self.dataxSel)
            self.scatter[idy].set_ydata(self.dataySel[idy])
            self.plot[idy].relim()
            self.plot[idy].autoscale()
        # end for
        self.canvas.draw()
    # end updateSel

    def updateData(self, force=False):

        if self.isRunning():
            return
        # end if

        dataRead = False

        if self.updateProgress.stopping <= self.paramCount:
            dataRead = True

            self.paramlist = list(self.paramlistThread)
            self.paramlistBox['values'] = self.paramlist
            try:
                self.paramlistBox.set(self.paramlist[self.iPoints - 1])
            except:
                pass
        # end if

        for idy in range(0, self.count):
            if self.line[idy] is None:
                self.line[idy], = self.plot[idy].plot(self.datax, self.datay[idy], self.linestyle[idy], linewidth=self.linesize[idy], zorder=4)
                self.line[idy].set_color(self.linecolor[idy])
                self.line[idy].set_markerfacecolor(self.linecolor[idy])
                self.line[idy].set_markeredgecolor(self.linecolor[idy])
            # end if
            self.line[idy].set_marker(self.markerhg[idy] if (len(self.datax) > 20) else self.markersm[idy])
            self.line[idy].set_markersize(self.markersizehg[idy] if (len(self.datax) > 20) else self.markersizesm[idy])
            self.line[idy].set_xdata(self.datax)
            self.line[idy].set_ydata(self.datay[idy])
            self.plot[idy].relim()
            self.plot[idy].autoscale()
        # end for

        isStopped = self.updateTitle(dataUpdated=dataRead)

        # self.canvas.draw() called in updateSel
        self.updateSel()

        if dataRead:
            if self.updateDelayAuto:
                if (self.updateDelayMin >= self.delayMin) and (self.updateDelayMin <= self.delayMax):
                    self.updateDelayEdit.delete(0, Tk.END)
                    self.updateDelayEdit.insert(0, str(self.updateDelayMin))
                    self.updateDelay = self.updateDelayMin
                # end if
            # end if
        # end if

        if (self.viewer is not None):
            self.viewer.frame.setText(self.strViewerFileContent, self.listKeyword, self.listKeyword2)
        # end if

        self.updateReport()

        if (isStopped == False):
            self.updateProgressVar.set(0)
            self.updateProgress.start(1000)

            # delay in milliseconds
            self.root.after(1000 * (self.updateDelay + 2), self.onUpdateData)

        else:
            self.updateProgressVar.set(0)
            self.updateProgress.stop()
        # end if

    # end updateData

    def onUpdateData(self, force=False):

        if self.isRunning():
            return
        # end if

        nowT = time.time()

        if force:
            self.updateProgress.waiting = 0
            self.updateProgress.stopping = 0
            self.updateProgress.stopped = 0
            self.killproc = 0
            self.startTime = int(nowT)
            self.filemtime = 0
            self.updateTime = 0
            self.updateCount = 0
            self.updateDelayMin = 0
            self.updateDelayMax = 0
            try:
                self.paramlistBox.selection_clear()
                self.paramlistBox.set("")
            except:
                pass
        # end if

        self.updateProgressVar.set(0)
        self.updateProgress.stop()

        self.updateTime = int(nowT)

        self.updateParam()

        strTitle = "SLALOM - updating..."
        self.plot[0].set_title(strTitle, fontsize=self.fontsize)

        self.actionbutton = self.btnStart
        self.setRunning(threadrunning = True, fromthread = False)
        self.thread = OptimizerThread(id=1, func=self.updateDataThread)
        self.thread.start()
        self.threadfinish = self.updateData
        self.onThreadMonitor()
        # end if

    # end onUpdateData

    def updateTitle(self, dataUpdated=False):

        strTitle = "SLALOM"

        remoteMon = self.remoteHostEnabled and (self.remoteHost is not None) and ("@" in self.remoteHost)

        strTitleM = strTitle + " - "
        if self.startTime > 0:
            strTitleM += "started @ " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(self.startTime)))
        # end if

        if self.dataFilename is None:
            self.plot[0].set_title(strTitle, fontsize=self.fontsize)
            self.root.wm_title(strTitleM)
            return
        # end if

        try:
            iii = self.dataFilename.find("/output/")
            if (iii == -1):
                iii = self.dataFilename.find("\\output\\")
            # end if
            if (iii != -1):
                strTitleM += " - " + self.dataFilename[iii+8:]
            # end if
        except:
            pass

        self.root.wm_title(strTitleM)

        isStopped = False

        bStopped = self.isStopped()
        if bStopped:
            strTitle += " - stopped @ "
            strTitle += self.updateProgress.stoppedtime if (self.updateProgress.stoppedtime is not None) else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            isStopped = True
        else:
            bStopping = self.isStopping()
            if bStopping:
                self.updateProgress.stopping += 1
                strTitle += " - being stopped since "
                strTitle += self.updateProgress.stoppingtime if (self.updateProgress.stoppingtime is not None) else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                isStopped = (self.updateProgress.stopping > self.paramCount)
            # end if
        # end if

        if (isStopped == False) and (bStopping == False):
            updateTime = None
            errMessage = None
            try:
                if remoteMon:
                    STDDEVNULL = open(os.devnull, 'w')
                    sshT = subprocess.Popen(['ssh', self.remoteHost, "stat", "--printf=%Y", self.dataFilename], stderr=STDDEVNULL, stdout=subprocess.PIPE)
                    fileT = sshT.stdout
                    updateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(fileT.readline())))
                    # end for
                else:
                    updateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(self.dataFilename)))
                # end if
                strTitle += " - updated @ "
                strTitle += updateTime if (updateTime is not None) else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception as excT:
                strTitle += " - file not found"
                self.updateProgress.waiting += 1
                isStopped = (self.updateProgress.waiting >= 3)
                pass
            # end try
        # end if

        self.plot[0].set_title(strTitle, fontsize=self.fontsize)

        try:
            strLabelX = ""
            if ((self.updateCount >= 1) and (self.updateDelayMin >= self.delayMin) and (self.updateDelayMin <= self.delayMax)
                    and (self.updateDelayMax >= self.updateDelayMin)):
                strLabelX = ("Delay: min = " + slalomCore.printTime(float(self.updateDelayMin), short=True)
                           + " ; max = " + slalomCore.printTime(float(self.updateDelayMax), short=True)
                           + " ; mean = " + slalomCore.printTime(float(self.updateDelayMean), short=True))
            # end if
            self.plot[self.count - 1].set_xlabel(strLabelX, fontsize=self.fontsize)
        except:
            pass
        # end try

        return isStopped

    # end updateTitle

    def onAbout(self):
        tkMessageBox.showinfo("SLALOM",
                             ("SLALOM - Open-Source Solar Cell Multivariate Optimizer\n" +
                              "Copyright(C) 2012-2018 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2).\n" +
                              "All rights reserved.\n" +
                              "(1) Université de Lorraine, LMOPS, Metz, F-57070, France\n" +
                              "(2) LMOPS, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France\n" +
                              "(*) sidi.hamady@univ-lorraine.fr\n" +
                              "Version: 1.0 Build: 1711\n" +
                              "The user manual is in the Guide directory\n" +
                              "See Copyright Notice in COPYRIGHT"),
                              parent=self.root)
    # end onAbout

    def onClose(self):
        if not tkMessageBox.askyesno("SLALOM", "Close Monitor?", default=tkMessageBox.NO, parent=self.root):
            return
        # end if

        # save the last used data filename and ssh host
        try:
            self.updateParam()
            if self.dataFilename:
                fileT = open("Settings/slalomMonitor.params", "w")
                fileT.write("dataFilename = " + self.dataFilename)
                if (self.remoteHost is not None) and ("@" in self.remoteHost):
                    fileT.write("\nremoteHost = " + self.remoteHost)
                    fileT.write("\nremoteHostEnabled = 1" if self.remoteHostEnabled else "\nremoteHostEnabled = 0")
                # end if
                if self.updateDelay and (self.updateDelay >= self.delayMin) and (self.updateDelay <= self.delayMax):
                    fileT.write("\nupdateDelay = " + str(self.updateDelay))
                    fileT.write("\nupdateDelayAuto = 1" if self.updateDelayAuto else "\nupdateDelayAuto = 0")
                # end if
                fileT.close()
            # end if
        except:
            pass

        try:
            if self.viewer is not None:
                self.viewer.destroy()
                self.viewer = None
            # end if
            for report in self.report:
                if report is not None:
                    report.destroy()
                    report = None
                # end if
            # end for
            self.root.quit()
            self.root.destroy()
        except:
            pass
        # end try
    # end onClose

# end slalomWindow class
