# save livestream data of E4 wristband as a txt file per each sensing signal.
# run in python 3.7
# it needs pylsl package
import os
import socket
import time
import pylsl
from datetime import datetime


class GSR:
    def __init__(self, deviceid, host='127.0.0.1', port=28000):
        # SELECT DATA TO STREAM
        self.acc = True  # 3-axis acceleration
        self.bvp = True  # Blood Volume Pulse
        self.gsr = True  # Galvanic Skin Response (Electrodermal Activity)
        self.tmp = True  # Temperature
        self.ibi = True  # Interbeat Interval
        self.tag = True

        self.serverAddress = host
        self.serverPort = port
        self.bufferSize = 4096

        # deviceID = 'CD36CD'  # 'A02088'

        self.samples_acc = []
        self.acc_start = None
        self.acc_end = None
        self.samples_bvp = []
        self.bvp_start = None
        self.bvp_end = None
        self.samples_gsr = []
        self.gsr_start = None
        self.gsr_end = None
        self.samples_temp = []
        self.temp_start = None
        self.temp_end = None
        self.samples_ibi = []
        self.ibi_start = None
        self.ibi_end = None
        self.samples_tag = []
        self.tag_start = None
        self.tag_end = None

        self.stream_on = True
        self.deviceid = deviceid
        self.s = None

        self._recording = False
        self.start_checker = 0
        self.standard_time = 0

    def clear(self):
        self.samples_tag = []
        self.samples_acc = []
        self.samples_ibi = []
        self.samples_gsr = []
        self.samples_temp = []
        self.samples_bvp = []

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(3)

        print("Connecting to server")
        self.s.connect((self.serverAddress, self.serverPort))
        print("Connected to server\n")

        print("Devices available:")
        self.s.send("device_list\r\n".encode())
        response = self.s.recv(self.bufferSize)
        print(response.decode("utf-8"))

        print("Connecting to device")
        self.s.send(("device_connect " + self.deviceid + "\r\n").encode())
        response = self.s.recv(self.bufferSize)
        print(response.decode("utf-8"))

        print("Pausing data receiving")
        self.s.send("pause ON\r\n".encode())
        response = self.s.recv(self.bufferSize)
        print(response.decode("utf-8"))

    def subscribe_to_data(self):
        if self.acc:
            print("Suscribing to ACC")
            self.s.send(("device_subscribe " + 'acc' + " ON\r\n").encode())
            response = self.s.recv(self.bufferSize)
            print(response.decode("utf-8"))
        if self.bvp:
            print("Suscribing to BVP")
            self.s.send(("device_subscribe " + 'bvp' + " ON\r\n").encode())
            response = self.s.recv(self.bufferSize)
            print(response.decode("utf-8"))
        if self.gsr:
            print("Subscribing to GSR")
            self.s.send(("device_subscribe " + 'gsr' + " ON\r\n").encode())
            response = self.s.recv(self.bufferSize)
            print(response.decode("utf-8"))
        if self.tmp:
            print("Subscribing to Temp")
            self.s.send(("device_subscribe " + 'tmp' + " ON\r\n").encode())
            response = self.s.recv(self.bufferSize)
            print(response.decode("utf-8"))
        if self.ibi:
            print("Subscribing to IBI")
            self.s.send(("device_subscribe " + 'ibi' + " ON\r\n").encode())
            response = self.s.recv(self.bufferSize)
            print(response.decode("utf-8"))
        if self.tag:
            print("Subscribing to Tag")
            self.s.send(("device_subscribe " + 'tag' + " ON\r\n").encode())
            response = self.s.recv(self.bufferSize)
            print(response.decode("utf-8"))

        print("Resuming data receiving")
        self.s.send("pause OFF\r\n".encode())
        response = self.s.recv(self.bufferSize)
        print(response.decode("utf-8"))

    def prepare_LSL_streaming(self):
        print("Starting LSL streaming")

        if self.acc:
            infoACC = pylsl.StreamInfo('acc', 'ACC', 3, 32, 'int32', 'ACC-empatica_e4')
            global outletACC
            outletACC = pylsl.StreamOutlet(infoACC)
        if self.bvp:
            infoBVP = pylsl.StreamInfo('bvp', 'BVP', 1, 64, 'float32', 'BVP-empatica_e4')
            global outletBVP
            outletBVP = pylsl.StreamOutlet(infoBVP)
        if self.gsr:
            infoGSR = pylsl.StreamInfo('gsr', 'GSR', 1, 4, 'float32', 'GSR-empatica_e4')
            global outletGSR
            outletGSR = pylsl.StreamOutlet(infoGSR)
        if self.tmp:
            infoTemp = pylsl.StreamInfo('tmp', 'Temp', 1, 4, 'float32', 'Temp-empatica_e4')
            global outletTemp
            outletTemp = pylsl.StreamOutlet(infoTemp)
        if self.ibi:
            infoIBI = pylsl.StreamInfo('hr', 'HR', 1, 1, 'float32', 'IBI-empatica_e4')
            global outletIBI
            outletTemp = pylsl.StreamOutlet(infoIBI)
        if self.tag:
            infoTag = pylsl.StreamInfo('tag', 'Tag', 1, channel_format='float32', source_id='Tag-empatica_e4')
            global outletTag
            outletTag = pylsl.StreamOutlet(infoTag)
            print('ok')

    def reconnect(self):
        print("Reconnecting...")
        self.connect()
        self.subscribe_to_data()
        self.stream()

    def save_data(self, folder):
        if self._recording:
            self.stop_record()

        with open(os.path.join(folder, "acc.csv"), 'w') as f:
            samples_acc = self.samples_acc[self.acc_start:self.acc_end]
            for sample in samples_acc:
                f.write(sample + '\n')
        with open(os.path.join(folder, "bvp.csv"), 'w') as f:
            samples_bvp = self.samples_bvp[self.bvp_start:self.bvp_end]
            for sample in samples_bvp:
                f.write(sample + '\n')
        with open(os.path.join(folder, "gsr.csv"), 'w') as f:
            samples_gsr = self.samples_gsr[self.gsr_start:self.gsr_end]
            for sample in samples_gsr:
                f.write(sample + '\n')
        with open(os.path.join(folder, "temp.csv"), 'w') as f:
            samples_temp = self.samples_temp[self.temp_start:self.temp_end]
            for sample in samples_temp:
                f.write(sample + '\n')
        with open(os.path.join(folder, "ibi.csv"), 'w') as f:
            samples_ibi = self.samples_ibi[self.ibi_start:self.ibi_end]
            for sample in samples_ibi:
                f.write(sample + '\n')
        with open(os.path.join(folder, "tags.csv"), 'w') as f:
            samples_tag = self.samples_tag[self.tag_start:self.tag_end]
            for sample in samples_tag:
                f.write(sample + '\n')

    def mark_e4(self, key):
        content = str(time.time()) + ", [Alt] + %s" % key
        self.samples_tag.append(content)
        self.samples_acc.append(content)
        self.samples_bvp.append(content)
        self.samples_gsr.append(content)
        self.samples_ibi.append(content)
        self.samples_temp.append(content)

    def stream(self):

        try:
            print("Streaming...")
            print("start stream UTC : ", time.time())
            while self.stream_on:

                #
                # if keyboard.is_pressed('q'):
                #     print("Disconnecting from device")
                #     s.send("device_disconnect\r\n".encode())
                #     s.close()
                #     save_data()

                # elif keyboard.is_pressed('t'):
                #     print("TAG")
                #     samples_tag.append(str(timestamp))
                #     samples_acc.append(str(timestamp) + ',' + '[TAG]')
                #     samples_bvp.append(str(timestamp) + ',' + '[TAG]')
                #     samples_gsr.append(str(timestamp) + ',' + '[TAG]')
                #     samples_ibi.append(str(timestamp) + ',' + '[TAG]')
                #     samples_temp.append(str(timestamp) + ',' + '[TAG]')

                try:
                    response = self.s.recv(self.bufferSize).decode("utf-8")
                    # print(response)
                    if "connection lost to device" in response:
                        print(response.decode("utf-8"))
                        self.reconnect()
                        break
                    samples = response.split("\n")
                    for i in range(len(samples) - 1):
                        stream_type = samples[i].split()[0]
                        if stream_type == "E4_Acc":
                            timestamp = float(samples[i].split()[1].replace(',', '.'))
                            data = [int(samples[i].split()[2].replace(',', '.')),
                                    int(samples[i].split()[3].replace(',', '.')),
                                    int(samples[i].split()[4].replace(',', '.'))]
                            # outletACC.push_sample(data, timestamp=timestamp)

                            self.samples_acc.append(f'{timestamp}, {data}')
                            # print('ACC', timestamp, data)
                        if stream_type == "E4_Bvp":
                            timestamp = float(samples[i].split()[1].replace(',', '.'))
                            data = float(samples[i].split()[2].replace(',', '.'))
                            # outletBVP.push_sample([data], timestamp=timestamp)

                            self.samples_bvp.append(f'{timestamp}, {data}')
                            # print('BVP', timestamp, data)
                        if stream_type == "E4_Gsr":
                            timestamp = float(samples[i].split()[1].replace(',', '.'))
                            data = float(samples[i].split()[2].replace(',', '.'))
                            # outletGSR.push_sample([data], timestamp=timestamp)
                            self.samples_gsr.append(f'{timestamp}, {data}')
                            # print('GSR', timestamp, data)
                        if stream_type == "E4_Temperature":
                            timestamp = float(samples[i].split()[1].replace(',', '.'))
                            data = float(samples[i].split()[2].replace(',', '.'))
                            # outletTemp.push_sample([data], timestamp=timestamp)
                            self.samples_temp.append(f'{timestamp}, {data}')
                            # print('Temp', timestamp, data)
                        if stream_type == "E4_Ibi":
                            # 안됨
                            timestamp = float(samples[i].split()[1].replace(',', '.'))
                            data = float(samples[i].split()[2].replace(',', '.'))
                            # outletIBI.push_sample([data], timestamp=timestamp)
                            self.samples_ibi.append(f'{timestamp}, {data}')
                            # print('IBI', timestamp, data)
                        if stream_type == "E4_Tag":
                            timestamp = float(samples[i].split()[1].replace(',', '.'))
                            data = float(samples[i].split()[2].replace(',', '.'))
                            # outletTag.push_sample([data], timestamp=timestamp)
                            self.samples_tag.append(f'{timestamp}, [TAG]')
                            self.samples_acc.append(f'{timestamp}, [TAG]')
                            self.samples_bvp.append(f'{timestamp}, [TAG]')
                            self.samples_gsr.append(f'{timestamp}, [TAG]')
                            self.samples_ibi.append(f'{timestamp}, [TAG]')
                            self.samples_temp.append(f'{timestamp}, [TAG]')
                            # print("[MARK TAG] : ", timestamp, data)
                    # time.sleep(1)
                except socket.timeout:
                    print("Socket timeout")
                    self.reconnect()
                    break
        except KeyboardInterrupt:
            print("Disconnecting from device")
            self.s.send("device_disconnect\r\n".encode())
            self.s.close()

    def record(self):
        self._recording = True
        self.gsr_start = len(self.samples_gsr)
        self.ibi_start = len(self.samples_ibi)
        self.temp_start = len(self.samples_temp)
        self.acc_start = len(self.samples_acc)
        self.bvp_start = len(self.samples_bvp)
        self.tag_start = len(self.samples_tag)

    def stop_record(self):
        self._recording = False
        self.start_checker = 0
        self.gsr_end = len(self.samples_gsr)
        self.ibi_end = len(self.samples_ibi)
        self.temp_end = len(self.samples_temp)
        self.acc_end = len(self.samples_acc)
        self.bvp_end = len(self.samples_bvp)
        self.tag_end = len(self.samples_tag)

    def terminate(self, p_folder):
        self.mark_e4('o')
        self.stream_on = False
        time.sleep(1)
        print("Disconnecting from device")
        self.s.send("device_disconnect\r\n".encode())
        self.s.close()
        print("GSR is terminated")
        # self.save_data(p_folder)

    def ready(self):
        self.connect()
        time.sleep(1)
        self.subscribe_to_data()
        self.prepare_LSL_streaming()
        time.sleep(1)
        print("GSR is ready")
        # self.stream()
