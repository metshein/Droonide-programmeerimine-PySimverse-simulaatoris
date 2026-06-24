from pysimverse import Drone 

drone = Drone() 
drone.connect() 
drone.set_speed(99)
drone.take_off() 

drone.move_forward(250)
drone.move_right(200)

drone.land()