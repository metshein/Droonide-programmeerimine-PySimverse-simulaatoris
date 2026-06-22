# Getting Started

This page explains how to start using the `Drone` class exposed by `pysimverse`.

## Repository Layout

The repository itself contains a minimal helper script:

```text
test.py
```

`test.py` imports the installed `Drone` class and prints its source code:

```python
import inspect
from pysimverse import Drone

print(inspect.getsource(Drone))
```

The actual implementation is installed in the local virtual environment, not in a project package inside this repository.

## Requirements

Observed from the installed package metadata:

- Python 3.7 or newer
- `pysimverse==0.14`
- `pyzmq`
- `opencv-python`

The code imports these modules directly:

```python
import zmq
import cv2
import numpy as np
import time
import socket
```

## Importing Drone

Use:

```python
from pysimverse import Drone
```

The package also exports `DroneManager`, but this documentation focuses on `Drone` because that is what the repository source imports and what the request asks to document.

## Creating a Drone

```python
from pysimverse import Drone

drone = Drone()
```

Default constructor values:

```python
Drone(
    host="*",
    cmd_port=5550,
    state_port=5556,
    video_port=5557,
    speed=20,
    rotation_speed=15,
)
```

These values configure the ZeroMQ addresses and movement speed settings.

## Connecting

Call `connect()` before sending commands or reading telemetry/video:

```python
drone = Drone()
drone.connect()
```

Observed connection behavior:

- Binds the command publisher to `tcp://{host}:{cmd_port}`.
- Connects the state subscriber to `tcp://localhost:{state_port}`.
- Connects the video subscriber to `tcp://localhost:{video_port}`.
- Subscribes to all messages on state and video sockets.
- Prints `Response: Connected`.
- Sleeps for 0.25 seconds to allow subscriber setup.

See [Connection and Telemetry](drone-api.md#connection-and-telemetry) for more detail.

## First Flight

```python
import time
from pysimverse import Drone

drone = Drone()
drone.connect()

drone.take_off()
time.sleep(1)
drone.move_forward(100)
drone.land()

drone.shutdown()
```

## How Movement Works

Movement methods send RC control values, sleep for an estimated duration, then send a stop command.

For example, `move_forward(distance)` does this when the drone is flying:

1. Sends forward speed using `send_rc_control(0, self.speed, 0, 0, 0)`.
2. Waits for `distance / self.speed` seconds.
3. Sends `send_rc_control(0, 0, 0, 0, 0)` to stop.

This means `distance` is used as an input to a timing calculation. The code does not verify the actual distance traveled.

## How Video Works

Video is received over a ZeroMQ subscriber. To request streaming:

```python
drone.streamon()
frame, ok = drone.get_frame()
```

`get_frame()` reads all pending frames and keeps the most recent decoded frame. It returns:

```python
(frame, is_success)
```

See [Camera and Video](camera.md).

## Cleaning Up

Call `shutdown()` at the end of scripts that opened sockets or OpenCV windows:

```python
drone.shutdown()
```

Observed cleanup behavior:

- Closes command, state, and video sockets.
- Terminates the ZeroMQ context.
- Calls `cv2.destroyAllWindows()`.
- Prints `Drone server has been terminated.`

## Next Steps

- Read the full [Drone API Reference](drone-api.md).
- Try copyable scripts from [Examples](examples.md).
- Use [Troubleshooting](troubleshooting.md) if sockets, frames, or movement do not behave as expected.
