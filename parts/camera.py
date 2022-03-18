# VScode issue
import sys
sys.path.append(".")

import os
import cv2
import numpy as np
import time

from datetime import datetime
import threading

from const.const import *
from common.video_audio_util import AudioRecorder

# IMPORTANT: windows는 https://www.wikihow.com/Install-FFmpeg-on-Windows따라 ffmpeg프로그램 설치
# IMPORTANT: ubuntu 는 apt-get install ffmpeg
import ffmpeg


# TODO: Add caption for each attribute
class WebcamRecorder:
    def __init__(self, camera_index=0):
        self._video_recorder = VideoRecorderForCamera(camera_index)
        self._audio_recorder = AudioRecorder(device_name=['마이크','USB'])
        
    def ready(self):
        self._audio_recorder.connect()
        self._video_recorder.connect()
        time.sleep(0.1)

    def stream(self):
        self._audio_recorder._recording = True
        self._video_recorder._recording = True
        self._audio_recorder.record()
        self._video_recorder.record()
    
    def record(self):
        self._audio_recorder.count()
        self._video_recorder.count()
    
    def stop_record(self):
        self._audio_recorder.stop()
        self._video_recorder.stop()
    
    def clear(self):
        self._video_recorder.clear()
        self._audio_recorder.clear()

    def get_current_video_value(self):
        return self._video_recorder.get_current_video_value()
    
    def get_current_audio_value(self):
        return self._audio_recorder.get_current_audio_value()
    
    def save_data(self, file_path='./', video_offset=0, audio_offset=30, file_name='camera'):
        self.stop_record()
        if not '/' in file_path[-1]:
            file_path = file_path+'/'
        vid_file = self._video_recorder.save(video_offset, file_name='camera_vid_tmp', file_path=file_path)
        aud_file = self._audio_recorder.save(audio_offset, file_name='camera_aud_tmp', file_path=file_path)

        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S").replace('/','').replace(',','_').replace(' ','').replace(':','')
        file_name = current_time + '_' + file_name
        if not('.mp4' in file_name):
            file_name = file_name+'.mp4'

        video_stream = ffmpeg.input(vid_file)
        audio_stream = ffmpeg.input(aud_file)
        stream = ffmpeg.output(audio_stream, video_stream, file_name).run()
        
        try:
            if os.path.exists(aud_file):
                os.remove(aud_file)
        
            if os.path.exists(vid_file):
                os.remove(vid_file)
        except:
            print('Fail to delete temp files')


class VideoRecorderForCamera:
    def __init__(self, camera_index=0):
        self._recording = True

        self.vid_capture = None

        self.vid_attribute = None
        self.current_frame = None
        
        self.start_time = None
        self.end_time = None
        self.start_frame_num = 0

        self.camera_index = camera_index

        self.video_frames = []
        self.flag = 0
        self.cnt = 0
    
    def connect(self):
        self.vid_capture = self.__open_camera(self.camera_index)
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
    
    def __record(self):
        while self._recording:
            ret, self.current_frame = self.vid_capture.read()
            if ret:
                # self.vid_recorder.write(self.current_frame)
                self.video_frames.append(self.current_frame)
                self.cnt = self.cnt+1
            else:
                print('read done')
                break
    
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
    
    def count(self):
        self.flag = self.cnt
        self.cnt = 0
    
    def save(self, start_frame=0, file_name='temp', file_path='./'):
        start_frame = start_frame + self.flag
        end_frame = -1
        # end_frame = self.flag + self.cnt
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