import cv2
import numpy as np
import pyaudio
import wave
import time
import threading
from datetime import datetime

from const.const import *
# IMPORTANT: windows는 https://www.wikihow.com/Install-FFmpeg-on-Windows따라 ffmpeg프로그램 설치
# IMPORTANT: ubuntu 는 apt-get install ffmpeg
import ffmpeg


# TODO: Add caption for each attribute
# TODO: refactoring
class WebcamRecorder:
    def __init__(self, camera_index=0):
        self._video_recorder = VideoRecorder(camera_index)
        self._audio_recorder = AudioRecorder()
        
    def record(self):
        self._audio_recorder.record()
        self._video_recorder.record()
    
    def stop(self):
        self._audio_recorder.stop()
        self._video_recorder.stop()
    
    def clear(self):
        self._video_recorder.clear()
        self._audio_recorder.clear()

    def get_current_video_value(self):
        return self._video_recorder.get_current_video_value()
    
    def get_current_audio_value(self):
        return self._audio_recorder.get_current_audio_value()
    
    def save(self, start_frame=0, end_frame=-1, video_offset=0, audio_offset=30, file_name='None', file_path='./'):
        vid_file = self._video_recorder.save(start_frame + video_offset, end_frame)
        aud_file = self._audio_recorder.save(start_frame + audio_offset, end_frame)

        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S").replace('/','').replace(',','_').replace(' ','').replace(':','')
        file_name = current_time + '_' + file_name
        if not('.mp4' in file_name):
            file_name = file_name+'.mp4'

        # video_stream = ffmpeg.input(vid_file)
        # audio_stream = ffmpeg.input(aud_file)
        # stream = ffmpeg.output(audio_stream, video_stream, file_name).run()
        #
        # try:
        #     if os.path.exists(aud_file):
        #         os.remove(aud_file)
        #
        #     if os.path.exists(vid_file):
        #         os.remove(vid_file)
        # except:
        #     print('Fail to delete temp files')


class VideoRecorder:
    def __init__(self, camera_index=0):
        self._recording = True

        self.vid_capture = None

        self.vid_attribute = None
        self.current_frame = None
        
        self.start_time = None
        self.end_time = None
        self.start_frame_num = 0

        self.init_connection(camera_index)

        self.video_frames = []
    
    def init_connection(self, camera_index=0):
        self.vid_capture = self.__open_camera(camera_index)
        if self.vid_capture is None:
            print('Warning: Please retry with other video sources')
        else:
            self.vid_attribute = {
                'width' : int(self.vid_capture.get(3)),
                'height' : int(self.vid_capture.get(4)),
                'fps' : self.vid_capture.get(5)
            }

    def __open_camera(self,camera_index,waiting=5):
        vid_capture = cv2.VideoCapture(camera_index)
        if vid_capture is None or not vid_capture.isOpened():
            print('Warning: unable to open video source: ', camera_index, " | waiting for", waiting, "second")
            time.sleep(0.8)
            waiting -= 1
            if waiting == 0:
                print('Warning: Returning None value')
                return None
            self.__open_camera(camera_index, waiting)
        else:
            return vid_capture
    
    def get_current_video_value(self):
        return self.current_frame, self.vid_attribute
    
    def get_total_frames(self):
        return len(self.video_frames)
    
    def get_record_time(self):
        return self.end_time - self.start_time
    
    def clear(self):
        self.video_frames = []

    def stream(self):
        while self._recording:
            ret, self.current_frame = self.vid_capture.read()
            if ret:
                # self.vid_recorder.write(self.current_frame)
                self.video_frames.append(self.current_frame)
            else:
                print('read done')
                break
    
    def record(self):
        self._recording = True
        if self.start_time is None:
            self.start_time = time.time()
        # video_thread = threading.Thread(target=self.__record)
        # video_thread.start()

    def stop(self):
        if self._recording:
            self._recording=False
            self.end_time = time.time()
            # self.vid_capture.release()
    
    def save(self, start_frame=0, end_frame=-1, file_name='temp', file_path='./'):
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")\
            .replace('/', '')\
            .replace(',', '_')\
            .replace(' ', '')\
            .replace(':', '')
        file_name = current_time + file_name
        if not('.mp4' in file_name):
            file_name = file_name+'.mp4'
        
        vid_cod = cv2.VideoWriter_fourcc(*'MPEG')
        vid_recorder = cv2.VideoWriter(file_path+file_name,
                                       vid_cod,
                                       self.vid_attribute['fps'],
                                       (self.vid_attribute['width'], self.vid_attribute['height']))
        
        for frame in self.video_frames[start_frame:end_frame]:
            vid_recorder.write(frame)
        
        vid_recorder.release()
        return file_path+file_name


class AudioRecorder():
    # Audio class based on pyAudio and Wave
    def __init__(self, dev_index=0):
        self.MIN = 200000 # sum of abs(MUTE) 211783
        self.MAX = 8000000 # 7889292

        self._recording = True
        self._mute = False
        self.current_frame = None
        
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        self.audio = pyaudio.PyAudio()

        dev_index = 0
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            # print(dev['name'], dev['hostApi'])
            if ( ( '마이크' in dev['name'] and 'USB' in dev['name']) and dev['hostApi'] == 0):
                dev_index = dev['index']
                print('dev_index', dev_index)

        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      input_device_index = dev_index,
                                      frames_per_buffer = self.frames_per_buffer)
        self.audio_frames = []

    # Audio starts being recorded
    def __record(self):
        self.stream.start_stream()
        while self._recording:
            data = self.stream.read(self.frames_per_buffer)
            if not self._mute:
                self.audio_frames.append(data)
            else:
                self.audio_frames.append(bytes(MUTE))

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