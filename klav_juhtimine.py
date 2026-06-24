from pysimverse import Drone
import keyboard
import time

drone = Drone()
drone.connect()

speed = 50
rspeed = 5

while True:

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

    drone.send_rc_control(lr, fb, ud, yaw)

    if keyboard.is_pressed("esc"):
        drone.land()
        break

    time.sleep(0.05)