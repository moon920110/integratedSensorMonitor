import cv2
import numpy as np
from mss import mss
import pyaudio
import wave
import time
from datetime import datetime
import threading

from const.const import *

# ffmpeg프로그램을 따로 설치해줘야 함
# IMPORTANT: windows는 https://www.wikihow.com/Install-FFmpeg-on-Windows 따라 ffmpeg프로그램 설치
# IMPORTANT: ubuntu는 apt-get install ffmpeg
import ffmpeg

# IMPORTANT: stereo mixer가 enable 되어 있어야 시스템 소리 녹음 가능
# IMPORTANT: windows는 https://m.blog.naver.com/PostView.naver?isHttpsRedirect=true&blogId=yun__dodo&logNo=221470090523 따라 설치
# IMPORTANT: ubuntu는 WIP


# TODO: Add caption for each attribute
# TODO: refactoring
class ScreenRecorder:
    def __init__(self):
        self._video_recorder = VideoRecorder()
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

    def select_screen_to_record(self, monitor_number=0, **kwargs):
        self._video_recorder.select_screen_to_record(monitor_number, **kwargs)

    def save(self,start_frame=0, end_frame=-1, video_offset=0, audio_offset=0, file_name='None', file_path='./'):
        vid_file = self._video_recorder.save(start_frame + video_offset, end_frame)
        aud_file = self._audio_recorder.save(start_frame + audio_offset, end_frame)

        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")\
            .replace('/', '')\
            .replace(',', '_')\
            .replace(' ', '')\
            .replace(':', '')
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


class VideoRecorder():
    def __init__(self):
        self._recording = True

        self.monitor = None
        self.current_frame = None

        self.sct = mss()

        self.start_time = None
        self.end_time = None

        self.monitors = self.sct.monitors

        self.video_frames = []

        self.select_screen_to_record()
        self.check_detected_monitors()

    def check_detected_monitors(self):
        print("Number of detected monitors:", len(self.monitors)-1)
        str_list = ["All :", "Primary :", "Secondary :", "Tertiary :", "Quaternary :", "Quinary :",
                    "Senary :", "Septenary :", "Octonary :", "Nonary :", "Denary :"]
        for i in range(len(self.monitors)):
            print(str_list[i], self.monitors[i])
        return self.monitors

    def select_screen_to_record(self, monitor_number=0, **kwargs):
        if monitor_number == 0:
            self.monitor = self.monitors[monitor_number]
        else:
            self.monitor = self.monitors[monitor_number]
            for key in ['left','top']:
                self.monitor[key] = self.monitor[key] + kwargs[key]

            for key in ['width','height']:
                self.monitor[key] = kwargs[key]

    def get_current_video_value(self):
        return self.current_frame, self.monitor

    def get_total_frames(self):
        return len(self.video_frames)

    def get_record_time(self):
        return self.end_time - self.start_time

    def clear(self):
        self.video_frames = []

    def __record(self):
        while self._recording:
            self.current_frame = np.array(self.sct.grab(self.monitor))[:, :, :3]
            self.video_frames.append(self.current_frame)

            # if self.current_frame != None:
            #     self.vid_recorder.write(self.current_frame)
            # else:
            #     print('read done')
            #     break

    def record(self):
        self._recording = True
        if self.start_time is None:
            self.start_time = time.time()
        video_thread = threading.Thread(target=self.__record)
        video_thread.start()

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

        frame_counts = self.get_total_frames()
        elapsed_time = self.get_record_time()
        recorded_fps = frame_counts / elapsed_time
        print("total frames " + str(frame_counts))
        print("elapsed time " + str(elapsed_time))
        print("recorded fps " + str(recorded_fps))

        vid_cod = cv2.VideoWriter_fourcc(*'MPEG')
        vid_recorder = cv2.VideoWriter(file_path+file_name,
                                       vid_cod,
                                       recorded_fps,
                                       (self.monitor['width'], self.monitor['height']))

        for frame in self.video_frames[start_frame:end_frame]:
            vid_recorder.write(frame)

        vid_recorder.release()
        return file_path+file_name


class AudioRecorder():
    # Audio class based on pyAudio and Wave
    def __init__(self, dev_index=0):
        self.MIN = 200000  # sum of abs(MUTE) 211783
        self.MAX = 8000000  # 7889292

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
            if ( ( '믹스' in dev['name'] or 'Stereo Mix' in dev['name']) and dev['hostApi'] == 0):
                dev_index = dev['index']
                print('dev_index', dev_index)
                break

        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      input_device_index=dev_index,
                                      frames_per_buffer=self.frames_per_buffer)

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
