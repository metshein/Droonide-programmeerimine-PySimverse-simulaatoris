# Camera and Video

This page explains the camera and video behavior observed in the `Drone` source code.

For the full method reference, see [Drone API Reference](drone-api.md#camera-and-video).

## Video Streaming Overview

The `Drone` class creates a ZeroMQ `SUB` socket for video:

```python
self.video_socket = self.context.socket(zmq.SUB)
self.video_address = f"tcp://localhost:{video_port}"
```

During `connect()`, the video socket connects and subscribes to all messages:

```python
self.video_socket.connect(self.video_address)
self.video_socket.setsockopt_string(zmq.SUBSCRIBE, "")
```

The default video address is:

```text
tcp://localhost:5557
```

## Turning the Stream On

```python
from pysimverse import Drone

drone = Drone()
drone.connect()
drone.streamon()
```

Observed behavior:

- Sets `drone.stream_on` to `True`.
- Sends a command payload where `streamon` is `True`.

The stream command is sent over the command socket. Video frames still depend on a simulator or publisher sending encoded frame bytes to the video port.

## Reading Frames

Use `get_frame()`:

```python
frame, ok = drone.get_frame()
```

Return values:

- `frame`: decoded OpenCV image frame, or `None`.
- `ok`: `True` when a frame was decoded, otherwise `False`.

Internally, frames are decoded with OpenCV:

```python
cv2.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
```

Because OpenCV is used, decoded color frames are in BGR format.

## Displaying Video With OpenCV

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

## Saving a Single Frame

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
        print("No frame available")
finally:
    drone.streamoff()
    drone.shutdown()
```

## Camera Rotation

`rotate_camera(angle)` controls the camera angle while the drone is flying:

```python
from pysimverse import Drone

drone = Drone()
drone.connect()
drone.take_off()

drone.rotate_camera(30)
drone.rotate_camera(-30)

drone.land()
drone.shutdown()
```

Observed behavior:

- Requires `drone.is_flying` to be `True`.
- Sends `angle` as the `cameraangle` field.
- Waits for `abs(angle / 40)` seconds.
- Sends a stop command.

## Turning the Stream Off

```python
drone.streamoff()
```

Observed behavior:

- Sets `drone.stream_on` to `False`.
- Sends a command payload where `streamon` is `False`.
- Does not close the video socket.

## Notes and Limitations

- `streamon()` and `streamoff()` only send stream commands; they do not guarantee the simulator starts or stops publishing frames.
- `get_frame()` does not call `streamon()` automatically.
- `get_frame()` polls with a 10 ms timeout, so it can return `(None, False)` when no frame is currently queued.
- `get_frame()` discards older pending frames during a call and returns the most recent decoded frame.
- `rotate_camera()` does not validate angle ranges and does not confirm the actual camera position.
