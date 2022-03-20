import numpy as np
import pyaudio
import wave

from datetime import datetime
import threading

from const.const import *
# IMPORTANT: windows는 https://www.wikihow.com/Install-FFmpeg-on-Windows따라 ffmpeg프로그램 설치
# IMPORTANT: ubuntu 는 apt-get install ffmpeg

class AudioRecorder():
    # Audio class based on pyAudio and Wave
    def __init__(self, device_name):
        self.MIN = 200000 # sum of abs(MUTE) 211783
        self.MAX = 8000000 # 7889292

        self._recording = True
        self._mute = False
        self.current_frame = None
        self.device_name = device_name
        
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        self.audio = pyaudio.PyAudio()

        self.stream = None
        self.audio_frames = []
        self.flag = 0
        self.cnt = 0

    def connect(self):
        dev_index = self.find_device_index(self.device_name)
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      input_device_index = dev_index,
                                      frames_per_buffer = self.frames_per_buffer)

    def find_device_index(self, device_name):
        dev_index = 0
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            # print(dev['name'], dev['hostApi'])
            if (self.is_it_mic_or_stero_mix(device_name, dev)):
                dev_index = dev['index']
                print('dev_index', dev_index)
                break

        return dev_index
    
    def count(self):
        self.flag = self.cnt
        self.cnt = 0

    def is_it_mic_or_stero_mix(self, device_name, dev):
        flag = False
        # print(dev['name'])
        if '마이크' in device_name[0]:
            if (( device_name[0] in dev['name'] and device_name[1] in dev['name']) and dev['hostApi'] == 0):
                flag = True
        else:
            if (( device_name[0] in dev['name'] or device_name[1] in dev['name']) and dev['hostApi'] == 0):
                flag = True
        return flag

    def mute(self):
        self._mute = True
    
    def undo_mute(self):
        self._mute = False
    
    def clear(self):
        self.audio_frames = []

    def get_current_audio_value(self):
        data = np.frombuffer(self.current_frame, dtype=np.int16)
        data = np.abs(data).sum()
        data = (data-self.MIN)/(self.MAX-self.MIN)
        return data
    
    # Finishes the audio recording therefore the thread too    
    def stop(self):
        if self._recording:
            self._recording = False
            self.stream.stop_stream()
            # self.stream.close()
            # self.audio.terminate()

    # Launches the audio recording function using a thread
    def record(self):
        self._recording = True
        audio_thread = threading.Thread(target=self.__record)
        audio_thread.start()
    
    def __record(self):
        self.stream.start_stream()
        while self._recording:
            data = self.stream.read(self.frames_per_buffer)
            if not self._mute:
                self.audio_frames.append(data)
            else:
                self.audio_frames.append(bytes(MUTE))
            self.cnt = self.cnt + 1        
    
    def save(self,start_frame=0, end_frame=-1, file_name='temp', file_path='./'):
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")\
            .replace('/', '')\
            .replace(',', '_')\
            .replace(' ', '')\
            .replace(':', '')
        file_name = current_time + file_name
        if not('.wav' in file_name):
            file_name = file_name+'.wav'
        
        wave_file = wave.open(file_path+file_name, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.audio_frames[start_frame:end_frame]))
        wave_file.close()

        return file_path + file_name