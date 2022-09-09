from __future__ import print_function

import odrive
from odrive.enums import *
import time
import math
#import keyboard
from inputs import get_gamepad
import threading

class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):

        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()


    def read(self): # return the buttons/triggers that you care about in this methode
        x = self.LeftJoystickX
        y = self.LeftJoystickY
        a = self.A
        xb = self.X
        return [x, y, a, xb]


    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.X = event.state
                elif event.code == 'BTN_WEST':
                    self.Y = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state



# Find a connected ODrive (this will block until you connect one)
print("finding an odrive...")
my_drive = odrive.find_any()

# Calibrate motor and wait for it to finish
print("starting calibration...")
my_drive.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
my_drive.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
while my_drive.axis0.current_state != AXIS_STATE_IDLE and my_drive.axis1.current_state != AXIS_STATE_IDLE:
    time.sleep(0.1)

my_drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
my_drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

# To read a value, simply read the property
print("Bus voltage is " + str(my_drive.vbus_voltage) + "V")

# Or to change a value, just assign to the property
my_drive.axis0.controller.input_pos = 3.14
print("Position setpoint is " + str(my_drive.axis0.controller.pos_setpoint))

# And this is how function calls are done:
for i in [1,2,3,4]:
    print('voltage on GPIO{} is {} Volt'.format(i, my_drive.get_adc_voltage(i)))

print('Ready for Motion')
curr_speed = 5      # max speed
idle_thresh = .1   # threshold for ADC when controller stick is idle
joy = XboxController()
while True:
    joyPos = joy.read()

    if joyPos[3] == 0 and joyPos[1] > idle_thresh or joyPos[1] < -idle_thresh: # Forward and backward speeds
        my_drive.axis0.controller.input_vel = joyPos[1] * curr_speed
        my_drive.axis1.controller.input_vel = joyPos[1] * -curr_speed
    elif joyPos[3] == 1 and joyPos[0] > idle_thresh or joyPos[0] < -idle_thresh: # Turning control
        my_drive.axis0.controller.input_vel = joyPos[0] * curr_speed
        my_drive.axis1.controller.input_vel = joyPos[0] * curr_speed
    else:
        my_drive.axis0.controller.input_vel = 0
        my_drive.axis1.controller.input_vel = 0
    
    if joyPos[2] == 1: # break if A button is pressed
        break
    
    #event = keyboard.read_event()
    #if event.event_type == keyboard.KEY_DOWN and event.name == 'esc':
    #    break
    #elif event.event_type == keyboard.KEY_DOWN and event.name == 'w':
    #    my_drive.axis0.controller.input_vel = -curr_speed
    #    my_drive.axis1.controller.input_vel = curr_speed
    #elif event.event_type == keyboard.KEY_DOWN and event.name == 's':
    #    my_drive.axis0.controller.input_vel = curr_speed
    #    my_drive.axis1.controller.input_vel = -curr_speed
    #elif event.event_type == keyboard.KEY_DOWN and event.name == 'a':
    #    my_drive.axis0.controller.input_vel = -curr_speed
    #    my_drive.axis1.controller.input_vel = -curr_speed
    #elif event.event_type == keyboard.KEY_DOWN and event.name == 'd':
    #    my_drive.axis0.controller.input_vel = curr_speed
    #    my_drive.axis1.controller.input_vel = curr_speed
    #else:
    #    my_drive.axis0.controller.input_vel = 0
    #    my_drive.axis1.controller.input_vel = 0
    
    
# Cleanup
my_drive.axis0.controller.input_vel = 0
my_drive.axis1.controller.input_vel = 0

my_drive.axis0.requested_state = AXIS_STATE_IDLE
my_drive.axis1.requested_state = AXIS_STATE_IDLE
