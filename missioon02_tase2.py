from pysimverse import Drone 

drone = Drone() 
drone.connect() 
drone.set_speed(99)
drone.take_off() 

drone.move_forward(50)
drone.move_left(200)
drone.move_forward(160)
drone.move_right(170)
drone.move_forward(90)
drone.move_right(230)

drone.land()