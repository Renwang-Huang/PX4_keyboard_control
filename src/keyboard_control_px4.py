#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bug report

# File "/home/renwang/Aether-Sim/src/simulation/scripts/keyboard_control_px4.py", line 95
# SyntaxError: Non-ASCII character '\xe7' keyboard_control_px4.py on line 95, but no encoding declared

# upgrade code:
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
import sys, select, termios, tty
import rospy
from mavros_msgs.msg import OverrideRCIn, State
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import Imu, NavSatFix
from std_msgs.msg import Float32, String
import time
import math

msg = """
#####################################################
If you use this script, please read readme.md first.
dir:some/src/simulation/scripts/README.md
#####################################################

********************
action_control
********************

---------------------------
        e    
   s    d    f

e and d : pitch control
s and f : roll control
---------------------------
        i    
   j    k    l

i and k : throttle control
j and l : yaw control
---------------------------
g : Speed reduction
h : Speed increase
---------------------------

*********************
flight_mode_control
*********************

---------------------------
0 : ARM
1 : TAKEOFF
2 : OFFBOARDS
3 : LAND
4 : POSCTL
5 : ATTITCTL
6 : MISSION
---------------------------

CTRL+C to quit

"""
speed_control = 1850
cur_target_rc_yaw = OverrideRCIn()
mavros_state = State()
armServer = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
setModeServer = rospy.ServiceProxy('/mavros/set_mode', SetMode)
local_target_pub = rospy.Publisher('/mavros/rc/override', OverrideRCIn, queue_size=100)

def __init__():
	rospy.init_node('PX4_keyboard_control')
	rospy.Subscriber("/mavros/state", State, mavros_state_callback)
	print("Initialized")

def RCInOverride(channel0,channel1,channel2,channel3):
	target_RC_yaw = OverrideRCIn()
	target_RC_yaw.channels[0] = channel0
	target_RC_yaw.channels[1] = channel1
	target_RC_yaw.channels[2] = channel2
	target_RC_yaw.channels[3] = channel3
	target_RC_yaw.channels[4] = 1100
	return target_RC_yaw

def mavros_state_callback(msg):
	global mavros_state
	mavros_state = msg

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

# 7种飞行模式对应的数字输入
def command_control():
	if key == '0':
		if armServer(True) :
			print("Vehicle arming succeed!")
		else:
			print("Vehicle arming failed!")
	elif key == '1':
		if setModeServer(custom_mode='AUTO.TAKEOFF'):
			print("Vehicle takeoff succeed!")
		else:
			print("Vehicle takeoff failed!")
	elif key == '2':
		if setModeServer(custom_mode='OFFBOARD'):
			print("Vehicle offboard succeed!")
		else:
			print("Vehicle offboard failed!")
	elif key == '3':
		if setModeServer(custom_mode='AUTO.LAND'):
			print("Vehicle land succeed!")
		else:
			print("Vehicle land failed!")
	elif key == '4':
		if setModeServer(custom_mode='POSCTL'):
			print("Vehicle posControl succeed!")
		else:
			print("Vehicle posControl failed!")
	elif key == '5':
		if setModeServer(custom_mode='STABILIZED'):
			print("Vehicle stabilized succeed!")
		else:
			print("Vehicle stabilized failed!")
	elif key == '6':
		if setModeServer(custom_mode='AUTO.MISSION'):
			print("Vehicle mission succeed!")
		else:
			print("Vehicle mission failed!")

# 摇杆的拨杆范围设置
def action_control():
	global speed_control

	#油门通道
	if mavros_state.mode == 'POSCTL':
		if key == 'i'or key == 'I':
			channel1 = 1850
		elif key == 'k'or key == 'K':
			channel1 = 1150
		else :
			channel1 = 1500
	elif mavros_state.mode == 'STABILIZED':
		if key == 'i'or key == 'I':
			channel1 = 1600
		elif key == 'k'or key == 'K':
			channel1 = 1400
		else :
			channel1 = 1100
	else:
		channel1 = 1000

	#pitch通道
	if key == 'e' or key == 'E':
		channel2 = speed_control
	elif key == 'd' or key == 'D':
		channel2 = 3000-speed_control
	else:
		channel2 = 1500

	#roll通道
	if key == 's' or key == 'S':
		channel0 = 3000-speed_control
	elif key == 'f' or key == 'F':
		channel0 = speed_control
	else:
		channel0 = 1500

	#偏航通道
	if key == 'j' or key == 'J':
		channel3 = 1850
	elif key == 'l' or key == 'L':
		channel3 = 1150
	else:
		channel3 = 1500

	global cur_target_rc_yaw
	cur_target_rc_yaw = RCInOverride(channel0,channel1,channel2,channel3)

	if key == 'h' or key == 'H':
		speed_control = speed_control + 10
		print('Current control speed :',speed_control)
	elif key == 'g' or key == 'G':
		speed_control = speed_control - 10
		print('Current control speed :',speed_control)

if __name__=="__main__":
	settings = termios.tcgetattr(sys.stdin)
	print (msg)
	__init__()
	cur_target_rc_yaw = RCInOverride(1500,1500,1000,1500)
	while(1):
		key= getKey()
		command_control()
		action_control()
		local_target_pub.publish(cur_target_rc_yaw)
		if (key == '\x03'):
			break
#		rospy.spin()
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
