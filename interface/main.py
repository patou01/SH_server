# # This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
import sys

import os
import csv
import datetime

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QComboBox

from PyQt5.QtCore import QDateTime

from mainwindow import Ui_MainWindow


from numpy import arange, sin, pi
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator()
yearsFmt = mdates.DateFormatter('%Y')
daysFmt = mdates.DateFormatter('%d')

TIME_INDEX = 0
TEMP_DHT_INDEX = 2
HUM_DHT_INDEX = 3
CO2_INDEX = 4
TVOC_INDEX = 5
TEMP_HDC_INDEX = 6
HUM_HDC_INDEX = 7
LUX_INDEX = 8
REPLOT_DELTA_TIME = 60 # minutes



class default_plot(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=4, height=3, dpi=100):

        self.fig = Figure(figsize=(parent.geometry().width()/dpi, parent.geometry().height()/dpi), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.axes = self.fig.add_subplot(111)
        self.title = ''
        self.reset_plot()
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.axes.xaxis.set_major_locator(days)
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%h'))


     #   print("done init")

    def reset_plot(self):
        self.axes.cla()
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.setTitle(self.title)
    #    self.axes.plot(t, s)
        self.draw()

    def update_figure(self, x, y):
     #   self.axes.cla()
        self.axes.locator_params(axis='y', nbins=6)
        self.axes.locator_params(axis='x', nbins=6)
        self.axes.plot(x, y, 'r')
        self.axes.format_xdata = mdates.DateFormatter('%h')
        self.axes.fmt_xdata = mdates.DateFormatter('%h')
        self.axes.set_xlim(x[0], x[-1])
        self.axes.locator_params(axis='y', nbins=6)
        self.axes.locator_params(axis='x', nbins=6)

        self.fig.autofmt_xdate()
        self.setTitle(self.title)
        self.draw()

    def setTitle(self, title):
        self.title = title
        self.axes.set_title(self.title)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
    #    super(MainWindow, self).__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.LogButton.clicked.connect(self.logButtonPress)
        self.ui.logComboBox.activated.connect(self.logComboChanged)
        self.clear_plot_data()

        self.ui.startDateSlider.setMinimum(1)
        self.ui.startDateSlider.setMaximum(1000)
        self.ui.endDateSlider.setMinimum(1)
        self.ui.endDateSlider.setMaximum(1000)
        self.ui.endDateSlider.setValue(1000);
        
        self.ui.startDateSlider.valueChanged.connect(self.startDateChanged)
        self.ui.endDateSlider.valueChanged.connect(self.endDateChanged)
        

        self.deltaTime = REPLOT_DELTA_TIME*60

        self.startDate = 0
        self.startIndex = 0
        self.endDate = 0
        self.endIndex = 0

        self.startSliderValue = 1
        self.endSliderValue = 1000
        

    def logComboChanged(self):
        self.logFile = self.logDirectory + "\\" + self.ui.logComboBox.currentText() + ".csv"
        self.load_file(self.logFile)

    def logButtonPress(self):
        # let user look up a file, show only the csv files.
        filter = "CSV files (*.csv)"
        t, _ = QFileDialog.getOpenFileName(self, "Select File", "", filter)
        self.logFile = str(t)
 

        self.logDirectory = os.path.dirname(os.path.abspath(self.logFile))
        fileList = []
        for file in os.listdir(self.logDirectory):
           if file.endswith(".csv"):
              fileList.append(file)

        names = []
        for name in fileList:
            names.append(name[0:-4])


        self.ui.logComboBox.clear()
        self.ui.logComboBox.addItems(names)

        #need to make the selected name match the clicked file
        splitFile = self.logFile.split("/")
        activeFile = splitFile[len(splitFile)-1]
        activeFile = activeFile[0:-4]

        # this is kind of a hack, I'm not sure this actually put the focus on it, but since the file is selected already it's ok.
        self.ui.logComboBox.setCurrentText(activeFile)

     #   print(activeFile)
        self.load_file(self.logFile)

    def clear_plot_data(self):
        self.time = []
        self.T_dht = []
        self.H_dht = []
        self.co2 = []
        self.tvoc = []
        self.T_hdc = []
        self.H_hdc = []
        self.lux = []

    def clear_plots(self):
        self.ui.plot1.reset_plot()
        self.ui.plot2.reset_plot()
        self.ui.plot3.reset_plot()
        self.ui.plot4.reset_plot()

    def load_file(self, File):
        self.clear_plot_data()
        self.clear_plots()
        with open(File) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0

            for row in csv_reader:
                if (row != []):
                    if(float(row[TEMP_DHT_INDEX]) < 120): # kind of a hack filter, the temperature data reads 200 if the sensor fails, and skipping a line every now and then is no big deal.
                        self.time.append(mdates.epoch2num(float(row[TIME_INDEX])))
                        self.T_dht.append(float(row[TEMP_DHT_INDEX]))
                        self.H_dht.append(float(row[HUM_DHT_INDEX]))
                        self.co2.append(float(row[CO2_INDEX]))
                        self.tvoc.append(float(row[TVOC_INDEX]))
                        self.T_hdc.append(float(row[TEMP_HDC_INDEX]))
                        self.H_hdc.append(float(row[HUM_HDC_INDEX]))
                        self.lux.append(float(row[LUX_INDEX]))



            self.time = mdates.num2date(self.time)
            self.T_dht = np.array(self.T_dht)
            self.co2 = np.array(self.co2)
            self.tvoc = np.array(self.tvoc)
            self.lux = np.array(self.lux)


            if(len(self.time) > 1):
                self.update_plots(0, len(self.time)-1)

                startTime = int(round(mdates.num2epoch(mdates.date2num(self.time[0]))))
                endTime = int(round(mdates.num2epoch(mdates.date2num(self.time[len(self.time)-1]))))

                minStartDate = QDateTime.fromTime_t(startTime)
                maxStartDate = QDateTime.fromTime_t(endTime)

                self.startDate = self.time[0]
                self.startIndex = 0
                self.endDate = self.time[len(self.time)-1]
                self.endIndex = len(self.time)-1


                print("read csv, number of lines: " + str(len(self.time)) + " start date " + minStartDate.toString() + " end date " + maxStartDate.toString())



    def update_plots(self, begin, end):
        if(begin >= 0 and end <= len(self.time) and begin < end):
            self.ui.plot1.update_figure(self.time[begin:end], self.T_dht[begin:end])
            self.ui.plot2.update_figure(self.time[begin:end], self.co2[begin:end])
            self.ui.plot3.update_figure(self.time[begin:end], self.tvoc[begin:end])
            self.ui.plot4.update_figure(self.time[begin:end], self.lux[begin:end])

    def startDateChanged(self):

        # only change if there's a big enough change
        if(abs(self.startSliderValue - self.ui.startDateSlider.value()) > 10):
            self.startSliderValue = self.ui.startDateSlider.value()
     
        # set new max value
        if(self.ui.endDateSlider.value() - self.ui.startDateSlider.value() < 10):
            self.ui.startDateSlider.setValue(self.ui.endDateSlider.value() - 10)

        # update the plots
        self.startEndDateChanged()
        
    def endDateChanged(self):

        # only change if htere's a big enough change
        if(abs(self.endSliderValue - self.ui.endDateSlider.value()) > 10):
            self.endSliderValue = self.ui.endDateSlider.value()
        
       # set new min value
        if(self.ui.endDateSlider.value() - self.ui.startDateSlider.value() < 10):
           self.ui.endDateSlider.setValue(self.ui.startDateSlider.value() + 10)

        # update plots
        self.startEndDateChanged()


    def startEndDateChanged(self):
        n = len(self.time)
        if(n > 0):
            self.startIndex =  int(self.startSliderValue * n / 1000)
            self.endIndex = int(self.endSliderValue * n/1000)
       #     print("startIndex " + str(self.startIndex) + " endIndex " +str(self.endIndex))
            self.update_plots(self.startIndex, self.endIndex)
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.ui.plot1 = default_plot(w.ui.plot1)
    w.ui.plot2 = default_plot(w.ui.plot2)
    w.ui.plot3 = default_plot(w.ui.plot3)
    w.ui.plot4 = default_plot(w.ui.plot4)
    w.ui.plot1.setTitle("temp")
    w.ui.plot2.setTitle("co2")
    w.ui.plot3.setTitle("tvoc")
    w.ui.plot4.setTitle("lux")



    w.show()
    sys.exit(app.exec_())

