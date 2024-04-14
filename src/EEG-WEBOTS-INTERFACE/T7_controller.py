"""T7_controller controller."""
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from controller import Robot
from datetime import datetime
import math
import numpy as np
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import cortex
from cortex import Cortex

class LiveAdvance():
    def __init__(self, app_client_id, app_client_secret, robot, **kwargs):
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # # Robot Parameters
        self.robot = robot
        self.time_step = 32 # ms
        self.max_speed = 1  # m/s
 
        # Enable Motors
        self.left_motor = self.robot.getDevice('left wheel motor')
        self.right_motor = self.robot.getDevice('right wheel motor')
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)
        self.velocity_left = 0
        self.velocity_right = 0
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=False, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(query_profile_done=self.on_query_profile_done)
        self.c.bind(load_unload_profile_done=self.on_load_unload_profile_done)
        self.c.bind(save_profile_done=self.on_save_profile_done)
        self.c.bind(new_com_data=self.on_new_com_data)
        self.c.bind(get_mc_active_action_done=self.on_get_mc_active_action_done)
        self.c.bind(mc_action_sensitivity_done=self.on_mc_action_sensitivity_done)
        self.c.bind(inform_error=self.on_inform_error)

    def sim_check(self):
        if (self.robot.step(self.time_step) == -1):
            exit()

    def delay(self, time):
        i = 0
        while(i < time):
            self.sim_check()
            i = i + 1

    def start(self, profile_name, headsetId=''):
        if profile_name == '':
            raise ValueError('Empty profile_name. The profile_name cannot be empty.')

        self.profile_name = profile_name
        self.c.set_wanted_profile(profile_name)

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def load_profile(self, profile_name):
        self.c.setup_profile(profile_name, 'load')

    def unload_profile(self, profile_name):
        self.c.setup_profile(profile_name, 'unload')

    def save_profile(self, profile_name):
        self.c.setup_profile(profile_name, 'save')

    def subscribe_data(self, streams):
        self.c.sub_request(streams)

    def get_active_action(self, profile_name):
        self.c.get_mental_command_active_action(profile_name)

    def get_sensitivity(self, profile_name):
        self.c.get_mental_command_action_sensitivity(profile_name)

    def set_sensitivity(self, profile_name, values):
        self.c.set_mental_command_action_sensitivity(profile_name, values)

    # callbacks functions
    def on_create_session_done(self, *args, **kwargs):
        print('on_create_session_done')
        self.c.query_profile()

    def on_query_profile_done(self, *args, **kwargs):
        print('on_query_profile_done')
        self.profile_lists = kwargs.get('data')
        if self.profile_name in self.profile_lists:
            # the profile is existed
            self.c.get_current_profile()
        else:
            # create profile
            self.c.setup_profile(self.profile_name, 'create')

    def on_load_unload_profile_done(self, *args, **kwargs):
        is_loaded = kwargs.get('isLoaded')
        print("on_load_unload_profile_done: " + str(is_loaded))
        
        if is_loaded == True:
            # get active action
            self.get_active_action(self.profile_name)
        else:
            print('The profile ' + self.profile_name + ' is unloaded')
            self.profile_name = ''

    def on_save_profile_done (self, *args, **kwargs):
        print('Save profile ' + self.profile_name + " successfully")
        # subscribe mental command data
        stream = ['com']
        self.c.sub_request(stream)

    # This script interprets EEG commands to guide the movements of an 
    # E-Puck robot within the Webots simulation environment.
    def on_new_com_data(self, *args, **kwargs):
        
        # Check simulation status
        self.sim_check()
        
        # Extract action and power data from incoming headset packets
        data = kwargs.get('data')
        action = data['action']
        power = data['power']

        # Move forward if received command is 'neutral'
        if action == 'neutral':
            print("FORWARD  ", power)
            self.left_motor.setVelocity(3.0)
            self.right_motor.setVelocity(3.0)
            pass

        elif action == 'left':
            # Move left if received command is 'left' and the power level is below 0.7
            if power < 0.7:           
                print("LEFT     ", power)
                self.left_motor.setVelocity(-3.0)
                self.right_motor.setVelocity(3.0)   
                pass

            # Move right if received command is 'left' and the power level is above 0.7
            else:
                print("RIGHT    ", power)
                self.left_motor.setVelocity(3.0)
                self.right_motor.setVelocity(-3.0) 
                pass

    def on_get_mc_active_action_done(self, *args, **kwargs):
        data = kwargs.get('data')
        print('on_get_mc_active_action_done: {}'.format(data))
        self.get_sensitivity(self.profile_name)

    def on_mc_action_sensitivity_done(self, *args, **kwargs):
        data = kwargs.get('data')
        print('on_mc_action_sensitivity_done: {}'.format(data))
        if isinstance(data, list):
            # get sensivity
            new_values = [7,7,5,5]
            self.set_sensitivity(self.profile_name, new_values)
        else:
            # set sensitivity done -> save profile
            self.save_profile(self.profile_name)

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        error_code = error_data['code']
        error_message = error_data['message']

        print(error_data)

        if error_code == cortex.ERR_PROFILE_ACCESS_DENIED:
            # disconnect headset for next use
            print('Get error ' + error_message + ". Disconnect headset to fix this issue for next use.")
            self.c.disconnect_headset()


# -----------------------------------------------------------
# 
# GETTING STARTED
#   - Please reference to https://emotiv.gitbook.io/cortex-api/ first.
#   - Connect your headset with dongle or bluetooth. You can see the headset via Emotiv Launcher
#   - Please make sure the your_app_client_id and your_app_client_secret are set before starting running.
#   - The function on_create_session_done,  on_query_profile_done, on_load_unload_profile_done will help 
#          handle create and load an profile automatically . So you should not modify them
#   - After the profile is loaded. We test with some advanced BCI api such as: mentalCommandActiveAction, mentalCommandActionSensitivity..
#      But you can subscribe 'com' data to get live mental command data after the profile is loaded
# RESULT
#    you can run live mode with the trained profile. the data as below:
#    {'action': 'push', 'power': 0.85, 'time': 1647525819.0223}
#    {'action': 'pull', 'power': 0.55, 'time': 1647525819.1473}
# 
# -----------------------------------------------------------

def main():
    # Please fill your application clientId and clientSecret before running script
    your_app_client_id = 'app_client_id'
    your_app_client_secret = 'app_client_secret'
    trained_profile_name = 'profile_name'

    # Init live advance
    my_robot = Robot()
    l = LiveAdvance(your_app_client_id, your_app_client_secret, my_robot)# Added my_robot

    l.start(trained_profile_name)

if __name__ =='__main__':
    main()

# -----------------------------------------------------------