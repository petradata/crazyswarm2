#!/usr/bin/env python

from pathlib import Path

from crazyflie_py import Crazyswarm
from crazyflie_py.uav_trajectory import Trajectory
import numpy as np

import time
import threading
import shutil
import os
from subprocess import Popen, PIPE, TimeoutExpired, STDOUT
import atexit
import signal

#supervisor bitfield constants
CAN_BE_ARMED = 1    # 0b00000001
IS_ARMED     = 2    # 0b00000010  
AUTO_ARM     = 4    # 0b00000100
CAN_FLY      = 8    # 0b00001000
IS_FLYING    = 16   # 0b00010000
IS_TUMBLED   = 32   # 0b00100000
IS_LOCKED    = 64   # 0b01000000


def is_crashed(swarm : Crazyswarm, ros2_ws):
    print("function call is_crashed")
    allcfs = swarm.allcfs
    while True: 
        # swarm.timeHelper.sleep(10)
        time.sleep(5)
        status = allcfs.crazyflies[0].get_status()
        if status == {}:
            print("status is an empty dictionary")
            continue
        print(status["supervisor"])
        #if the CF is tumbled (32) or locked(64)
        if (status['supervisor'] & IS_TUMBLED) or (status['supervisor'] & IS_LOCKED):
        # if status['supervisor'] == 32 or status['supervisor'] == 64:
            print("Crazyflie has crashed. Downloading logs and ending infinite_flight")
            outputfile = str(ros2_ws) + "/infinite_flight_results/SDlogfile"
            for cf in swarm.allcfs.crazyflies:
                cf.downloadUSD(outputfile, verbose=True)
            print("Sd download finished")
            os._exit(0)
            # downloadSD_PIPE_file = str(ros2_ws) + "/infinite_flight_results/SD_download_PIPE.txt"
            # with open(downloadSD_PIPE_file, 'w') as f:
            #     try:               
            #         # src = "source " + str(ros2_ws) + '/install/setup.bash' 
            #         # command = f"{src} && ros2 run crazyflie downloadUSDLogfile --output SDlogfile" #if CF doesn't use default URI, add --uri custom_uri (e.g --uri radio://0/80/2M/E7E7E7E70B)
            #         # downloadSD= Popen(command, shell=True, stderr=STDOUT, stdout=f, text=True,         #download the log file in ....../ros2_ws/results/test_xxxxxxx/
            #         #                     cwd= ros2_ws / "infinite_flight_results" ,start_new_session=True, executable="/bin/bash") 
            #         # atexit.register(clean_process, downloadSD)
            #         # downloadSD.wait(timeout=180)
            #         f.write('success')
            #         print("download successful")
            #         os._exit(0)  
            #         #we need to call _exit to finish the whole script because sys.exit only finishes this thread
            #         #but _exit doesn't call cleanup handlers, flush stdio buffers, etc. Is this an issue ?
                    
                    
            #     except TimeoutExpired:
            #         # clean_process(downloadSD)
            #         print("Downloading SD card data was killed for taking too long")
            #         f.write('\n \n \n#########################################################\n')
            #         f.write("Downloading SD card data was killed for taking too long !\n")
            #         f.write('#########################################################\n \n \n \n')
            #         os._exit(1)
                     
        else:
            print("all good")
            
def clean_process(process:Popen) -> int :
    '''Kills process and its children on exit if they aren't already terminated (called with atexit). Returns 0 on termination, 1 if SIGKILL was needed''' 
    if process.poll() == None:
        group_id = os.getpgid(process.pid)
        print(f"cleaning process {group_id}")
        os.killpg(group_id, signal.SIGTERM)
        time.sleep(0.01) #necessary delay before first poll
        i=0
        while i < 10 and process.poll() == None:  #in case the process termination is lazy and takes some time, we wait up to 0.5 sec per process
            if process.poll() != None:
                return 0  #if we have a returncode-> it terminated
            time.sleep(0.05) #if not wait a bit longer
        if(i == 9):
            os.killpg(group_id, signal.SIGKILL)
            return 1  #after 0.5s we stop waiting, consider it did not terminate correctly and kill it
        return 0
    else:
        return 0 #process already terminated


