# pysimverse Drone Documentation

This documentation describes the `Drone` API exposed by the source code used in this repository.

The repository contains `test.py`, which imports `Drone` from `pysimverse` and prints its source with `inspect.getsource(Drone)`. The actual `Drone` implementation is installed in the local virtual environment at `.venv/Lib/site-packages/pysimverse/simulators/drone/drone.py`.

The installed package metadata identifies the package as:

- Package: `pysimverse`
- Version: `0.14`
- Summary: Python Computer Vision and Robotics Simulator
- Runtime dependencies observed in metadata: `pyzmq`, `opencv-python`

## Documentation Pages

- [Getting Started](getting-started.md)
- [Drone API Reference](drone-api.md)
- [Camera and Video](camera.md)
- [Examples](examples.md)
- [Troubleshooting](troubleshooting.md)

## What the Drone Class Does

`Drone` is a small Python client for controlling a simulated drone over ZeroMQ sockets.

It creates three communication channels:

- A command publisher for sending movement, camera, color, and stream commands.
- A telemetry subscriber for receiving state data such as battery text messages.
- A video subscriber for receiving encoded image frames.

The class also provides convenience methods for common actions:

- Connect to the simulator.
- Take off and land.
- Move in six directions.
- Rotate the drone.
- Rotate the camera.
- Turn the video stream on and off.
- Read the most recent video frame.
- Adjust movement and rotation speed settings.

## Important Observed Behavior

This documentation is based on the actual source code, not on an external API specification. A few behaviors are worth knowing early:

- Most command methods return `None`; they send data over ZeroMQ and print status messages.
- `get_frame()` returns `(frame, is_success)`.
- `get_battery()` receives and parses telemetry, but does not return the parsed value.
- Movement methods estimate travel time using `distance / speed`; they do not wait for simulator feedback.
- Movement, rotation, landing, and camera rotation require `is_flying` to be `True`.
- `is_port_available()` is defined without `self`, so call it as `Drone.is_port_available(port)`.

## Basic Usage

```python
import time
from pysimverse import Drone

drone = Drone()
drone.connect()

drone.take_off()
time.sleep(1)
drone.move_forward(100)
drone.rotate(90)
drone.land()

drone.shutdown()
```

For more setup detail, see [Getting Started](getting-started.md). For every method, see the [Drone API Reference](drone-api.md).
