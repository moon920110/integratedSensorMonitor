import cv2
import numpy as np
from mss import mss

import pyaudio
import wave

import time
from datetime import datetime
import os

import threading

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

        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S").replace('/','').replace(',','_').replace(' ','').replace(':','')
        file_name = current_time + '_' + file_name
        if not('.mp4' in file_name):
            file_name = file_name+'.mp4'

        video_stream = ffmpeg.input(vid_file)
        audio_stream = ffmpeg.input(aud_file)
        stream = ffmpeg.output(audio_stream, video_stream, file_path+file_name).run()

        try:
            if os.path.exists(aud_file):
                os.remove(aud_file)

            if os.path.exists(vid_file):
                os.remove(vid_file)
        except:
            print('Fail to delete temp files')

class VideoRecorder():
    def __init__(self):
        self._recording = True

        self.monitor =  None
        self.current_frame = None

        self.sct = mss()

        self.start_time = None
        self.end_time = None

        self.monitors = self.sct.monitors

        self.video_frames = []

        self.select_screen_to_record()
        self.check_detected_monitors()
    
    def check_detected_monitors(self):
        print("Number of detected monitors:",len(self.monitors)-1)
        str_list = ["All :","Primary :","Secondary :","Tertiary :","Quaternary :","Quinary :","Senary :","Septenary :","Octonary :","Nonary :","Denary :"]
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
        return (self.current_frame, self.monitor)
    
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
        self._recording=True
        if self.start_time == None:
            self.start_time = time.time()
        video_thread = threading.Thread(target=self.__record)
        video_thread.start()

    def stop(self):
        if self._recording:
            self._recording=False
            self.end_time = time.time()
            # self.vid_capture.release()
    
    def save(self,start_frame=0, end_frame=-1, file_name='temp', file_path='./'):
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S").replace('/','').replace(',','_').replace(' ','').replace(':','')
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
        vid_recorder = cv2.VideoWriter(file_path+file_name, vid_cod, recorded_fps, (self.monitor['width'],self.monitor['height']))
        
        for frame in self.video_frames[start_frame:end_frame]:
            vid_recorder.write(frame)
        
        vid_recorder.release()
        return file_path+file_name

