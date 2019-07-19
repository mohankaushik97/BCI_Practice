import serial

class uart():
    def __init__(self):
        start_up = True
        print("waiting for uC")
        while True:
            # wait for the uC to handshake to ensure bite alignment
            while start_up:
                try:
                    line = line.decode('utf-8')
                except UnicodeDecodeError:
                    print("Unable to decode, try restart uC")
                # print(line)
                # uC is starting, move on
                if line == "sstarting\n":
                    start_up = False
                # uC will continously send ss until start is sent
                elif line == "ss\n":
                    self.ser.write('start\n'.encode)