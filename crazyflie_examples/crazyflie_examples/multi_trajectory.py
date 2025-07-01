#!/usr/bin/env python

from pathlib import Path

from crazyflie_py import Crazyswarm
from crazyflie_py.uav_trajectory import Trajectory
import numpy as np


def main():
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs
    trajs = []
    n = 4  # number of distinct trajectories

    # path = 'data/two_circle'
    path = 'data/two_circle_traj_r0.5'

    # enable logging
    # allcfs.setParam('usd.logging', 1)

    # for i in range(n):
    #     traj = Trajectory()
    #     traj.loadcsv(Path(__file__).parent / f'data/multi_trajectory/traj{i}.csv')
    #     trajs.append(traj)


    ##### load two circle trajectories, horizontal and vertical 
    for i in range(n):
        traj = Trajectory()
        traj.loadcsv(Path(__file__).parent / f'{path}/horizontal{i}.csv')
        trajs.append(traj)
    # for i in range(n):
    #     traj = Trajectory()
    #     traj.loadcsv(Path(__file__).parent / f'{path}/vertical{i}.csv')
    #     trajs.append(traj)



    TRIALS = 1
    TIMESCALE = 1.0
    for i in range(TRIALS):
        for idx, cf in enumerate(allcfs.crazyflies):
            cf.uploadTrajectory(0, 0, trajs[idx % len(trajs)])

        allcfs.takeoff(targetHeight=1.0, duration=2.0)
        timeHelper.sleep(3.0)

        ids = list(allcfs.crazyfliesById.keys())
        print("All Crazyflie IDs:", ids)
        
        for i, cf_id in enumerate(ids):
            cf = allcfs.crazyfliesById[cf_id]
            start_pos = trajs[i % len(trajs)].eval(0).pos  # (x, y, z)
            print(f"CF ID: {cf_id} going to start position {start_pos}")
            cf.goTo(start_pos, 0, 2.0)  # 0 is yaw, 2.0 is duration (adjust as needed)


        timeHelper.sleep(2.5) 


        allcfs.startTrajectory(0, timescale=TIMESCALE)
        timeHelper.sleep(max([t.duration for t in trajs]) * TIMESCALE + 2.0)

        allcfs.land(targetHeight=0.06, duration=2.0)
        timeHelper.sleep(3.0)

    # disable logging
    # allcfs.setParam('usd.logging', 0)


if __name__ == '__main__':
    main()
