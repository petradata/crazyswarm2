#!/usr/bin/env python

from pathlib import Path

from crazyflie_py import Crazyswarm
from crazyflie_py.uav_trajectory import Trajectory
import numpy as np


def main():
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    traj1 = Trajectory()
    traj1.loadcsv(Path(__file__).parent / 'data/figure8_rotated.csv')

    TRIALS = 1
    TIMESCALE = 0.8
    HEIGHT = 1.1
    for i in range(TRIALS):
        for cf in allcfs.crazyflies:
            cf.uploadTrajectory(0, 0, traj1)

        allcfs.takeoff(targetHeight=HEIGHT, duration=3.0)
        timeHelper.sleep(2.5)
        for cf in allcfs.crazyflies:
            pos = np.array(cf.initialPosition) + np.array([0, 0, HEIGHT])
            cf.goTo(pos, 0, 2.0)
        timeHelper.sleep(2.5)

        # enable logging
        # allcfs.setParam('ctrlLeeP.indi', 2)
        timeHelper.sleep(5)
     
        allcfs.setParam('usd.logging', 1)
        timeHelper.sleep(3)
        # allcfs.setParam('ctrlLeeP.est_acc', 0)

        allcfs.setParam('stabilizer.controller', 7)
        timeHelper.sleep(8)
        # allcfs.setParam('ctrlLeeP.est_acc', 2)
        # timeHelper.sleep(5)

        allcfs.setParam('ctrlLeeP.indi', 1)
        # allcfs.setParam('ctrlLeeP.use_nn', 1)
        timeHelper.sleep(1)
        # allcfs.setParam('usd.logging', 0)

        # exit()


     
        # timeHelper.sleep(8)

        # allcfs.setParam('usd.logging', 1)
        # timeHelper.sleep(3)

        allcfs.startTrajectory(0, timescale=TIMESCALE)
        timeHelper.sleep(traj1.duration * TIMESCALE)

        timeHelper.sleep(5)
        # disable logging
        allcfs.setParam('usd.logging', 0)
        allcfs.setParam('stabilizer.controller', 5)

        # allcfs.setParam('ctrlLee.indi', 0)


        # allcfs.startTrajectory(0, timescale=TIMESCALE, reverse=True)
        # timeHelper.sleep(traj1.duration * TIMESCALE + 2.0)

        allcfs.land(targetHeight=0.06, duration=2.0)
        timeHelper.sleep(3.0)




if __name__ == '__main__':
    main()
