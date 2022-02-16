import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
import threading


class ISMSocket:
    """
    Integrated sensor monitoring tool TCP/IP socket
    """
    def __init__(self, host, port, logging=None):
        self.logging = logging

        self.host = host
        self.port = port
        self.done = False
        self.data_log = b''
        self.latest_packets = []
        self.latest_packet_headers = []
        self.latest_packet_data = np.zeros((1, 1))
        self.signal_log = np.zeros((1, 20))
        self.time_log = np.zeros((1, 20))
        self.montage = []
        self.fsample = 0
        self.fmains = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def stream_signal(self, parser_func):
        pass

    def parse_data(self):
        # parse_data() receives DSI-Streamer TCP/IP packets and updates the signal_log and time_log attributes
        # which capture EEG data and time data, respectively, from the last 100 EEG data packets (by default) into a numpy array.
        while not self.done:
            data = self.sock.recv(921600)
            self.data_log += data
            if self.data_log.find(b'@ABCD', 0, len(
                    self.data_log)) != -1:  # The script looks for the '@ABCD' header start sequence to find packets.
                for index, packet in enumerate(self.data_log.split(b'@ABCD')[
                                               1:]):  # The script then splits the inbound transmission by the header start sequence to collect the individual packets.
                    self.latest_packets.append(b'@ABCD' + packet)
                for packet in self.latest_packets:
                    self.latest_packet_headers.append(struct.unpack('>BHI', packet[5:12]))
                self.data_log = b''

                for index, packet_header in enumerate(self.latest_packet_headers):
                    # For each packet in the transmission, the script will append the signal data and timestamps to their respective logs.
                    if packet_header[0] == 1:
                        if np.shape(self.signal_log)[0] == 1:  # The signal_log must be initialized based on the headset and number of available channels.
                            self.signal_log = np.zeros((int(len(self.latest_packets[index][23:]) / 4), 20))
                            self.time_log = np.zeros((1, 20))
                            self.latest_packet_data = np.zeros((int(len(self.latest_packets[index][23:]) / 4), 1))

                        self.latest_packet_data = np.reshape(
                            struct.unpack('>%df' % (len(self.latest_packets[index][23:]) / 4),
                                          self.latest_packets[index][23:]), (len(self.latest_packet_data), 1))
                        self.latest_packet_data_timestamp = np.reshape(
                            struct.unpack('>f', self.latest_packets[index][12:16]), (1, 1))

                        print("Timestamps: " + str(self.latest_packet_data_timestamp))
                        print("Signal Data: " + str(self.latest_packet_data))

                        self.signal_log = np.append(self.signal_log, self.latest_packet_data, 1)
                        self.time_log = np.append(self.time_log, self.latest_packet_data_timestamp, 1)
                        self.signal_log = self.signal_log[:, -100:]
                        self.time_log = self.time_log[:, -100:]
                    ## Non-data packet handling
                    if packet_header[0] == 5:
                        (event_code, event_node) = struct.unpack('>II', self.latest_packets[index][12:20])
                        if len(self.latest_packets[index]) > 24:
                            message_length = struct.unpack('>I', self.latest_packets[index][20:24])[0]
                        print("Event code = " + str(event_code) + "  Node = " + str(event_node))
                        if event_code == 9:
                            montage = self.latest_packets[index][24:24 + message_length].decode()
                            montage = montage.strip()
                            print("Montage = " + montage)
                            self.montage = montage.split(',')
                        if event_code == 10:
                            frequencies = self.latest_packets[index][24:24 + message_length].decode()
                            print("Mains,Sample = " + frequencies)
                            mains, sample = frequencies.split(',')
                            self.fsample = float(sample)
                            self.fmains = float(mains)
            self.latest_packets = []
            self.latest_packet_headers = []

    def example_plot(self):

        # example_plot() uses the threading python library and matplotlib to plot the eeg data in realtime.
        # the plots are unlabeled but users can refer to the tcp/ip socket protocol documentation to understand how to discern the different plots given their indices.
        # ideally, each eeg plot should have its own subplot but for demonstrative purposes, they are all plotted on the same figure.
        data_thread = threading.Thread(target=self.parse_data)
        data_thread.start()

        refresh_rate = 0.03
        duration = 60  # the default plot duration is 60 seconds.
        runtime = 0

        fig = plt.figure()

        while True:  # runtime < duration/refresh_rate:
            self.signal_log = self.signal_log[:, -1000:]
            self.time_log = self.time_log[:, -1000:]
            plt.clf()
            try:
                plt.plot(self.time_log.t, self.signal_log.t)
            except:
                pass
            plt.gca().legend(self.montage)
            plt.xlabel('timestamp')
            plt.ylabel('peak-to-peak uv')
            plt.title('dsi-streamer tcp/ip eeg sensor data output')
            plt.pause(refresh_rate)
            runtime += 1
        plt.show()

        self.done = True
        data_thread.join()

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    eeg_test = ISMSocket('localhost', 8844)
    eeg_test.example_plot()
