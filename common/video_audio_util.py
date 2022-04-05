import numpy as np
import pyaudio
import wave
import os

from datetime import datetime
import threading

from const.const import *
# IMPORTANT: windows는 https://www.wikihow.com/Install-FFmpeg-on-Windows따라 ffmpeg프로그램 설치
# IMPORTANT: ubuntu 는 apt-get install ffmpeg


class AudioRecorder:
    # Audio class based on pyAudio and Wave
    def __init__(self, device_name):
        self.MIN = 200000  # sum of abs(MUTE) 211783
        self.MAX = 8000000  # 7889292

        self._recording = False
        self._mute = False
        self.current_frame = None
        self.device_name = device_name
        
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        self.audio = pyaudio.PyAudio()
        self.audio_thread = None

        self.stream = None
        self.audio_frames = []
        self.start_frame = None
        self.end_frame = None
        self._terminate = False

    def connect(self):
        dev_index = self.find_device_index(self.device_name)
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      input_device_index=dev_index,
                                      frames_per_buffer=self.frames_per_buffer)

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
    
    def record(self):
        self._recording = True
        self.start_frame = len(self.audio_frames)

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
            self.end_frame = len(self.audio_frames)

    # Launches the audio recording function using a thread
    def stream_audio(self):
        self.audio_thread = threading.Thread(target=self.__stream)
        self.audio_thread.start()

    def __stream(self):
        self.stream.start_stream()
        while not self._terminate:
            data = self.stream.read(self.frames_per_buffer)
            if self._recording:
                if not self._mute:
                    self.audio_frames.append(data)
                else:
                    self.audio_frames.append(bytes(MUTE))

    def terminate(self):
        self._terminate = True
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def save(self, file_path='./',audio_offset=0):
        file_name = self.device_name[0] + '_audio_temp'
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")\
            .replace('/', '')\
            .replace(',', '_')\
            .replace(' ', '')\
            .replace(':', '')
        file_name = current_time + file_name
        if not('.wav' in file_name):
            file_name = file_name+'.wav'
        
        audio_offset = int(self.start_frame+audio_offset)
        wave_file = wave.open(os.path.join(file_path, file_name), 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.audio_frames[audio_offset:self.end_frame]))
        wave_file.close()

        return os.path.join(file_path, file_name)