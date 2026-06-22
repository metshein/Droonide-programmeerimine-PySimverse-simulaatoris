# Troubleshooting

This page lists issues that can be explained from the observed source code.

For the complete API, see [Drone API Reference](drone-api.md). For video-specific behavior, see [Camera and Video](camera.md).

## `connect()` Fails or Hangs

Observed behavior:

- `connect()` binds the command socket to `tcp://{host}:{cmd_port}`.
- The default command address is `tcp://*:5550`.

Possible causes:

- Another process is already bound to the command port.
- A previous script did not shut down cleanly.
- The simulator is not running or is using different ports.

Try checking the port:

```python
from pysimverse import Drone

print(Drone.is_port_available(5550))
```

## `drone.is_port_available(5550)` Raises `TypeError`

`is_port_available()` is defined as:

```python
def is_port_available(port):
```

It does not accept `self`. Call it on the class:

```python
Drone.is_port_available(5550)
```

## Movement Prints `Take off the drone first.`

Movement methods only send commands when `drone.is_flying` is `True`.

Call `take_off()` first:

```python
drone.take_off()
drone.move_forward(100)
```

Observed affected methods:

- `move_forward()`
- `move_backward()`
- `move_right()`
- `move_left()`
- `move_up()`
- `move_down()`
- `rotate()`
- `rotate_camera()`

## Movement Raises `ZeroDivisionError`

Movement methods calculate delay with:

```python
delay = distance / self.speed
```

If you call `set_speed(0)`, movement methods can raise `ZeroDivisionError`.

Use a non-zero speed:

```python
drone.set_speed(20)
```

`take_off()` can also raise `ZeroDivisionError` if `takeoff_speed=0`.

## Movement Distance Is Not Accurate

The code estimates movement duration from `distance / speed`, sends a command, sleeps, and stops.

It does not:

- Read position telemetry.
- Confirm the actual distance traveled.
- Correct drift or simulator physics.

Treat `distance` as a timing input for the simulator rather than a guaranteed real-world distance.

## `get_battery()` Does Not Return a Number

Observed source behavior:

```python
message = self.state_socket.recv_string()
print(f"Received Battery Data: {message}%")
battery_percentage = float(message)
time.sleep(1)
```

The local variable `battery_percentage` is not returned. The method returns `None`.

## `get_battery()` Blocks

`get_battery()` uses:

```python
self.state_socket.recv_string()
```

This is a blocking receive. It waits until a telemetry message arrives. Make sure the simulator is running and publishing state data to the configured state port.

## `get_battery()` Raises `ValueError`

The received telemetry string is parsed with:

```python
float(message)
```

If the simulator sends a non-numeric message, parsing can fail.

## `get_frame()` Returns `(None, False)`

Possible causes:

- `streamon()` was not called.
- The simulator is not publishing video frames.
- The video port does not match the simulator.
- No frame arrived within the 10 ms polling window.

Minimal check:

```python
drone.streamon()
frame, ok = drone.get_frame()
print(ok, frame is not None)
```

## OpenCV Window Does Not Update

When displaying frames with OpenCV, call `cv2.waitKey()`.

```python
if ok:
    cv2.imshow("Drone Camera", frame)
cv2.waitKey(1)
```

`shutdown()` calls `cv2.destroyAllWindows()`.

## Video Colors Look Swapped

`get_frame()` decodes images with OpenCV. OpenCV frames are usually BGR, not RGB.

If another library expects RGB, convert the frame:

```python
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
```

## Reusing a Drone After `shutdown()`

`shutdown()` closes sockets and terminates the ZeroMQ context.

Create a new `Drone` instance after shutdown:

```python
drone = Drone()
drone.connect()
```

## Commands Print Payloads

`send_rc_control()` prints every successful command:

```text
Published RC control data: {...}
```

This is normal observed behavior in the source code.

## Related Pages

- [Getting Started](getting-started.md)
- [Drone API Reference](drone-api.md)
- [Camera and Video](camera.md)
- [Examples](examples.md)
