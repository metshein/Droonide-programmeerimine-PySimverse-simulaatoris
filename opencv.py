from pysimverse import Drone
import keyboard
import cv2
import time
from datetime import datetime

drone = Drone()

drone.connect()
drone.streamon()
drone.take_off()

speed = 50

while True:

    frame = drone.get_frame()[0]

    if frame is not None:
        cv2.imshow("Drooni kaamera", frame)

    lr = 0
    fb = 0

    if keyboard.is_pressed("w"):
        fb = speed
    if keyboard.is_pressed("s"):
        fb = -speed
    if keyboard.is_pressed("a"):
        lr = -speed
    if keyboard.is_pressed("d"):
        lr = speed
    if keyboard.is_pressed("p"):
        failinimi = datetime.now().strftime( "fotod/%Y-%m-%d_%H-%M-%S.jpg" ) 
        cv2.imwrite(failinimi, frame) 
        print("Pilt salvestatud:", failinimi)

    drone.send_rc_control(lr, fb, 0, 0)

    cv2.waitKey(1)
    time.sleep(0.05)