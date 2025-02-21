#!/usr/bin/python3
import numpy as np
from crazyflie_py import *
import threading
import time


SPEED = [3.0, 7.0]
ANGSPEED = .7
# DLIMITS = [1.0, 1.0]
BBOX = [[-1.2,-1.2,0.3],
        [1.2,1.2,0.9]]
DURATION = 20


def move(cf, last_pos, total_time, bbox_min, bbox_max):
    start = time.time()
    done = False
    last_yaw = 0
    while not done:
        if time.time() < start + total_time:
            pos = np.random.uniform(bbox_min, bbox_max)
            yaw = np.random.uniform(-np.pi, np.pi)
        else:
            # move back to the initial position at the end
            pos = np.array(cf.initialPosition) + np.array([0, 0, 0.5])
            yaw = 0
            done = True

        dist = np.linalg.norm(last_pos - pos)
        # atan2(sin(x-y), cos(x-y))
        dist2 = np.abs(np.arctan2(np.sin(yaw-last_yaw), np.cos(yaw-last_yaw)))
        speed = np.random.uniform(SPEED[0], SPEED[1]) # m/s
        time_to_move = max(max(dist / speed, 1.5), dist2/ANGSPEED)

        cf.goTo(pos, yaw, time_to_move)
        if done:
            time_to_sleep = time_to_move + 0.5
        else:
            time_to_sleep = np.random.uniform(1.0, time_to_move)
        time.sleep(time_to_sleep)
        last_pos = pos
        last_yaw = yaw

def main():
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    allcfs.setParam("ctrlLee.indi", 0) # switch to INDI

    # allcfs.setParam("usec.reset", 1)

    # for the flight part
    # allcfs.setParam("motorPowerSet.enable", 0) # make sure mocap can see us
    timeHelper.sleep(0.5)
    allcfs.takeoff(targetHeight=0.5, duration=3.0)
    timeHelper.sleep(3.0)
    allcfs.setParam("ctrlLee.indi", 3) # switch to INDI
    timeHelper.sleep(1.0)

    # start recording to sdcard
    allcfs.setParam("usd.logging", 1)

    # # start thread for each cf
    # threads = []
    # total_time = DURATION
    # for _, cf in allcfs.crazyfliesById.items():
    #     cf_bbox_min = np.array(BBOX[0])
    #     cf_bbox_max = np.array(BBOX[1])
    #     pos = np.array(cf.initialPosition) + np.array([0, 0, 0.5])
    #     thread = threading.Thread(target=move_lowlevel, args=(cf, pos, total_time, cf_bbox_min, cf_bbox_max))
    #     thread.start()
    #     threads.append(thread)

    # # wait for all threads to be done
    # for thread in threads:
    #     thread.join()

    cf = allcfs.crazyflies[0]
    pos = np.array(cf.initialPosition) + np.array([0, 0, 0.5])
    move(cf, pos, DURATION, BBOX[0], BBOX[1])

    # stop recording to sdcard
    allcfs.setParam("usd.logging", 0)

    allcfs.land(targetHeight=0.02, duration=3.0)
    timeHelper.sleep(3.0)
    


if __name__ == "__main__":
    main()