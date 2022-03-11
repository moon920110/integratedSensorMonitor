import datetime
import random


def keyboardMarker(key):
    from pynput.keyboard import Controller, Key
    keyboard = Controller()
    keyboard.press(Key.alt)
    keyboard.press(key)
    keyboard.release(key)
    keyboard.release(Key.alt)


def generate_datetime():
    from datetime import datetime, timedelta
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    start = datetime(2020, 1, 1, 00, 00, 00)
    end = start + timedelta(days=365)
    result = start + (end - start) * random.random()
    birth = str(result).split(' ')[0]
    year, month, day = birth.split('-')

    return year, month, day


def formatting_filename(video, username):
    nowtime = datetime.datetime.now()
    print(nowtime)
    date, time = str(nowtime).split(' ')
    times = str(time).split('.')[0]
    times = times.replace(':', '-')
    filename = '_'.join([date, times, video, username])
    return filename

def marking_time():
    pass

"""
TEST
format example : 2020-04-02 V1 USER
"""
# print(formatting_filename('V1', '김주영'))

# formatting_filename('V1', '김주영')    # 2021-03-18 VIDEO PNAME
