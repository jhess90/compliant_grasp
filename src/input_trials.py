#!/usr/bin/env python
# license removed for brevity
import rospy
import math
import time
from std_msgs.msg import Int32

global freq
freq = 10


def talker():
    pressure_pub = rospy.Publisher('/pressure_cmd', Int32)

    rospy.init_node('wam_python', anonymous=True)
    r = rospy.Rate(freq) # 10hz
    

    while not rospy.is_shutdown():
        pressure_pub.publish(0)
        #rospy.loginfo(msg)
        r.sleep()

 

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException: pass
