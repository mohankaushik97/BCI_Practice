import sys
import time
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
import serial
import threading


class Signal(object):
    def __init__(self, pipe, port):
        self.pipe = pipe
        self.port = port
        self.app = QtWidgets.QApplication(sys.argv)

        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle("EEG Scale")

        # Add Real Time Plot
        self.main_plot = self.win.addPlot(title="Raw Data")

        # Add FFT Plot
        self.win.nextRow()
        self.fft_plot = self.win.addPlot(title="FFT Plot")

        self.y_min = 0
        self.y_max = 4095
        self.Fs = 1000
        self.sample_interval = 1 / self.Fs

        # main Plot Setup
        self.main_plot_t_start = 0
        self.main_plot_t_size = 2047
        self.main_plot_t_end = self.main_plot_t_size
        self.main_plot.setYRange(self.y_min, self.y_max)
        self.main_plot.setLabel('left', 'ADC Value', '')
        self.main_plot.setLabel('bottom', 'time', 's')

        # Creating the plot
        self.graph = self.main_plot.plot()
        self.graph_time = np.arange(self.main_plot_t_start, self.main_plot_t_end / self.Fs, self.sample_interval)
        self.graph_pos = self.graph_time[-1]  # Place Cursor at the far right of the screen

        # FFT Variables
        self.fft_sample_size = 1000
        self.fft_sample_num = 0
        self.fft_padding = 5
        # Frequency axis
        self.fft_freq = np.fft.rfftfreq(self.fft_sample_size * self.fft_padding, 1 / self.Fs)

        # FFT graph setup
        self.fft_plot.setYRange(0, 250)
        self.fft_plot.setXRange(0, 100)
        self.fft_plot.setLabel('left', 'ADC Value', '')
        self.fft_plot.setLabel('bottom', 'Frequency', 'Hz')

        self.fft_graph = self.fft_plot.plot()
        self.fft_graph_fft_mag = np.zeros(int((self.fft_sample_size * self.fft_padding) / 2) + 1)

        # Calculation Variables
        self.first_run = True
        self.saved_values = np.zeros(self.main_plot_t_size, dtype='uint16')

        self.graph_N = 2047
        self.graph_data_read = False
        self.graph_head = 0
        self.graph_tail = self.graph_head
        self.graph_buff = int(self.y_max / 2) * np.ones(self.graph_N, dtype='uint16')
        self.serial_thread = threading.Thread(target = self.serial_read, daemon = True)
        self.ser = None
        self.plot_timer = None

        # logging variables
        self.filename = ''
        self.logfile = None

        # Start automatically if pipe was given
        if self.pipe is not None:
            self.start()

    def start(self):
        # Serial variables
        self.ser = serial.Serial(self.port, baudrate=57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS)

        if not self.ser.isOpen():
            print('Failed to open port')
            return

        # create log file
        self.filename = 'home/mohan/Desktop/BCI_Practice/New' + time.ctime() + '.csv'
        self.filename = self.filename.replace(':', '-')
        print('Opening data log file' + self.fimename + '...')
        self.logfile = open(self.filename, 'w')

        if not self.logfile:
            print('Failed to open logfile')
            return

        # Create a timer to update graph every timeout
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(25)

        # start thread to read from serial port
        self.serial_thread.start()

        self.app.exec_()

    def serial_read(self):
        self.ser.reset_input_buffer()
        start_up = True
        print("waiting for uC")


        while self.ser.inWaiting() >=2:

            self.graph_data_read = True
            lowbyte = self.ser.read()
            highbyte = self.ser.read()

            self.graph_buff[:-1] = self.graph_buff[1:]
            self.graph_buff[-1] = (ord(highbyte) << 8) + ord(lowbyte)

            self.graph_time[:-1] = self.graph_time[1:]
            # shift sursor
            self.graph_pos += self.sample_interval
            self.graph_time[-1] = self.graph_pos

            # Write value to log file
            self.logfile.write(str(self.graph_buff[-1]) + '\n')

            # Shift head forward
            self.graph_head = (self.graph_head + 1) % self.graph_N

            self.fft_sample_num += 1
            if self.fft_sample_num ==self.fft_sample_size:
                self.fft_sample_num = 0
                self.calc()

    def update_plot(self):
        # Only update plot is data has been read
        if self.graph_data_read:
            self.graph_data_read = False
            # Set set new data to plot
            self.graph.setData(self.graph_time, self.graph_buff)

    def calc(self):
        # store current buff so it doesn't changed as we're doing calculations
        temp_buff = self.graph_buff[self.main_plot_t_size-self.fft_sample_size:]
        # Remove DC offset
        temp_buff = temp_buff - np.mean(temp_buff)

        # If there is a pipe, send temp before
        if self.pipe is not None:
            self.pipe.send(temp_buff[:])

        # FFT calculations
        ham = np.hamming(self.fft_sample_size)
        y_ham = temp_buff * ham
        self.fft_graph_fft_mag = 4/self.fft_sample_size * \
            np.abs(np.fft.rfft(y_ham, self.fft_sample_size * self.fft_padding))

        # Set FFT data
        self.fft_graph.setData(self.fft_freq, self.fft_graph_fft_mag)


    def show(self):
        self.win.show()
        self.app.exec()

    def exit(self):
        print('Exit called')
        sys.exit()


if __name__ == '__main__':
        signal = Signal(None,'COM5')
        signal.start()
