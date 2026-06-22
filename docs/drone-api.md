# Drone API Reference

This page documents every public method observed on the `Drone` class.

Import:

```python
from pysimverse import Drone
```

Constructor signature:

```python
Drone(host="*", cmd_port=5550, state_port=5556, video_port=5557, speed=20, rotation_speed=15)
```

## Constructor

### `Drone(host="*", cmd_port=5550, state_port=5556, video_port=5557, speed=20, rotation_speed=15)`

**Description**

Creates a drone client with ZeroMQ sockets for commands, telemetry, and video. The constructor creates sockets and a video poller, but it does not bind or connect them. Call [`connect()`](#connect) after constructing the object.

**Parameters**

| Name | Default | Description |
| --- | --- | --- |
| `host` | `"*"` | Host used for the command publisher bind address. |
| `cmd_port` | `5550` | TCP port used to publish command JSON. |
| `state_port` | `5556` | TCP port used to subscribe to state/telemetry messages from `localhost`. |
| `video_port` | `5557` | TCP port used to subscribe to video frames from `localhost`. |
| `speed` | `20` | Default movement speed used by movement helper methods. |
| `rotation_speed` | `15` | Default rotation speed value used by `rotate()`. |

**Return value**

Returns a new `Drone` instance.

**Example usage**

```python
from pysimverse import Drone

drone = Drone(speed=30, rotation_speed=20)
drone.connect()
```

**Notes and limitations**

- The constructor initializes `is_flying` as `False`.
- The constructor registers the video socket with a ZeroMQ poller before `connect()` connects the socket.
- The default command bind address is `tcp://*:5550`.
- The default telemetry and video subscriber addresses always use `localhost`.

## Communication Model

### Commands

Commands are sent as JSON through a ZeroMQ `PUB` socket. The command payload created by [`send_rc_control()`](#send_rc_control) has this shape:

```json
{
  "left_right": 0,
  "forward_backward": 20,
  "up_down": 0,
  "yaw": 0,
  "cameraangle": 0,
  "streamon": null,
  "color": {
    "red": null,
    "green": null,
    "blue": null
  }
}
```

### Telemetry

Telemetry is received as strings over a ZeroMQ `SUB` socket. The only telemetry helper in `Drone` is [`get_battery()`](#get_battery), which reads one string message and attempts to parse it as a float.

### Video

Video is received as encoded bytes over a ZeroMQ `SUB` socket. [`get_frame()`](#get_frame) decodes bytes with OpenCV:

```python
cv2.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
```

See [Camera and Video](camera.md) for focused video examples.

## Connection and Telemetry

### `connect()`

**Description**

Binds and connects the ZeroMQ sockets used by the drone client.

Observed behavior:

- Binds `command_socket` to `tcp://{host}:{cmd_port}`.
- Connects `state_socket` to `tcp://localhost:{state_port}`.
- Subscribes to all state messages.
- Connects `video_socket` to `tcp://localhost:{video_port}`.
- Subscribes to all video messages.
- Prints `Response: Connected`.
- Sleeps for 0.25 seconds.

**Parameters**

None.

**Return value**

Returns `None`.

**Example usage**

```python
from pysimverse import Drone

drone = Drone()
drone.connect()
```

**Notes and limitations**

- `connect()` does not check whether a simulator is running.
- If the command port is already in use, the underlying ZeroMQ bind may raise an exception.
- The state and video sockets connect to `localhost` regardless of the `host` constructor argument.

### `shutdown()`

**Description**

Closes sockets, terminates the ZeroMQ context, destroys OpenCV windows, and prints a shutdown message.

**Parameters**

None.

**Return value**

Returns `None`.

**Example usage**

```python
from pysimverse import Drone

drone = Drone()
drone.connect()

try:
    drone.take_off()
finally:
    drone.shutdown()
```

**Notes and limitations**

- After `shutdown()`, the same `Drone` instance should not be reused for more commands.
- `shutdown()` does not call `land()` automatically.

### `get_battery()`

**Description**

Receives one telemetry string from `state_socket`, prints it as battery data, parses it as a float, then sleeps for one second.

Observed source behavior:

```python
message = self.state_socket.recv_string()
print(f"Received Battery Data: {message}%")
battery_percentage = float(message)
time.sleep(1)
```

**Parameters**

None.

**Return value**

Returns `None`.

**Example usage**

```python
from pysimverse import Drone

drone = Drone()
drone.connect()

drone.get_battery()
drone.shutdown()
```

**Notes and limitations**

- This method blocks until a state message is received.
- It parses `battery_percentage`, but does not return it.
- The received message must be parseable as `float`, or `float(message)` will raise `ValueError`.
- Only `KeyboardInterrupt` is caught by the method.

### `is_port_available(port)`

**Description**

Checks whether a TCP port on `localhost` can be bound.

**Parameters**

| Name | Description |
| --- | --- |
| `port` | TCP port number to test. |

**Return value**

Returns `True` if the port can be bound, otherwise `False`.

**Example usage**

```python
from pysimverse import Drone

if Drone.is_port_available(5550):
    print("Command port is available")
else:
    print("Command port is already in use")
```

**Notes and limitations**

- The method is defined without `self`, so call it as `Drone.is_port_available(5550)`.
- Calling `drone.is_port_available(5550)` on an instance will pass the instance automatically and can raise a `TypeError`.
- The method tests `localhost`, not the `host` configured on a `Drone` instance.

## Low-Level Command Method

### `send_rc_control(left_right, forward_backward, up_down, yaw, camera_angle=0, streamon=None, red=None, green=None, blue=None)`

**Description**

Publishes a command JSON object to the command socket. This is the low-level method used by movement, camera, stream, takeoff, and landing helpers.

**Parameters**

| Name | Description |
| --- | --- |
| `left_right` | Lateral movement command. Positive values are used by `move_right()`, negative values by `move_left()`. |
| `forward_backward` | Forward/backward movement command. Positive values are used by `move_forward()`, negative values by `move_backward()`. |
| `up_down` | Vertical movement command. Positive values are used by `move_up()` and takeoff, negative values by `move_down()` and landing. |
| `yaw` | Rotation/yaw command. `rotate()` sends positive or negative values here. |
| `camera_angle` | Camera angle value. Defaults to `0`. |
| `streamon` | Stream state. `streamon()` sends `True`; `streamoff()` sends `False`. |
| `red` | Optional red color component. |
| `green` | Optional green color component. |
| `blue` | Optional blue color component. |

**Return value**

Returns `None`.

**Example usage**

```python
from pysimverse import Drone

drone = Drone()
drone.connect()

# Send a raw forward command, then stop.
drone.send_rc_control(0, 20, 0, 0, 0)
drone.send_rc_control(0, 0, 0, 0, 0)

drone.shutdown()
```

**Notes and limitations**

- The method catches all exceptions and prints `Error publishing data: ...`.
- It does not validate value types or ranges.
- It prints every successfully published payload.
- Higher-level helpers usually send a movement command, wait, and then call this method again with zeros to stop.

## Flight State

### `take_off(takeoff_height=100, takeoff_speed=25)`

**Description**

Starts flight if the drone is not already flying. It waits two seconds, sets `is_flying` to `True`, sends an upward command, waits for `takeoff_height / takeoff_speed` seconds, sends a stop command, prints `Drone has taken off.`, and waits one more second.

**Parameters**

| Name | Default | Description |
| --- | --- | --- |
| `takeoff_height` | `100` | Used to calculate takeoff duration. |
| `takeoff_speed` | `25` | Upward command value and divisor for duration calculation. |

**Return value**

Returns `None`.

**Example usage**

```python
from pysimverse import Drone

drone = Drone()
drone.connect()
drone.take_off(takeoff_height=120, takeoff_speed=30)
drone.land()
drone.shutdown()
```

**Notes and limitations**

- The method does not confirm actual altitude.
- If `takeoff_speed` is `0`, the duration calculation will raise `ZeroDivisionError`.
- If `is_flying` is already `True`, it only prints `Drone is already flying.`

### `land(landing_speed=25)`

**Description**

Lands the drone if it is currently flying. It sends a downward command, waits 10 seconds, sends a stop command, sets `is_flying` to `False`, and prints `Drone has landed.`

**Parameters**

| Name | Default | Description |
| --- | --- | --- |
| `landing_speed` | `25` | Downward command speed. |

**Return value**

Returns `None`.

**Example usage**

```python
from pysimverse import Drone

drone = Drone()
drone.connect()
drone.take_off()
drone.land(landing_speed=20)
drone.shutdown()
```

**Notes and limitations**

- Landing always waits 10 seconds; it does not calculate duration from altitude.
- The method does not confirm actual touchdown.
- If `is_flying` is `False`, it prints `Drone is already on the ground.`

## Movement

All movement methods require `is_flying` to be `True`. If the drone has not taken off, each method prints `Take off the drone first.`

Movement distance is converted into time using:

```python
delay = distance / self.speed
```

The methods do not validate distance or speed values and do not use simulator feedback to confirm movement.

### `move_forward(distance)`

**Description**

Moves the drone forward using the current `speed`.

**Parameters**

| Name | Description |
| --- | --- |
| `distance` | Used with `self.speed` to calculate movement duration. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.take_off()
drone.move_forward(100)
```

**Notes and limitations**

- Sends `send_rc_control(0, self.speed, 0, 0, 0)`.
- If `self.speed` is `0`, the method raises `ZeroDivisionError`.

### `move_backward(distance)`

**Description**

Moves the drone backward using the current `speed`.

**Parameters**

| Name | Description |
| --- | --- |
| `distance` | Used with `self.speed` to calculate movement duration. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.take_off()
drone.move_backward(80)
```

**Notes and limitations**

- Sends `send_rc_control(0, -self.speed, 0, 0, 0)`.
- If `self.speed` is `0`, the method raises `ZeroDivisionError`.

### `move_right(distance)`

**Description**

Moves the drone right using the current `speed`.

**Parameters**

| Name | Description |
| --- | --- |
| `distance` | Used with `self.speed` to calculate movement duration. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.take_off()
drone.move_right(50)
```

**Notes and limitations**

- Sends `send_rc_control(self.speed, 0, 0, 0, 0)`.
- If `self.speed` is `0`, the method raises `ZeroDivisionError`.

### `move_left(distance)`

**Description**

Moves the drone left using the current `speed`.

**Parameters**

| Name | Description |
| --- | --- |
| `distance` | Used with `self.speed` to calculate movement duration. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.take_off()
drone.move_left(50)
```

**Notes and limitations**

- Sends `send_rc_control(-self.speed, 0, 0, 0, 0)`.
- If `self.speed` is `0`, the method raises `ZeroDivisionError`.

### `move_up(distance)`

**Description**

Moves the drone upward using the current `speed`.

**Parameters**

| Name | Description |
| --- | --- |
| `distance` | Used with `self.speed` to calculate movement duration. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.take_off()
drone.move_up(40)
```

**Notes and limitations**

- Sends `send_rc_control(0, 0, self.speed, 0, 0)`.
- If `self.speed` is `0`, the method raises `ZeroDivisionError`.

### `move_down(distance)`

**Description**

Moves the drone downward using the current `speed`.

**Parameters**

| Name | Description |
| --- | --- |
| `distance` | Used with `self.speed` to calculate movement duration. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.take_off()
drone.move_down(40)
```

**Notes and limitations**

- Sends `send_rc_control(0, 0, -self.speed, 0, 0)`.
- If `self.speed` is `0`, the method raises `ZeroDivisionError`.

## Rotation

### `rotate(angle)`

**Description**

Rotates the drone left or right depending on the sign of `angle`.

Observed behavior:

- If `angle < 0`, sends negative yaw.
- Otherwise, sends positive yaw.
- Waits `abs(angle / 60)` seconds.
- Sends a stop command.

**Parameters**

| Name | Description |
| --- | --- |
| `angle` | Rotation amount used to choose direction and calculate delay. Negative values rotate one direction; non-negative values rotate the opposite direction. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.take_off()
drone.rotate(90)
drone.rotate(-90)
```

**Notes and limitations**

- Requires `is_flying` to be `True`.
- The yaw value is `self.rotation_speed / 70` or `-self.rotation_speed / 70`.
- The code does not verify the actual resulting angle.

### `set_rotation_speed(rotation_speed)`

**Description**

Updates the `rotation_speed` attribute used by `rotate()`.

**Parameters**

| Name | Description |
| --- | --- |
| `rotation_speed` | New rotation speed value. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.set_rotation_speed(25)
drone.take_off()
drone.rotate(180)
```

**Notes and limitations**

- The method does not validate the value.
- `rotate()` divides `rotation_speed` by `70` before sending it as yaw.

## Speed

### `set_speed(speed)`

**Description**

Updates the `speed` attribute used by movement helper methods.

**Parameters**

| Name | Description |
| --- | --- |
| `speed` | New movement speed value. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.set_speed(30)
drone.take_off()
drone.move_forward(120)
```

**Notes and limitations**

- The method does not validate the value.
- Movement methods divide by `self.speed`; setting speed to `0` can cause `ZeroDivisionError`.

## Camera and Video

### `streamon()`

**Description**

Sets `stream_on` to `True` and publishes a stream command.

Observed payload is sent through:

```python
self.send_rc_control(None, None, None, None, None, self.stream_on)
```

**Parameters**

None.

**Return value**

Returns `None`.

**Example usage**

```python
drone.streamon()
frame, ok = drone.get_frame()
```

**Notes and limitations**

- This method only sends a command requesting streaming. Actual video availability depends on the simulator publishing frames.
- It does not require `is_flying` to be `True`.

### `streamoff()`

**Description**

Sets `stream_on` to `False` and publishes a stream command.

**Parameters**

None.

**Return value**

Returns `None`.

**Example usage**

```python
drone.streamoff()
```

**Notes and limitations**

- It does not close the video socket.
- It does not require `is_flying` to be `True`.

### `get_frame()`

**Description**

Receives and decodes video frames from the video socket.

The method polls the video socket with a 10 ms timeout. While frames are available, it receives frame bytes and decodes them. Older pending frames are overwritten in the local loop so the returned frame is the newest frame observed during that call.

**Parameters**

None.

**Return value**

Returns a tuple:

```python
(frame, is_success)
```

| Tuple item | Description |
| --- | --- |
| `frame` | Decoded OpenCV image frame, or `None` if no frame was decoded. |
| `is_success` | `True` if a frame was decoded, otherwise `False`. |

**Example usage**

```python
import cv2
from pysimverse import Drone

drone = Drone()
drone.connect()
drone.streamon()

frame, ok = drone.get_frame()
if ok:
    cv2.imshow("Drone", frame)
    cv2.waitKey(1)

drone.streamoff()
drone.shutdown()
```

**Notes and limitations**

- If no frame is decoded, it prints `Failed to decode frame.`
- If the ZeroMQ receive has no message, it can print `No new frames available.`
- Other exceptions are caught and printed.
- The returned frame uses OpenCV BGR color ordering.
- The method does not call `streamon()` automatically.

### `rotate_camera(angle)`

**Description**

Sends a camera angle command while the drone is flying, waits `abs(angle / 40)` seconds, then sends a stop command.

**Parameters**

| Name | Description |
| --- | --- |
| `angle` | Camera angle command and duration input. |

**Return value**

Returns `None`.

**Example usage**

```python
drone.take_off()
drone.rotate_camera(30)
drone.rotate_camera(-30)
```

**Notes and limitations**

- Requires `is_flying` to be `True`.
- The method sends the provided `angle` as `cameraangle`.
- The code does not validate camera angle range.
- The code does not verify the final camera position.

## See Also

- [Getting Started](getting-started.md)
- [Camera and Video](camera.md)
- [Examples](examples.md)
- [Troubleshooting](troubleshooting.md)
