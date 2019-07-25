from pyqtgraph.Qt import QtGui, QtWidgets, QtCore
import pyqtgraph as pg
import serial
import time
import sys
import numpy as np
import threading
import pyqtgraph.exporters


class Signal(object):
    def __init__(self, pipe, port):
        self.pipe = pipe
        self.port = port
        self.app = QtWidgets.QApplication(sys.argv)

        # create a window to show the graph
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle("EEG Signals")

        # add plot to the graph
        self.main_plot = self.win.addPlot(title="EEG Scale")

        self.y_min = 0
        self.y_max = 255
        self.Fs = 100
        self.sample_interval = 1 / self.Fs

        # Main plot setup
        self.main_plot_t_start = 0
        self.main_plot_t_size = 1023
        self.main_plot_t_end = self.main_plot_t_size
        self.main_plot.setYRange(self.y_min, self.y_max)
        self.main_plot.setLabel('left', 'ADC Value')
        self.main_plot.setLabel('bottom', 'time', 's')

        # create the plot
        self.graph = self.main_plot.plot()
        self.graph_time = np.arange(self.main_plot_t_start, self.main_plot_t_end/self.Fs, self.sample_interval)
        self.graph_pos = self.graph_time[-1]

        # calculation Variables
        self.first_run = True
        self.saved_values = np.zeros(self.main_plot_t_size, dtype='uint16')

        self.graph_N = 1023
        self.graph_data_read = False
        self.graph_head = 0
        self.graph_tail = self.graph_head
        self.graph_buff = int(self.y_max / 2) * np.ones(self.graph_N, dtype='uint16')
        self.serial_thread = threading.Thread(target=self.serial_read, daemon=True)
        self.ser = None
        self.plot_timer = None

        self.filename = ''
        self.logfile = None

        if self.pipe is not None:
            self.start()

    def start(self):
        self.ser = serial.Serial(self.port, baudrate=57600, parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

        if not self.ser.isOpen():
            print('Failed to open port')
            return
        print("Port opened")

        self.filename = '/Users/mohankaushik/Desktop/BCI_Practice/New/' + time.ctime() + '.csv'
        self.filename = self.filename.replace(':', '-')
        print('Opening data log file ' + self.filename)
        self.logfile = open(self.filename, 'w+')

        if not self.logfile:
            print('Failed to open Logfile')
            return

        # create a timer to update graph every timeout
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(25)

        # start thread to read from serial port
        self.serial_thread.start()

        self.app.exec()

    def serial_read(self):
        self.ser.reset_input_buffer()
        while True:
            self.graph_data_read = True
            value = self.ser.readline()
            print(value)

            self.graph_buff[:-1] = self.graph_buff[1:]
            self.graph_buff[-1] = value

            # shift cursor
            self.graph_time[:-1] = self.graph_time[1:]
            self.graph_pos += self.sample_interval
            self.graph_time[-1] = self.graph_pos

            # write value to logfile
            self.logfile.write(str(self.graph_buff[-1]) + '\n')

            # shift head forward
            self.graph_head = (self.graph_head + 1) % self.graph_N

    def update_plot(self):
        if self.graph_data_read:
            self.graph_data_read = False
            self.graph.setData(self.graph_time, self.graph_buff)

    def show(self):
        self.app.exec()

    def exit(self):
        print("exit called")
        self.app.exit()
        sys.exit()


if __name__ == '__main__':
    signal = Signal(None, '/dev/cu.usbmodem14203')
    signal.start()
