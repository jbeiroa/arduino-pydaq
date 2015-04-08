# -*- coding: utf-8 -*-

"""

Data acquisition script with matplotlib and wxpython.

@author: Juan Beiroa.

Every one second, the app tells an Arduino (arduino.py) to make a 
measurement and send it to the computer for plotting and logging. 
Deformation and temperature data are saved to a txt file in the same
folder of this python script.

The program plots temperature vs. deformation, time vs. deformation 
and time vs. temperature. Data is stored in a two column txt file
(delimited by tabs).

"""

import os
import numpy as np
import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
#from arduino import Arduino

###############################################################################

class Plots_Panel(wx.Panel):
    """

    Panel to hold matplotlib figure. There are three plots inside a grid, big one
    for temperature vs. deformation and smaller ones for time vs. deformation and
    time vs. temperature.

    """

    #--------------------------------------------------------------------------#
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        self.init_plots() #make figure
        self.PlotsCanvas = FigCanvas(self, wx.ID_ANY, self.fig)

        self.toolbar = NavigationToolbar(self.PlotsCanvas)
        self.toolbar.Realize()
        
        #correct toolbar size
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.PlotsCanvas.GetSizeTuple()
        
        

        # Sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.PlotsCanvas, 1, wx.EXPAND | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.BOTTOM | wx.GROW)
        self.toolbar.SetSize(wx.Size(fw, th))
        self.toolbar.update()
        self.SetSizerAndFit(sizer)

    #--------------------------------------------------------------------------#
    def init_plots(self):

        self.fig = Figure((-1,7.5))
        self.fig.subplots_adjust(left=0.05, wspace=.3, hspace=3) #sub plot spacing

        gs = matplotlib.gridspec.GridSpec(8,3)
        self.ax1 = self.fig.add_subplot(gs[:,0:2])
        self.ax2 = self.fig.add_subplot(gs[0:4,2])
        self.ax3 = self.fig.add_subplot(gs[4:8,2])

        self.ax1.set_xlabel(u'Temperatura ($^\circ$C)')
        self.ax1.set_ylabel(u'Deformación (mm)')
        self.ax2.set_xlabel(u'Tiempo (s)')
        self.ax2.set_ylabel(u'Deformación (mm)')
        self.ax3.set_xlabel(u'Tiempo (s)')
        self.ax3.set_ylabel(u'Temperatura ($^\circ$C)')

###############################################################################

class Action_Panel(wx.Panel):
    """

    Panel with start button, output file control and text log to see measurement
    values.

    """

    #--------------------------------------------------------------------------#
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        #start toggle button to start/pause the program and textctrl to
        #entry output file name
        self.toggle = wx.ToggleButton(self, label="Start")
        self.txt_output_file = wx.TextCtrl(self, size=(440,30))

        horizontal = wx.BoxSizer(wx.HORIZONTAL)
        horizontal.Add(self.toggle, 1, wx.EXPAND | wx.GROW)
        horizontal.Add(self.txt_output_file, 1, wx.EXPAND | wx.GROW)

        #text box for event logging
        self.log_text = wx.TextCtrl(
                                  self, -1, size=(440,30),
                                  style=wx.TE_MULTILINE)
        self.log_text.SetFont(
                           wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))

        horizontal.Add(self.log_text, 1, wx.EXPAND | wx.GROW)

        self.SetSizer(horizontal)

###############################################################################

