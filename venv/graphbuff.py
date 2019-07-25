import sys
import time
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
import serial
import threading

app = QtWidgets.QApplication(sys.argv)

win = pg.GraphicsWindow()

main_plot = win.addPlot()
main_plot_t_start = 0
main_plot_t_size = 2047
main_plot_t_end = main_plot_t_size
main_plot.setYRange(0,4095)
main_plot.setLabel('left', 'ADC Value', '')
main_plot.setLabel('bottom', 'time', 's')

graph = main_plot.plot()

graph.setData()

app.exec()