from pysimverse import Drone
import cv2
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = python.BaseOptions
PoseLandmarker = vision.PoseLandmarker
PoseLandmarkerOptions = vision.PoseLandmarkerOptions
VisionRunningMode = vision.RunningMode

POSE_CONNECTIONS = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (24, 26), (26, 28)]

drone = Drone()

drone.connect()
drone.take_off()

camera = cv2.VideoCapture(0)

options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path="pose_landmarker_lite.task"), running_mode=VisionRunningMode.VIDEO, num_poses=1)

landmarker = PoseLandmarker.create_from_options(options)

timestamp_ms = 0

base_hip_y = None
jump_count = 0
last_jump_time = 0

while True:

    success, frame = camera.read()

    if not success:
        continue

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = landmarker.detect_for_video(mp_image, timestamp_ms)

    timestamp_ms += 33

    if result.pose_landmarks:

        landmarks = result.pose_landmarks[0]

        for start, end in POSE_CONNECTIONS:

            x1 = int(landmarks[start].x * frame.shape[1])
            y1 = int(landmarks[start].y * frame.shape[0])

            x2 = int(landmarks[end].x * frame.shape[1])
            y2 = int(landmarks[end].y * frame.shape[0])

            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        for landmark in landmarks:

            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])

            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        left_hip = landmarks[23]
        right_hip = landmarks[24]

        hip_y = (left_hip.y + right_hip.y) / 2

        if base_hip_y is None:
            base_hip_y = hip_y

        current_time = time.time()

        jump_detected = hip_y < base_hip_y - 0.05

        if jump_detected and current_time - last_jump_time > 1:

            jump_count += 1
            last_jump_time = current_time

            print("HÜPE")

            drone.move_forward(0.5)

        cv2.putText(frame, f"HIP: {hip_y:.3f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"BASE: {base_hip_y:.3f}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"JUMPS: {jump_count}", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        if jump_detected:
            cv2.putText(frame, "JUMP", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "NO JUMP", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    cv2.imshow("Body Follower", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()

drone.land()