def main():
    #delete previous logfiles if they exist
    # if(Path(Path.home() / ".ros/log").exists()): #delete log files of the previous test
        # shutil.rmtree(Path.home() / ".ros/log")
    #create folder where the logfiles of the crash will be downloaded
    ros2_ws = Path.home() / "ros2_ws"
    if(Path(ros2_ws / "infinite_flight_results").exists()):
        shutil.rmtree(ros2_ws / "infinite_flight_results")  
    os.makedirs(ros2_ws / "infinite_flight_results")
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs
    check_crashed_thread = threading.Thread(target=is_crashed, args=(swarm,ros2_ws), daemon=True)
    check_crashed_thread.start()
    traj1 = Trajectory()
    traj1.loadcsv(Path(__file__).parent / 'data/figure8.csv')
    
    #enable logging
    allcfs.setParam("usd.logging", 1)
    print("before upload traj", time.time())
    TIMESCALE = 1.0
    for cf in allcfs.crazyflies: #sometimes we get stuck at this for loop forever. Is it because upload_trajectory doesn't work properly ?
        print(cf)
        cf.uploadTrajectory(0, 0, traj1)
    timeHelper.sleep(1)
    print("upload traj finished", time.time())

    # pm_state : 0 = on battery  1 = charging  2 = charged  3 = low power  4 = shutdown
    flight_counter = 1
    while True:
        print("true loop")
        time.sleep(2)
        # print('takeoff')
        # allcfs.takeoff(targetHeight=1.0, duration=2.0)
        # timeHelper.sleep(2.5)
        # for cf in allcfs.crazyflies:
        #     pos = np.array(cf.initialPosition) + np.array([0, 0, 1.0])
        #     cf.goTo(pos, 0, 2.0)
        # timeHelper.sleep(2.5)

        # # fly figure8 until battery is low
        # fig8_counter = 0
        # status = allcfs.crazyflies[0].get_status()
        # # while status['battery'] > 3.8:
        # while status['pm_state'] == 0:
        #     fig8_counter += 1
        #     print(f'starting figure8 number {fig8_counter} of flight number {flight_counter}')
        #     allcfs.startTrajectory(0, timescale=TIMESCALE)
        #     timeHelper.sleep(traj1.duration * TIMESCALE + 2.0)
        #     status = allcfs.crazyflies[0].get_status()
        #     print(f'pm state : {status["pm_state"]}, battery left : {status["battery"]}')
        #     timeHelper.sleep(1)

        # # not sure if useful
        # # check if pm = 3 just to be sure, if not abort test
        # if status['pm_state'] != 3:
        #     print(f'power state is not 3 (low) but {status["pm_state"]}. Landing and aborting')
        #     allcfs.land(targetHeight=0.06, duration=2.0)
        #     timeHelper.sleep(3)
        #     return 1

        # # now that battery is low, we try to land on the pad and see if it's charging
        # allcfs.land(targetHeight=0.06, duration=2.0)
        # timeHelper.sleep(5)
        # status = allcfs.crazyflies[0].get_status()

        # # if not charging, take off and land back again until it charges
        # while status['pm_state'] != 1:
        #     print('Not charging, retrying')
        #     allcfs.takeoff(targetHeight=1.0, duration=2.0)
        #     timeHelper.sleep(2.5)
        #     for cf in allcfs.crazyflies:
        #         pos = np.array(cf.initialPosition) + np.array([0, 0, 1.0])
        #     cf.goTo(pos, 0, 2.0)
        #     timeHelper.sleep(2.5)
        #     allcfs.land(targetHeight=0.06, duration=2.0)
        #     timeHelper.sleep(5)
        #     status = allcfs.crazyflies[0].get_status()

        # # now we wait until the crazyflie is charged
        # while status['battery'] < 3.78:
        # # while status['pm_state'] != 2:
        #     print(f'Charging in progress, battery at {status["battery"]}V')
        #     timeHelper.sleep(60)
        #     status = allcfs.crazyflies[0].get_status()
        #     # check if it's still charging ###not sure if this check is useful
        #     if status['pm_state'] != 1:
        #         print(f'charging interrupted, pm state : {status["pm_state"]}')

        # print('Charging finished, time to fly again')
        # flight_counter += 1


if __name__ == '__main__':
    main()
