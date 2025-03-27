#!/usr/bin/env python

from pathlib import Path

from crazyflie_py import Crazyswarm
from crazyflie_py.uav_trajectory import Trajectory
import numpy as np


def main():
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    # allcfs.setParam('stabilizer.controller', 5)
    # timeHelper.sleep(3)
    # exit()

    allcfs.arm(True)

    traj1 = Trajectory()
    traj1.loadcsv(Path(__file__).parent / 'data/yaw0.csv')

    TRIALS = 1
    TIMESCALE = 0.5
    HEIGHT = 0.5
    for i in range(TRIALS):
        for cf in allcfs.crazyflies:
            cf.uploadTrajectory(0, 0, traj1)

        allcfs.takeoff(targetHeight=HEIGHT, duration=3.0)
        timeHelper.sleep(2.5)
        # for cf in allcfs.crazyflies:
        #     pos = np.array(cf.initialPosition) + np.array([0, 0, HEIGHT])
        #     cf.goTo(pos, 0, 2.0)
        # timeHelper.sleep(2.5)

        # # yaw motion
        # yaw = 0
        # for i in range(10):
        #     for cf in allcfs.crazyflies:
        #         pos = np.array(cf.initialPosition) + np.array([0, 0, HEIGHT])
        #         cf.goTo(pos, yaw, 2.0)
        #     yaw += 1.0
        #     timeHelper.sleep(1.5)

        # enable logging
        # allcfs.setParam('ctrlLee.indi', 3)
        # timeHelper.sleep(5)
        # allcfs.setParam('stabilizer.controller', 7)
        # timeHelper.sleep(8)

        allcfs.setParam('usd.logging', 1)
        timeHelper.sleep(3)

        allcfs.startTrajectory(0, timescale=TIMESCALE)
        timeHelper.sleep(traj1.duration * TIMESCALE)

        # timeHelper.sleep(3)
        # disable logging
        allcfs.setParam('usd.logging', 0)
        # allcfs.setParam('stabilizer.controller', 5)

        # allcfs.setParam('ctrlLee.indi', 0)


        # allcfs.startTrajectory(0, timescale=TIMESCALE, reverse=True)
        # timeHelper.sleep(traj1.duration * TIMESCALE + 2.0)

        allcfs.land(targetHeight=0.06, duration=2.0)
        timeHelper.sleep(3.0)
        allcfs.arm(False)
        timeHelper.sleep(1.0)


if __name__ == '__main__':
    main()
