import time
from pysimverse import Drone

drone = Drone()
drone.connect()

drone.take_off()
time.sleep(1)
drone.move_forward(100)
drone.land()

drone.shutdown()