from pysimverse import Drone 

drone = Drone() 
drone.connect() 
drone.set_speed(99)
drone.take_off() 

# Ülesanne: ring
for i in range(72):
    drone.move_forward(5)
    drone.rotate(5)

drone.land()