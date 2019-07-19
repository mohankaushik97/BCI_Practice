import sys
import time
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
import serial
import threading


app = QtWidgets.QApplication(sys.argv)
#Creating window
win = pg.GraphicsWindow()
win.setWindowTitle("EEG Scale")

#Add Real Time Plot
main_plot = win.addPlot(title = "Raw Data")

#Add FFT Plot
win.nextRow()
fft_plot = win.addPlot(title = "FFT Plot")

y_min = 0
y_max = 4095
Fs = 1000
sample_interval = 1/ Fs

#main Plot Setup
main_plot_t_start = 0
main_plot_t_size = 2047
main_plot_t_end = main_plot_t_size
main_plot.setYRange(y_min, y_max)
main_plot.setLabel('left', 'ADC Value', '')
main_plot.setLabel('bottom', 'time', 's')

#Creating the plot
graph = main_plot.plot()
graph_time = np.arange(main_plot_t_start, main_plot_t_end/Fs, sample_interval)
graph_pos = graph_time[-1] #Place Cursor at the far right of the screen

#FFT Variables
fft_sample_size = 1000
fft_sample_num = 0
fft_padding = 5
#Frequency axis
fft_freq = np.fft.rfftfreq(fft_sample_size * fft_padding, 1/Fs)

#FFT graph setup
fft_plot.setYRange(0,250)
fft_plot.setXRange(0,100)
fft_plot.setLabel('left', 'ADC Value', '')
fft_plot.setLabel('bottom', 'Frequency', 'Hz')

fft_graph = fft_plot.plot()
fft_graph_fft_mag = np.zeros(int((fft_sample_size * fft_padding)/2) + 1)

#Calculation Variables
first_run = True
saved_values = np.zeros(main_plot_t_size, dtype='uint16')

graph_N = 2047
graph_data_read = False
graph_head = 0
graph_tail = graph_head
graph_buff = int(y_max / 2) * np.ones(graph_N,dtype='uint16')
# serial_thread = threading.Thread(target = serial_read, daemon = True)
ser = None
plot_timer = None


win.show()
app.exec()
# print(time.time())
# time.sleep(5)
# print(time.time())
# sys.exit()
