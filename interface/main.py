# # This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
import sys

import os
import csv
import datetime

from PyQt5 import  QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QComboBox

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
TEMP_DHT_INDEX = 1
HUM_DHT_INDEX = 2
CO2_INDEX = 3
TVOC_INDEX = 4
TEMP_HDC_INDEX = 5
HUM_HDC_INDEX = 6
LUX_INDEX = 7




class default_plot(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=4, height=3, dpi=100):

        self.fig = Figure(figsize=(parent.geometry().width()/dpi, parent.geometry().height()/dpi), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.axes = self.fig.add_subplot(111)
        self.compute_initial_figure()
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.axes.xaxis.set_major_locator(days)
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%h'))


        print("done init")

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)

    def update_figure(self, x,y):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)

        t = self.axes.get_title()
        self.axes.cla()
        self.axes.locator_params(axis='y', nbins=6)
        self.axes.locator_params(axis='x', nbins=6)
        self.axes.plot(x, y, 'r')
        self.axes.format_xdata = mdates.DateFormatter('%h')
        self.axes.fmt_xdata = mdates.DateFormatter('%h')
        self.axes.set_xlim(x[0], x[-1])
        self.axes.locator_params(axis='y', nbins=6)
        self.axes.locator_params(axis='x', nbins=6)

        self.fig.autofmt_xdate()
        self.axes.set_title(t)
        self.draw()

    def setTitle(self, title):
        self.axes.set_title(title)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
    #    super(MainWindow, self).__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.LogButton.clicked.connect(self.logButtonPress)

        self.clear_plot_data()



    #def resizeEvent(self, event):

    def logButtonPress(self):
        # let user look up a file, show only the csv files.
        filter = "CSV files (*.csv)"
        t, _ = QFileDialog.getOpenFileName(self, "Select File", "", filter)
        logFile = str(t)
        #print("log file:" + t)

        logDirectory = os.path.dirname(os.path.abspath(logFile))
        #print(logDirectory)
        fileList = []
        for file in os.listdir(logDirectory):
           if file.endswith(".csv"):
              fileList.append(file)
        #      print(os.path.join(logDirectory, file))

        #print(fileList)

        names = []
        for name in fileList:
            names.append(name[0:-4])
        #print(names)

        self.ui.logComboBox.clear()
        self.ui.logComboBox.addItems(names)

        #need to make the selected name match the clicked file
        splitFile = logFile.split("/")
        activeFile = splitFile[len(splitFile)-1]
        activeFile = activeFile[0:-4]

        # this is kind of a hack, I'm not sure this actually put the focus on it, but since the file is selected already it's ok.
        self.ui.logComboBox.setCurrentText(activeFile)

        print(activeFile)
        self.load_file(logFile)

    def clear_plot_data(self):
        self.time = []
        self.T_dht = []
        self.H_dht = []
        self.co2 = []
        self.tvoc = []
        self.T_hdc = []
        self.H_hdc = []
        self.lux = []

    def load_file(self, File):
        self.clear_plot_data()
        with open(File) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            print("started reading csv")
            for row in csv_reader:
                if (row != []):
                    if(float(row[TEMP_DHT_INDEX]) < 120):
                    #    print(row)
                 #   print(type(row[TIME_INDEX]))
                        self.time.append(mdates.epoch2num(float(row[TIME_INDEX])))
                        self.T_dht.append(float(row[TEMP_DHT_INDEX]))
                        self.H_dht.append(float(row[HUM_DHT_INDEX]))
                        self.co2.append(float(row[CO2_INDEX]))
                        self.tvoc.append(float(row[TVOC_INDEX]))
                        self.T_hdc.append(float(row[TEMP_HDC_INDEX]))
                        self.H_hdc.append(float(row[HUM_HDC_INDEX]))
                        self.lux.append(float(row[LUX_INDEX]))

            print("read csv")

            self.time = mdates.num2date(self.time)
            self.T_dht = np.array(self.T_dht)
            self.co2 = np.array(self.co2)
            self.tvoc = np.array(self.tvoc)
            self.lux = np.array(self.lux)
            print(len(self.time))

            self.ui.plot1.update_figure(self.time, self.T_dht)
            self.ui.plot2.update_figure(self.time, self.co2)
            self.ui.plot3.update_figure(self.time, self.tvoc)
            self.ui.plot4.update_figure(self.time, self.lux)




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

