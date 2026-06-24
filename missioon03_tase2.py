from pysimverse import Drone
import keyboard
import time
import cv2
from datetime import datetime

drone = Drone()
drone.connect()
drone.streamon()

speed = 50
rspeed = 5

while True:

    frame = drone.get_frame()[0]

    if frame is not None:
        cv2.imshow("Drooni kaamera", frame)

    lr = 0
    fb = 0
    ud = 0
    yaw = 0

    if keyboard.is_pressed("space"):
        drone.take_off()
        time.sleep(1)

    if keyboard.is_pressed("w"):
        fb = speed

    if keyboard.is_pressed("s"):
        fb = -speed

    if keyboard.is_pressed("a"):
        lr = -speed

    if keyboard.is_pressed("d"):
        lr = speed

    if keyboard.is_pressed("q"):
        yaw = -rspeed

    if keyboard.is_pressed("e"):
        yaw = rspeed

    if keyboard.is_pressed("up"):
        ud = speed

    if keyboard.is_pressed("down"):
        ud = -speed

    if keyboard.is_pressed("z"):
        failinimi = datetime.now().strftime( "fotod/%Y-%m-%d_%H-%M-%S.jpg" ) 
        cv2.imwrite(failinimi, frame) 
        print("Pilt salvestatud:", failinimi)

    drone.send_rc_control(lr, fb, ud, yaw)

    if keyboard.is_pressed("esc"):
        drone.land()
        break

    cv2.waitKey(1)
    time.sleep(0.05)