class GuiFrame(wx.Frame):
    """
    
    Main frame of the application. Sets up a timer to perform measurements
    and plot them every one second and starts a stopwatch to plot time vs.
    deformation and temperature.
    TODO: record time in output file.
    
    """

    title = 'DAQ'

    #--------------------------------------------------------------------------#
    def __init__(self):

        wx.Frame.__init__(self, None, title=self.title)

        # Try Arduino
        # try:
            # self.arduino = Arduino(arduino_port, 115200)
        # except:
            # print 'unable to connect to arduino'

        self.Maximize()

        self.plots_panel = Plots_Panel(self)
        self.action_panel = Action_Panel(self)

        #timer for the main loop and watch to record time
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.sw = wx.StopWatch()
        self.sw.Pause()
        
        #start/stop button from action_panel
        self.action_panel.toggle.Bind(wx.EVT_TOGGLEBUTTON, self.onToggle)

        #Sizers
        panels = wx.BoxSizer(wx.VERTICAL)

        panels.Add(self.action_panel, 1, wx.GROW)
        panels.Add(self.plots_panel, 1, wx.GROW)

        self.SetSizerAndFit(panels)
        self.Layout()

        #add status bar?

    #--------------------------------------------------------------------------#
    def onToggle(self, event):
        """

        Start / Stop the measurement on button toggle.

        """

        value = self.action_panel.toggle.GetValue()
        if value:
            if not self.check_file():
                self.action_panel.toggle.SetLabel("Start")
            else:
                self.action_panel.toggle.SetLabel("Pause")
                self.sw.Resume()
                self.timer.Start(1000)
        else:
            self.sw.Pause()
            self.timer.Stop()
            self.action_panel.toggle.SetLabel("Start")
            try:
                self.txt.close()
            except AttributeError:
                pass

    #--------------------------------------------------------------------------#
    def poll(self):
        """

        Retrieve data from Arduino and perform temperature and deformation 
        correction from calibration curves.

        """

        #self.data = self.arduino.poll()

        # Add volt to mm and raw to temp conversions

        self.data = (np.random.rand(2)*1000).tolist()
        self.action_panel.log_text.AppendText(str(self.data[0])+"\t"+
                                              str(self.data[1])+"\n")

    #--------------------------------------------------------------------------#
    def check_file(self):
        """

        Checks for output file name on Start button toggle. If no file 
        with the chosen name exists, this function creates it. If no file
        name is declared, prompts to write one. If a file with the chosen
        name already exists, asks to overwrite, append to already existing
        or enter a new name.

        """

        # check for output file
        if self.action_panel.txt_output_file.IsEmpty():
            msg = wx.MessageDialog(self, 'Especifique nombre de archivo.',
                                      'Error', wx.OK | wx.ICON_ERROR)
            msg.ShowModal() == wx.ID_YES
            msg.Destroy()

            return False

        else:
            self.output_file = self.action_panel.txt_output_file.GetRange(0,-1)

            if os.path.isfile(self.output_file):
                msg = wx.MessageDialog(self, 
                                        'Ya existe el archivo - Sobreescribir?\n'
                                        'Cancelar para anexar al archivo existente.',
                                        'Si o No', 
                                        wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                result = msg.ShowModal() == wx.ID_CANCEL

                #overwrite
                if result == True:
                    return True
                else:
                    self.action_panel.txt_output_file.SetFocus()
                    return False

            #make a file if it does not exist
            else:
                open(self.output_file, 'w').close()

            return True

    #--------------------------------------------------------------------------#
    def save_meas(self):
        """
        
        Save measurement to output file as a two column delimited by tabs.
        TODO: add time as another column.

        """

        self.txt = open(self.output_file, 'a')
        self.txt.write(str(self.data[0]) + '\t' + str(self.data[1]) + '\n')
        self.txt.close()

    #--------------------------------------------------------------------------#
    def draw(self):
        """

        Adds new data to plots.
        BUG: Not able to join the dots with lines.

        """

        self.plots_panel.ax1.plot(self.data[0], self.data[1], 'bo-')
        self.plots_panel.ax2.plot(self.sw.Time() * 0.001, self.data[0], 'ro-')
        self.plots_panel.ax3.plot(self.sw.Time() * 0.001, self.data[1], 'ko-')

        self.plots_panel.PlotsCanvas.draw()

    #--------------------------------------------------------------------------#
    def on_timer(self,event):
        """

        Make measurements, plot and saving on timer.

        """

        self.poll()
        self.draw()
        self.save_meas()

###############################################################################

def main():

    app = wx.App()
    app.frame = GuiFrame()
    app.frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