class AudioRecorder():
    # Audio class based on pyAudio and Wave
    def __init__(self, dev_index=0):
        self.MUTE = [293, 273, 273, 277, 249, 242, 215, 185, 214, 202, 199, 169, 198, 185, 133, 186, 206, 195, 151, 149, 200, 172, 194, 163, 109, 140, 125, 111, 67, 71, 64, 22, 25, 36, 43, 22, 12, -13, -8, -18, -38, -49, -70, -88, -110, -69, -92, -71, -86, -110, -121, -103, -85, -65, -35, -13, -31, -61, -24, 6, -9, -34, -43, -60, -51, -64, -36, -17, -12, -3, 25, 27, -18, 2, 19, 18, 20, 49, 42, 34, 44, 64, 59, 22, 88, 105, 92, 107, 58, 83, 73, 87, 94, 71, 81, 84, 120, 82, 115, 133, 135, 163, 144, 158, 165, 172, 189, 147, 199, 181, 171, 154, 137, 181, 154, 177, 209, 169, 170, 207, 207, 204, 228, 225, 212, 243, 293, 272, 250, 317, 290, 272, 303, 284, 280, 285, 284, 273, 299, 319, 298, 280, 288, 294, 275, 302, 288, 298, 262, 294, 301, 286, 291, 284, 267, 294, 256, 278, 311, 252, 282, 266, 285, 315, 275, 248, 270, 269, 254, 257, 285, 319, 287, 241, 272, 295, 272, 259, 217, 288, 337, 328, 313, 316, 312, 318, 313, 309, 291, 288, 287, 300, 319, 323, 322, 293, 286, 298, 304, 274, 292, 302, 287, 291, 285, 309, 326, 304, 320, 299, 303, 343, 323, 334, 311, 326, 289, 322, 326, 306, 325, 308, 330, 313, 313, 281, 303, 316, 323, 338, 315, 328, 310, 324, 331, 330, 325, 313, 366, 364, 351, 332, 326, 312, 305, 290, 260, 294, 309, 328, 321, 281, 292, 292, 278, 343, 331, 332, 329, 306, 318, 264, 282, 313, 265, 276, 280, 246, 279, 241, 224, 274, 277, 283, 256, 284, 311, 274, 266, 266, 228, 267, 234, 245, 233, 201, 206, 187, 238, 249, 238, 274, 273, 215, 228, 221, 216, 216, 201, 191, 181, 226, 172, 193, 209, 186, 235, 227, 202, 195, 232, 191, 179, 210, 241, 204, 202, 220, 215, 243, 254, 211, 220, 203, 223, 254, 255, 222, 222, 203, 194, 209, 207, 220, 181, 196, 216, 210, 199, 206, 172, 173, 161, 153, 122, 91, 112, 111, 115, 127, 116, 117, 152, 128, 140, 152, 131, 147, 184, 210, 154, 218, 200, 195, 227, 228, 213, 202, 256, 290, 289, 329, 313, 282, 322, 301, 325, 316, 320, 357, 344, 324, 324, 319, 328, 346, 354, 350, 319, 362, 364, 351, 318, 349, 348, 339, 352, 357, 371, 379, 338, 376, 410, 404, 351, 385, 385, 355, 347, 282, 312, 248, 269, 253, 283, 297, 273, 293, 262, 297, 244, 247, 267, 255, 292, 298, 254, 257, 274, 271, 264, 2929, 223, 230, 212, 183, 194, 199, 219, 179, 148, 146, 126, 131, 99, 105, 144, 159, 144, 125, 150, 136, 171, 175, 159, 184, 179, 193, 150, 144, 121, 157, 110, 96, 78, 79, 109, 82, 90, 106, 126, 97, 80, 107, 111, 78, 44, 35, 60, 51, 28, 49, 13, 5, 29, 5, 13, -31, 40, 68, 46, 83, 63, 50, 50, 33, 54, 93, 108, 82, 92, 66, 87, 112, 108, 116, 99, 64, 95, 71, 72, 77, 71, 71, 59, 54, 10, 60, 38, 39, 68, 46, 80, 81, 75, 101, 113, 116, 145, 133, 180, 151, 151, 210, 178, 199, 212, 199, 161, 228, 258, 214, 237, 221, 246, 246, 245, 262, 324, 314, 288, 294, 274, 301, 286, 292, 282, 313, 332, 362, 341, 305, 348, 364, 388, 364, 361, 413, 419, 403, 420, 441, 429, 411, 446, 413, 399, 364, 413, 418, 396, 405, 424, 418, 386, 426, 394, 394, 393, 398, 372, 332, 328, 366, 389, 386, 393, 388, 362, 391, 385, 349, 356, 381, 371, 381, 377, 372, 371, 350, 340, 343, 380, 363, 391, 388, 384, 384, 384, 379, 392, 388, 363, 390, 401, 387, 381, 381, 359, 363, 356, 368, 409, 387, 422, 426, 389, 425, 381, 365, 385, 358, 331, 355, 328, 330, 347, 338, 364, 363, 382, 387, 384, 375, 407, 377, 365, 372, 371, 398, 378, 414, 452, 440, 405, 387, 401, 414, 400, 430, 421, 431, 438, 419, 418, 433, 433, 434, 441, 423, 456, 424, 378, 398, 408, 380, 412, 416, 405, 411, 413, 369, 362, 342, 327, 339, 371, 361, 336, 347, 333, 351, 349, 333, 317, 284, 318, 293, 273, 304, 266, 256, 252, 231, 197, 224, 234, 235, 262, 262, 246, 203, 202, 183, 190, 186, 169, 191, 190, 170, 200, 206, 187, 179, 198, 201, 185, 170, 187, 197, 150, 174, 190, 161, 145, 146, 124, 132, 144, 103, 97, 92, 89, 87, 55, 46, 37, 48, -5, 16, -1, -39, -18, -49, -49, -96, -92, -83, -111, -108, -102, -136, -131, -100, -119, -89, -98, -45, -26, -33, 5, 37, 10, 5, 39, 13, 54, 64, 78, 70, 55, 85, 62, 115, 159, 177, 154, 170, 152, 164, 191, 166, 201, 170, 157, 181, 175, 183, 191, 155, 138, 166, 175, 124, 121, 84, 113, 130, 115, 126, 163, 154, 175, 177, 162, 199, 195, 221, 228, 249, 239, 241, 225, 227, 253, 216, 246, 264, 278, 292, 276, 244, 262, 280, 281, 270, 249, 271, 291, 308, 238, 213, 268, 286, 224, 221, 240, 259, 250, 214, 223, 200, 204, 198, 200, 215, 208, 219, 162, 200, 193, 173, 171, 191, 184, 159, 177, 159, 148, 155, 194, 140, 162, 168, 175, 230, 186, 161, 151, 121, 109, 100, 140, 109, 104, 104, 79, 113, 109, 45, 42, 67, 75, 37, 36, 93, 42, 23, 62, 64, 91, 91, 60, 95, 59, 78, 98, 85, 84, 115, 109, 96, 61, 77, 90, 72, 98, 107, 82, 91, 74, 56, 73, 63, 54, 69, 36, 57, 48, -33, 3, -23, 22, 18, 19, 28, -12, 21, 50, 62, 50, 84, 84, 70, 91, 41, 57, 91, 73, 70, 57, 59, 80, 77, 53, 52, 79, 50, 66, 96, 80, 112, 100, 93, 112, 148, 109, 156, 185, 161, 161, 181, 175, 161, 193]
        self.MIN = 200000 # sum of abs(self.MUTE) 211783
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
            if ( ( '믹스' in dev['name'] or 'Stereo Mix' in dev['name']) and dev['hostApi'] == 0):
                dev_index = dev['index']
                print('dev_index', dev_index)
                break

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
                self.audio_frames.append(bytes(self.MUTE))

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
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S").replace('/','').replace(',','_').replace(' ','').replace(':','')
        file_name = current_time + file_name
        if not('.wav' in file_name):
            file_name = file_name+'.wav'
        
        waveFile = wave.open(file_path+file_name, 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.audio.get_sample_size(self.format))
        waveFile.setframerate(self.rate)
        waveFile.writeframes(b''.join(self.audio_frames[start_frame:end_frame]))
        waveFile.close()

        return file_path+file_name