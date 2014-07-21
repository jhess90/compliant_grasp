#!/usr/bin/env python
# license removed for brevity
import rospy
import math
import time
PACKAGE='compliant_grasp'
#PACKAGE2='wam_node'
import roslib
roslib.load_manifest(PACKAGE)
#roslib.load_manifest(PACKAGE2)
from std_msgs.msg import String
from biotac_sensors.msg import BioTacHand
from compliant_grasp.msg import HandPosVel
from sensor_msgs.msg import JointState


class Finger(object):
    pos=0.0       # actual position from /bahnd/joint_state
    pos_n=0.0     # next required position
    pr=9999       # pressure from tactile sensors
    status=2      # status close()=0, stay()=1 or open()=2
    offset=0        # pressure sensor offset


    def __init__(self,offst):
        self.pos=0.0
        self.pos_n=0.0
        self.pr=9999
        self.status=2
        self.offset=offst

    def CalcStatus(self):
        if (self.pr>self.offset+7 and self.pr<self.offset+150):
            self.status = 1
        elif (self.pr>=self.offset+150):
            self.status = 2
        else:
            self.status = 0
    
    def CalcNextPos(self,incr):
        if (self.status==2):
            self.pos_n = -incr
        elif (self.status==1):
            self.pos_n = 0.0
        else:
            self.pos_n = incr
    

        


global F1
global F2
global F3
global SPREAD
F1=Finger(2620)
F2=Finger(2170)
F3=Finger(2270)
SPREAD=Finger(0)

global freq
freq = 20


def talker():
    rospy.Subscriber("biotac_pub", BioTacHand , callback_biotac)
    #rospy.Subscriber("/bhand/joint_states", JointState , callback_WAM_JointState)
    joint_vel_pub = rospy.Publisher('/bhand/hand_pos_vel_cmd', HandPosVel)

    rospy.init_node('wam_python', anonymous=True)
    r = rospy.Rate(freq) # 10hz
    calibrate()

    while not rospy.is_shutdown():
        CalcStatus()
        CalcNextPos(2.4/8/freq)
        
        msg=GenMsg()
        joint_vel_pub.publish(msg)
        #rospy.loginfo(msg)
        r.sleep()

def calibrate():
    sum1=0
    sum2=0
    sum3=0
    for count in range(100):
        sum1+=F1.pr
        sum2+=F2.pr
        sum3+=F3.pr
        time.sleep(0.05)

    F1.offset=sum1/count
    F2.offset=sum2/count
    F3.offset=sum3/count

def CalcStatus():
    F1.CalcStatus()
    F2.CalcStatus()
    F3.CalcStatus()
        
def CalcNextPos(incr):
    F1.CalcNextPos(incr)
    F2.CalcNextPos(incr)
    F3.CalcNextPos(incr)

def GenMsg():
    return HandPosVel([F1.pos_n,F2.pos_n,F3.pos_n,SPREAD.pos_n],freq)


# def slow_close(freq):
#     incr=2.4/8/freq
#     return HandPosVel([f1+incr,f2+incr,f3+incr,spread],freq)

# def stay(freq):
#     incr=0.0
#     return HandPosVel([f1+incr,f2+incr,f3+incr,spread],freq)

# def slow_open(freq):
#     incr=2.4/8/freq
#     return HandPosVel([f1-incr,f2-incr,f3-incr,spread],freq)




def callback_WAM_JointState(msg):
    global F1
    global F2
    global F3
    global SPREAD
    
    F1.pos=msg.position[0]
    F2.pos=msg.position[1]
    F3.pos=msg.position[2]
    SPREAD.pos=msg.position[3]


def callback_biotac(msg):
    global F1
    global F2
    global F3

    F1.pr=msg.bt_data[0].pdc_data
    F2.pr=msg.bt_data[1].pdc_data
    F3.pr=msg.bt_data[2].pdc_data
    #rospy.loginfo(F1.pr)
    #rospy.loginfo(F2.pr)
    #rospy.loginfo(F3.pr)
 

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException: pass
