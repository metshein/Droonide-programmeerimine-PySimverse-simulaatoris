# Examples

These examples are based on the actual `Drone` API. They assume a compatible simulator is running and publishing/receiving on the expected ZeroMQ ports.

For setup notes, see [Getting Started](getting-started.md). For method details, see [Drone API Reference](drone-api.md).

## Print the Drone Source

This is the behavior already present in `test.py`.

```python
import inspect
from pysimverse import Drone

print(inspect.getsource(Drone))
```

## Basic Takeoff, Move, Land

```python
import time
from pysimverse import Drone

drone = Drone()
drone.connect()

try:
    drone.take_off()
    time.sleep(1)

    drone.move_forward(100)
    drone.rotate(90)
    drone.move_right(50)

    drone.land()
finally:
    drone.shutdown()
```

## Movement Square

```python
from pysimverse import Drone

drone = Drone(speed=25)
drone.connect()

try:
    drone.take_off()

    for _ in range(4):
        drone.move_forward(100)
        drone.rotate(90)

    drone.land()
finally:
    drone.shutdown()
```

## Change Speed

```python
from pysimverse import Drone

drone = Drone()
drone.connect()

try:
    drone.set_speed(30)
    drone.take_off()

    drone.move_forward(90)
    drone.move_backward(90)

    drone.land()
finally:
    drone.shutdown()
```

## Rotate With a Custom Rotation Speed

```python
from pysimverse import Drone

drone = Drone()
drone.connect()

try:
    drone.set_rotation_speed(25)
    drone.take_off()

    drone.rotate(180)
    drone.rotate(-180)

    drone.land()
finally:
    drone.shutdown()
```

## Read One Video Frame

```python
import cv2
from pysimverse import Drone

drone = Drone()
drone.connect()
drone.streamon()

try:
    frame, ok = drone.get_frame()
    if ok:
        cv2.imwrite("drone-frame.jpg", frame)
        print("Saved drone-frame.jpg")
    else:
        print("No frame was available")
finally:
    drone.streamoff()
    drone.shutdown()
```

## Display Live Video

Press `q` in the OpenCV window to exit.

```python
import cv2
from pysimverse import Drone

drone = Drone()
drone.connect()
drone.streamon()

try:
    while True:
        frame, ok = drone.get_frame()

        if ok:
            cv2.imshow("Drone Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    drone.streamoff()
    drone.shutdown()
```

## Camera Tilt While Flying

```python
from pysimverse import Drone

drone = Drone()
drone.connect()

try:
    drone.take_off()

    drone.rotate_camera(30)
    drone.rotate_camera(-30)

    drone.land()
finally:
    drone.shutdown()
```

## Raw RC Command

Use `send_rc_control()` when you need direct access to the command payload fields.

```python
import time
from pysimverse import Drone

drone = Drone()
drone.connect()

try:
    drone.take_off()

    # Move forward for one second using a raw command.
    drone.send_rc_control(
        left_right=0,
        forward_backward=20,
        up_down=0,
        yaw=0,
        camera_angle=0,
    )
    time.sleep(1)

    # Stop.
    drone.send_rc_control(0, 0, 0, 0, 0)

    drone.land()
finally:
    drone.shutdown()
```

## Check Whether the Command Port Is Available

`is_port_available()` is defined on the class without `self`, so call it on `Drone`.

```python
from pysimverse import Drone

if Drone.is_port_available(5550):
    drone = Drone(cmd_port=5550)
    drone.connect()
    drone.shutdown()
else:
    print("Port 5550 is already in use")
```

## Read Battery Telemetry

```python
from pysimverse import Drone

drone = Drone()
drone.connect()

try:
    drone.get_battery()
finally:
    drone.shutdown()
```

Observed limitation: `get_battery()` prints the battery value and parses it internally, but it does not return the parsed number.
