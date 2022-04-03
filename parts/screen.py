import os
import cv2
import numpy as np
from mss import mss
import time
from datetime import datetime
import threading

from common.video_audio_util import AudioRecorder

# ffmpeg프로그램을 따로 설치해줘야 함
# IMPORTANT: windows는 https://www.wikihow.com/Install-FFmpeg-on-Windows 따라 ffmpeg프로그램 설치
# IMPORTANT: ubuntu는 apt-get install ffmpeg
import ffmpeg

# IMPORTANT: stereo mixer가 enable 되어 있어야 시스템 소리 녹음 가능
# IMPORTANT: windows는 https://m.blog.naver.com/PostView.naver?isHttpsRedirect=true&blogId=yun__dodo&logNo=221470090523 따라 설치
# IMPORTANT: ubuntu는 WIP


class ScreenRecorder:
    def __init__(self, monitor_num, left, top, width, height):
        self._video_recorder = VideoRecorderForScreen()
        self._audio_recorder = AudioRecorder(device_name=['믹스', 'Stereo Mix'])

        self.monitor_num = monitor_num
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        self.recording = False

    def stream(self):
        self._audio_recorder.stream_audio()
        self._video_recorder.stream_video()
    
    def record(self):
        self.recording = True
        self._audio_recorder.record()
        self._video_recorder.record()

    def stop_record(self):
        self.recording = False
        self._audio_recorder.stop()
        self._video_recorder.stop()

    def clear(self):
        self._video_recorder.clear()
        self._audio_recorder.clear()

    def get_current_video_value(self):
        return self._video_recorder.get_current_video_value()

    def get_current_audio_value(self):
        return self._audio_recorder.get_current_audio_value()

    def ready(self):
        self._audio_recorder.connect()
        self._video_recorder.connect(self.monitor_num,
                                        left=self.left,
                                        top=self.top,
                                        width=self.width,
                                        height=self.height)
        time.sleep(0.1)

    def save_data(self, file_path='./'):
        print("Saving screen")
        if self.recording:
            self.stop_record()
        file_name = 'screen'
        vid_file = self._video_recorder.save(file_path)
        aud_file = self._audio_recorder.save(file_path)

        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")\
            .replace('/', '')\
            .replace(',', '_')\
            .replace(' ', '')\
            .replace(':', '')
        file_name = current_time + '_' + file_name
        if not('.mp4' in file_name):
            file_name = file_name+'.mp4'

        video_stream = ffmpeg.input(vid_file)
        audio_stream = ffmpeg.input(aud_file)
        try:
            stream = ffmpeg.output(audio_stream, video_stream, os.path.join(file_path, file_name)).run()
            try:
                if os.path.exists(aud_file):
                    os.remove(aud_file)

                if os.path.exists(vid_file):
                    os.remove(vid_file)
            except:
                print('Fail to delete temp files')
        except:
            print('Failed to mix video and audio')

        print("Screen is saved")
        self.clear()

    def terminate(self):
        print("terminating screen")
        self._audio_recorder.terminate()
        self._video_recorder.terminate()
        print("screen is terminated")


class VideoRecorderForScreen:
    def __init__(self):
        self._recording = False
        self._terminate = False

        self.monitor = None
        self.current_frame = None

        self.start_time = None
        self.end_time = None
        self.start_frame = None
        self.end_frame = None
        
        self.sct = mss()
        self.monitors = self.sct.monitors

        self.video_thread = None
        self.video_frames = []

    def connect(self,monitor_number=0, **kwargs):
        self.check_detected_monitors()
        self.select_screen_to_record(monitor_number=monitor_number, **kwargs)

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
            self.video_frames = np.empty((1, self.monitor['height'], self.monitor['width'], 3), dtype=np.uint8)
        else:
            self.video_frames = np.empty((1, kwargs['height'], kwargs['width'], 3), dtype=np.uint8)
            self.monitor = self.monitors[monitor_number]
            for key in ['left', 'top']:
                self.monitor[key] = self.monitor[key] + kwargs[key]

            for key in ['width', 'height']:
                self.monitor[key] = kwargs[key]

    def get_current_video_value(self):
        return self.current_frame, self.monitor

    def get_record_time(self):
        return self.end_time - self.start_time

    def clear(self):
        self.video_frames = []
    
    def record(self):
        self._recording = True
        self.start_frame = len(self.video_frames)

    def __stream(self):
        while not self._terminate:
            if self._recording:
                self.current_frame = np.array(self.sct.grab(self.monitor), dtype=np.uint8)[:, :, :3]
                self.current_frame = np.expand_dims(self.current_frame, 0)
                self.video_frames = np.append(self.video_frames, self.current_frame, axis=0)

            # if self.current_frame != None:
            #     self.vid_recorder.write(self.current_frame)
            # else:
            #     print('read done')
            #     break

    def stream_video(self):
        if self.start_time is None:
            self.start_time = time.time()

        self.video_thread = threading.Thread(target=self.__stream)
        self.video_thread.start()

    def stop(self):
        if self._recording:
            self._recording = False
            self.end_time = time.time()
            self.end_frame = len(self.video_frames)

    def terminate(self):
        self._terminate = True
        self.video_thread.join()

    def save(self, file_path):
        file_name = 'screen_video_temp'
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")\
            .replace('/', '')\
            .replace(',', '_')\
            .replace(' ', '')\
            .replace(':', '')
        file_name = current_time + file_name
        if not('.mp4' in file_name):
            file_name = file_name+'.mp4'

        frame_counts = len(self.video_frames)
        elapsed_time = self.get_record_time()
        recorded_fps = frame_counts / elapsed_time
        # print("total frames " + str(frame_counts))
        # print("elapsed time " + str(elapsed_time))
        # print("recorded fps " + str(recorded_fps))

        vid_cod = cv2.VideoWriter_fourcc(*'MPEG')
        vid_recorder = cv2.VideoWriter(os.path.join(file_path, file_name),
                                       vid_cod,
                                       recorded_fps,
                                       (self.monitor['width'], self.monitor['height']))

        for frame in self.video_frames[self.start_frame:self.end_frame]:
            vid_recorder.write(frame)

        vid_recorder.release()
        return os.path.join(file_path, file_name)
