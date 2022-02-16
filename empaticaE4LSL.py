# save livestream data of E4 wristband as a txt file per each sensing signal.
# run in python 3.7
# it needs pylsl package
import os
import socket
import time
import pylsl
import pandas as pd
import keyboard


# SELECT DATA TO STREAM
acc = True  # 3-axis acceleration
bvp = True # Blood Volume Pulse
gsr = True # Galvanic Skin Response (Electrodermal Activity)
tmp = True  # Temperature
ibi = True  # Interbeat Interval
tag = True

serverAddress = '127.0.0.1'
serverPort = 28000
bufferSize = 4096

# deviceID = 'CD36CD'  # 'A02088'

samples_acc = []
samples_bvp = []
samples_gsr = []
samples_temp = []
samples_ibi = []
samples_tag = []

stream_on = True


def connect(deviceid):
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)

    print("Connecting to server")
    s.connect((serverAddress, serverPort))
    print("Connected to server\n")

    print("Devices available:")
    s.send("device_list\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))

    print("Connecting to device")
    s.send(("device_connect " + deviceid + "\r\n").encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))

    print("Pausing data receiving")
    s.send("pause ON\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))


def suscribe_to_data():
    if acc:
        print("Suscribing to ACC")
        s.send(("device_subscribe " + 'acc' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bvp:
        print("Suscribing to BVP")
        s.send(("device_subscribe " + 'bvp' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if gsr:
        print("Suscribing to GSR")
        s.send(("device_subscribe " + 'gsr' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tmp:
        print("Suscribing to Temp")
        s.send(("device_subscribe " + 'tmp' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if ibi:
        print("Suscribing to IBI")
        s.send(("device_subscribe " + 'ibi' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tag:
        print("Suscribing to Tag")
        s.send(("device_subscribe " + 'tag' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))

    print("Resuming data receiving")
    s.send("pause OFF\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))


def prepare_LSL_streaming():
    print("Starting LSL streaming")

    if acc:
        infoACC = pylsl.StreamInfo('acc', 'ACC', 3, 32, 'int32', 'ACC-empatica_e4');
        global outletACC
        outletACC = pylsl.StreamOutlet(infoACC)
    if bvp:
        infoBVP = pylsl.StreamInfo('bvp', 'BVP', 1, 64, 'float32', 'BVP-empatica_e4');
        global outletBVP
        outletBVP = pylsl.StreamOutlet(infoBVP)
    if gsr:
        infoGSR = pylsl.StreamInfo('gsr', 'GSR', 1, 4, 'float32', 'GSR-empatica_e4');
        global outletGSR
        outletGSR = pylsl.StreamOutlet(infoGSR)
    if tmp:
        infoTemp = pylsl.StreamInfo('tmp', 'Temp', 1, 4, 'float32', 'Temp-empatica_e4');
        global outletTemp
        outletTemp = pylsl.StreamOutlet(infoTemp)
    if ibi:
        infoIBI = pylsl.StreamInfo('hr', 'HR', 1, 1, 'float32', 'IBI-empatica_e4');
        global outletIBI
        outletTemp = pylsl.StreamOutlet(infoIBI)
    if tag:
        infoTag = pylsl.StreamInfo('tag', 'Tag', 1, channel_format='float32', source_id='Tag-empatica_e4');
        global outletTag
        outletTag = pylsl.StreamOutlet(infoTag)
        print('ok')


def reconnect(deviceid):
    print("Reconnecting...")
    connect(deviceid)
    suscribe_to_data()
    stream(deviceid)


def save_data(folder):

    with open(os.path.join(folder, "acc.csv"), 'w') as f:
        for sample in samples_acc:
            f.write(sample + '\n')
    with open(os.path.join(folder, "bvp.csv"), 'w') as f:
        for sample in samples_bvp:
            f.write(sample + '\n')
    with open(os.path.join(folder, "gsr.csv"), 'w') as f:
        for sample in samples_gsr:
            f.write(sample + '\n')
    with open(os.path.join(folder, "temp.csv"), 'w') as f:
        for sample in samples_temp:
            f.write(sample + '\n')
    with open(os.path.join(folder, "ibi.csv"), 'w') as f:
        for sample in samples_ibi:
            f.write(sample + '\n')
    with open(os.path.join(folder, "tags.csv"), 'w') as f:
        for sample in samples_tag:
            f.write(sample + '\n')

    print("Saved datastream")


def mark_e4(key):
    content = str(time.time()) + ", [Alt] + %s" % key
    samples_tag.append(content)
    samples_acc.append(content)
    samples_bvp.append(content)
    samples_gsr.append(content)
    samples_ibi.append(content)
    samples_temp.append(content)


def stream(deviceid):

    try:
        print("Streaming...")
        print("start stream UTC : ", time.time())
        while stream_on:

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
                response = s.recv(bufferSize).decode("utf-8")
                # print(response)
                if "connection lost to device" in response:
                    print(response.decode("utf-8"))
                    reconnect(deviceid)
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
                        samples_acc.append(str(timestamp) + ',' + str(data))
                        # print(timestamp, data)
                    if stream_type == "E4_Bvp":
                        timestamp = float(samples[i].split()[1].replace(',', '.'))
                        data = float(samples[i].split()[2].replace(',', '.'))
                        # outletBVP.push_sample([data], timestamp=timestamp)
                        samples_bvp.append(str(timestamp) + ',' + str(data))
                        # print(timestamp, data)
                    if stream_type == "E4_Gsr":
                        timestamp = float(samples[i].split()[1].replace(',', '.'))
                        data = float(samples[i].split()[2].replace(',', '.'))
                        # outletGSR.push_sample([data], timestamp=timestamp)
                        samples_gsr.append(str(timestamp) + ',' + str(data))
                        # print(timestamp, data)
                    if stream_type == "E4_Temperature":
                        timestamp = float(samples[i].split()[1].replace(',', '.'))
                        data = float(samples[i].split()[2].replace(',', '.'))
                        # outletTemp.push_sample([data], timestamp=timestamp)
                        samples_temp.append(str(timestamp) + ',' + str(data))
                        # print(timestamp, data)
                    if stream_type == "E4_Ibi":
                        # 안됨
                        timestamp = float(samples[i].split()[1].replace(',', '.'))
                        data = float(samples[i].split()[2].replace(',', '.'))
                        # outletIBI.push_sample([data], timestamp=timestamp)
                        samples_ibi.append(str(timestamp) + ',' + str(data))
                        # print(timestamp, data)
                    if stream_type == "E4_Tag":
                        timestamp = float(samples[i].split()[1].replace(',', '.'))
                        data = float(samples[i].split()[2].replace(',', '.'))
                        # outletTag.push_sample([data], timestamp=timestamp)
                        samples_tag.append(str(timestamp) + ',' + '[TAG]')
                        samples_acc.append(str(timestamp) + ',' + '[TAG]')
                        samples_bvp.append(str(timestamp) + ',' + '[TAG]')
                        samples_gsr.append(str(timestamp) + ',' + '[TAG]')
                        samples_ibi.append(str(timestamp) + ',' + '[TAG]')
                        samples_temp.append(str(timestamp) + ',' + '[TAG]')
                        print("[MARK TAG] : ", timestamp, data)
                # time.sleep(1)
            except socket.timeout:
                print("Socket timeout")
                reconnect(deviceid)
                break
    except KeyboardInterrupt:
        print("Disconnecting from device")
        s.send("device_disconnect\r\n".encode())
        s.close()



def stop_E4streaming(p_folder):
    global stream_on
    mark_e4('o')
    stream_on = False
    time.sleep(1)
    print("Disconnecting from device")
    s.send("device_disconnect\r\n".encode())
    s.close()
    save_data(p_folder)


def run_E4streaming(deviceid):
    connect(deviceid)
    time.sleep(1)
    suscribe_to_data()
    prepare_LSL_streaming()
    time.sleep(1)
    stream(deviceid)
