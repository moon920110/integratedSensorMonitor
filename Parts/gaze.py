import tobii_research as tr
import time
from datetime import datetime
from tkinter import Tk, PhotoImage

# class Gaze():
#     def __init__(self,):
        

class Tobii():
    def __init__(self,):
        self.found_eyetrackers = tr.find_all_eyetrackers()
        self.my_eyetracker = self.found_eyetrackers[0]
        self.address = self.my_eyetracker.address
        self.model = self.my_eyetracker.model
        self.device_name = self.my_eyetracker.device_name
        self.serial_number = self.my_eyetracker.serial_number
        
        self.gaze_data = {}
        
    def gaze_data_callback(self, gaze_data):
        # Print gaze points of left and right eye
#         self.gaze_data = gaze_data
        self.gaze_time = datetime.now()
        self.gaze_left = gaze_data['left_gaze_point_on_display_area']
        self.gaze_right = gaze_data['right_gaze_point_on_display_area']
        
        print("Date: ({date_time}) \t Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
            date_time = self.gaze_time,
            gaze_left_eye = self.gaze_left,
            gaze_right_eye = self.gaze_right))
        
        self.gaze_data[len(self.gaze_data)] = {'time':self.gaze_time, 'left':self.gaze_left, 
                                               'right':self.gaze_right}
        time.sleep(5)
        
    def subscribe(self,):
        self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary=True)
    
    def unsubscribe(self,):
        self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback)
    
    def calibration(self,):
        if self.my_eyetracker is None:
            return

        calibration = tr.ScreenBasedCalibration(self.my_eyetracker)

        calibration.enter_calibration_mode()
        print("Entered calibration mode for eye tracker with serial number {0}.".format(self.serial_number))
        points_to_calibrate = [(0.5, 0.5), (0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9)]

        for point in points_to_calibrate:
            print("Show a point on screen at {0}.".format(point))

            time.sleep(5)

            print("Collecting data at {0}.".format(point))
            if calibration.collect_data(point[0], point[1]) != tr.CALIBRATION_STATUS_SUCCESS:
                calibration.collect_data(point[0], point[1])

            print("Computing and applying calibration.")
            calibration_result = calibration.compute_and_apply()
            print("Compute and apply returned {0} and collected at {1} points.".format(calibration_result.status, len(calibration_result.calibration_points)))

            recalibrate_point = (0.1, 0.1)
            print("Removing calibration point at {0}.".format(recalibrate_point))
            print("Show a point on screen at {0}.".format(recalibrate_point))
            calibration.collect_data(recalibrate_point[0], recalibrate_point[1])

            print("Computing and applying calibration.")
            calibration_result = calibration.compute_and_apply()
            print("Compute and apply returned {0} and collected at {1} points.".format(calibration_result.status, len(calibration_result.calibration_points)))

            calibration.leave_calibration_mode()
            print("Left calibration mode.")
            
            
    ## eye_images 따로 나오진 않음
    def eye_image_callback(self, ey_image_data):
        print("System time: {0}, Device time {1}, Camera id {2}".format(eye_image_data['system_time_stamp'],
                                                                         eye_image_data['device_time_stamp'],
                                                                         eye_image_data['camera_id']))
        image = PhotoImage(data=base64.standard_b64encode(eye_image_data['image_data']))
        print("{0} width {1}, height {2}".format(image, image.width(), image.height()))

    def eye_image(self,):
        root = Tk()
        print("Subscribing to eye images for eye tracker with serial number {0}.".format(self.serial_number))
        eyetracker.subscribe_to(tr.EYETRACKER_EYE_IMAGES, eye_image_callback, as_dictionary=True)

        time.sleep(5)
        eyetracker.unsubscribe_from(tr.EYETRACKER_EYE_IMAGES, eye_image_callback)
        print("Unsubscribed from eye images.")
        root.destroy()
        
    def display_area(self,):
        display_area = self.my_eyetracker.get_display_area()

        print("Got display area from tracker with serial number {0}:".format(self.serial_number))

        print("Bottom Left: {0}".format(display_area.bottom_left))
        print("Bottom Right: {0}".format(display_area.bottom_right))
        print("Height: {0}".format(display_area.height))
        print("Top Left: {0}".format(display_area.top_left))
        print("Top Right: {0}".format(display_area.top_right))
        print("Width: {0}".format(display_area.width))

        new_display_area_dict = dict()
        new_display_area_dict['top_left'] = display_area.top_left
        new_display_area_dict['top_right'] = display_area.top_right
        new_display_area_dict['bottom_left'] = display_area.bottom_left

        new_display_area = tr.DisplayArea(new_display_area_dict)
        self.my_eyetracker.set_display_area(new_display_area)
    
#     def get_track_box(self,):
#         track_box = self.my_eyetracker.get_track_box()
#         print("Got track box from tracker with serial number {0} with corners:".format(self.serial_number))

#         print("Back Lower Left: {0}".format(track_box.back_lower_left))
#         print("Back Lower Right: {0}".format(track_box.back_lower_right))
#         print("Back Upper Left: {0}".format(track_box.back_upper_left))
#         print("Back Upper Right: {0}".format(track_box.back_upper_right))

#         print("Front Lower Left: {0}".format(track_box.front_lower_left))
#         print("Front Lower Right: {0}".format(track_box.front_lower_right))
#         print("Front Upper Left: {0}".format(track_box.front_upper_left))
#         print("Front Upper Right: {0}".format(track_box.front_upper_right))


def main():
    tobii = Tobii()
    calibration_result = tobii.calibration()
    if calibration_result.status == 'calibration_status_failure':
        calibration_result = tobii.calibration()
    
    tobii.subscribe()
    time.sleep(10)
    tobii.unsubscribe()

    
if __name__ == "__main__":
	main()