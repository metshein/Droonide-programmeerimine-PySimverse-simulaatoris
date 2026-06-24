from pysimverse import Drone 

drone = Drone() 
drone.connect() 
drone.set_speed(99)
drone.take_off() 

drone.move_forward(350)
drone.move_left(220)
drone.move_down(80)
drone.move_backward(160)
drone.move_right(450)


drone.land()