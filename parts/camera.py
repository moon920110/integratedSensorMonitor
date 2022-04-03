import os
import cv2
import numpy as np
import time

from datetime import datetime
import threading

from common.video_audio_util import AudioRecorder

# IMPORTANT: windows는 https://www.wikihow.com/Install-FFmpeg-on-Windows따라 ffmpeg프로그램 설치
# IMPORTANT: ubuntu 는 apt-get install ffmpeg
import ffmpeg


class WebcamRecorder:
    def __init__(self, camera_index=0):
        self._video_recorder = VideoRecorderForCamera(camera_index)
        self._audio_recorder = AudioRecorder(device_name=['마이크', 'USB'])
        self.recording = False
        
    def ready(self):
        self._audio_recorder.connect()
        self._video_recorder.connect()
        time.sleep(0.1)

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
    
    def save_data(self, file_path):
        print("Saving camera")
        if self.recording:
            self.stop_record()
        file_name = 'camera'
        vid_file, fps = self._video_recorder.save(file_path)
        aud_file = self._audio_recorder.save(file_path, fps)

        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")\
            .replace('/', '').replace(',', '_').replace(' ', '').replace(':', '')
        file_name = current_time + '_' + file_name
        if not('.mp4' in file_name):
            file_name = file_name+'.mp4'

        video_stream = ffmpeg.input(vid_file)
        audio_stream = ffmpeg.input(aud_file)

        try:
            stream_for_debug = ffmpeg.output(audio_stream, video_stream, os.path.join(file_path, file_name)).run()
            try:
                if os.path.exists(aud_file):
                    os.remove(aud_file)

                if os.path.exists(vid_file):
                    os.remove(vid_file)
            except:
                print('Fail to delete temp files')
        except:
            print("Failed to mix video and audio")
        

        print("Camera is saved")
        self.clear()

    def terminate(self):
        print('terminating camera')
        self._video_recorder.terminate()
        self._audio_recorder.terminate()
        print('camera is terminated')


class VideoRecorderForCamera:
    def __init__(self, camera_index=0):
        self._recording = False
        self._terminate = False

        self.video_thread = None
        self.vid_capture = None

        self.vid_attribute = None
        self.current_frame = None
        
        self.start_time = None
        self.end_time = None
        self.start_frame = None
        self.end_frame = None

        self.camera_index = camera_index

        self.video_frames = []

    def connect(self):
        self.vid_capture = self.__open_camera(self.camera_index)
        if self.vid_capture is None:
            print('Warning: Please retry with other video sources')
        else:
            self.vid_attribute = {
                'width': int(self.vid_capture.get(3)),
                'height': int(self.vid_capture.get(4)),
                'fps': self.vid_capture.get(5)
            }
            self.video_frames = np.empty((1, self.vid_attribute['height'], self.vid_attribute['width'], 3),
                                         dtype= np.uint8)
    
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

    def get_record_time(self):
        return self.end_time - self.start_time
    
    def clear(self):
        self.video_frames = np.empty((1, self.vid_attribute['height'], self.vid_attribute['width'], 3),
                                         dtype= np.uint8)
    
    def __stream(self):
        while not self._terminate:
            if self._recording:
                ret, self.current_frame = self.vid_capture.read()
                if ret:
                    self.current_frame = np.expand_dims(self.current_frame, 0).astype(np.uint8)
                    self.video_frames = np.append(self.video_frames, self.current_frame, axis=0)
                else:
                    print('read done')
                    break

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
        self.vid_capture.release()

    def record(self):
        self._recording = True
        self.start_frame = len(self.video_frames)

    def save(self, file_path='./'):
        file_name = 'camera_video_temp'
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
        print('elapsed_time', elapsed_time)
        print('recorded_fps', recorded_fps)
        if ((self.vid_attribute['fps'] * 2 ) + 5) > recorded_fps:
            print('webcam recorded fps is', recorded_fps)
            recorded_fps = recorded_fps * 2

        vid_cod = cv2.VideoWriter_fourcc(*'MPEG')
        vid_recorder = cv2.VideoWriter(os.path.join(file_path, file_name),
                                       vid_cod,
                                       recorded_fps,
                                       (self.vid_attribute['width'], self.vid_attribute['height']))
        
        for frame in self.video_frames[self.start_frame:self.end_frame]:
            vid_recorder.write(frame)
        
        vid_recorder.release()
        return os.path.join(file_path, file_name), recorded_fps
