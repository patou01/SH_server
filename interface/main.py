# # This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
import sys

import os
import csv
import datetime


from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QComboBox, QListWidget, QListWidgetItem

from PyQt5.QtCore import QDateTime

from mainwindow import Ui_MainWindow

from timeit import default_timer as timer

from numpy import arange, sin, pi
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator()
yearsFmt = mdates.DateFormatter('%Y')
daysFmt = mdates.DateFormatter('%d')


REPLOT_THRESHOLD = 50

TIME_INDEX = 0


class default_plot(FigureCanvas):
    #"""Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=8, height=7, dpi=100):

        self.fig = Figure(figsize=(parent.geometry().width()/dpi, parent.geometry().height()/dpi), dpi=dpi)
        self.ax = []
        FigureCanvas.__init__(self, self.fig)
        self.ax.append( self.fig.add_subplot(111))
     #   self.axes = self.fig.add_subplot(111)
 #       self.title = ''
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

  #      self.axes.xaxis.set_major_locator(days)
  #      self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%h'))

        self.colors = ['b','g','r', 'c', 'm', 'y', 'k']
        
        self.fig.clf()
     #   print("done init")

    def reset_plot(self):
        for a in self.ax:
            a.cla()

       # for i in range(1,len(self.ax)-1):
      #      self.ax[-i]


    def update_figure(self, x, y, headers):

  #     self.reset_plot()
        print(y[:,1:3])

        plt.figure()
        print("alive")
        plt.plot(x, y[1,:], self.colors[0])
       # self.ax[0].plot(x, y[1,:], self.colors[0])
  #      self.ax[0].format_xdata = mdates.DateFormatter('%h')
   #     self.ax[0].fmt_xdata = mdates.DateFormatter('%h')
    #    self.ax[0].set_xlim(x[0], x[-1])
     #   self.ax[0].locator_params(axis='y', nbins=3)
      #  self.ax[0].locator_params(axis='x', nbins=6)
       # self.ax[0].set_xlabel("time")

        print("done")
        
 #       for i in range(3, len(headers)):
   #         if(headers[i][1] == True):
      #          print("i " + str(i) + " len self.ax " + str(len(self.ax)) + " len data " + str(len(y)) + " len header " + str(len(headers)))
  #              self.ax.append( self.ax[0].twinx())

   #             a = self.ax[len(self.ax)-1]
    #            a.plot(x, y[i-2, :], self.colors[len(self.ax)-1])


#        self.ax3.spines["right"].set_position(("axes", 1.2))
    
 #       self.ax3.spines["right"].set_visible(True)

#        self.fig.autofmt_xdate()
    #    self.fig.tight_layout()
        
      #  self.setTitle(self.title)
#        self.draw()

    def setTitle(self, title):
        self.title = title
       # self.axes.set_title(self.title)


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

        self.load_file(self.logFile)



    def clear_plot_data(self):
        self.time = []
        self.dataList = []
        self.dataArr = []
        self.headerPlot = []



    def clear_plots(self):
        self.ui.plot1.reset_plot()



    def selection_changed(self):
        # get all true/false values for plotting
        dataList = self.ui.dataListWidget
        for i in range(dataList.count()):
            self.headerPlot[i] = [dataList.item(i).text(), bool(dataList.item(i).checkState())]

        #replot
        self.update_plots()




    def load_file(self, File):
        self.clear_plot_data()
        self.ui.dataListWidget.clear()

        with open(File) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            headers = next(csv_reader) # first line is the headers

            #ignore the first 2 headers because they're both time due to a screw up and we use time as x axis at the moment
            for i in range(2, len(headers)):
                self.headerPlot.append([headers[i], False])
                item = QListWidgetItem(headers[i])
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.ui.dataListWidget.addItem(item)

            self.ui.dataListWidget.itemChanged.connect(self.selection_changed)

            for i in range(0, len(self.headerPlot)):
                self.dataList.append([])

            for row in csv_reader:
                if (row != []):
                    self.time.append(mdates.epoch2num(float(row[TIME_INDEX])))
                
                    for i in range(2,len(row)):
                        self.dataList[i-2].append(float(row[i]))


            #convert to more usable formats
            self.time = mdates.num2date(self.time)
            self.dataArr = np.array(self.dataList)

            # set the scope to plot and plot it
            if(len(self.time) > 1):
                startTime = int(round(mdates.num2epoch(mdates.date2num(self.time[0]))))
                endTime = int(round(mdates.num2epoch(mdates.date2num(self.time[len(self.time)-1]))))

                minStartDate = QDateTime.fromTime_t(startTime)
                maxStartDate = QDateTime.fromTime_t(endTime)

                self.startDate = self.time[0]
                self.startIndex = 0
                self.endDate = self.time[len(self.time)-1]
                self.endIndex = len(self.time)-1
                
                print("read csv, number of lines: " + str(len(self.time)) + " start date " + minStartDate.toString() + " end date " + maxStartDate.toString() + " number of datapoints " + str(len(self.dataArr[3])))

                self.update_plots()

    def update_plots(self):
        if(self.startIndex >= 0 and self.endIndex <= len(self.time) and self.startIndex < self.endIndex):
            self.clear_plots()
            self.ui.plot1.update_figure(self.time[self.startIndex:self.endIndex], self.dataArr[:,self.startIndex:self.endIndex], self.headerPlot)

    def startDateChanged(self):
        # only change if there's a big enough change
        if(abs(self.startSliderValue - self.ui.startDateSlider.value()) > REPLOT_THRESHOLD):
            self.startSliderValue = self.ui.startDateSlider.value()
     
        # set new max value
        if(self.ui.endDateSlider.value() - self.ui.startDateSlider.value() < 10):
            self.ui.startDateSlider.setValue(self.ui.endDateSlider.value() - 10)

        # call common callback
        self.startEndDateChanged()

        
    def endDateChanged(self):
        # only change if htere's a big enough change
        if(abs(self.endSliderValue - self.ui.endDateSlider.value()) > REPLOT_THRESHOLD):
            self.endSliderValue = self.ui.endDateSlider.value()
        
       # set new min value
        if(self.ui.endDateSlider.value() - self.ui.startDateSlider.value() < 10):
           self.ui.endDateSlider.setValue(self.ui.startDateSlider.value() + 10)

        # call common callback
        self.startEndDateChanged()


    #checks if we have a log file loaded, then computes start/end indices and updates plots.
    def startEndDateChanged(self):
        n = len(self.time) 
        if(n > 0):
            self.startIndex =  int(self.startSliderValue * n / 1000)
            self.endIndex = int(self.endSliderValue * n/1000)
            self.update_plots()   



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.ui.plot1 = default_plot(w.ui.plot1)
    w.ui.plot1.setTitle("temp")




    w.show()
    sys.exit(app.exec_())

