import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# MediaPipe klassid
BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

# Käe tuvastaja seadistamine
options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

# Loome käe tuvastaja
landmarker = HandLandmarker.create_from_options(options)

# Avame veebikaamera
cap = cv2.VideoCapture(0)

# MediaPipe vajab kasvavat ajatemplite loendurit
timestamp_ms = 0

while True:

    frame = cap.read()[1]

    if frame is None:
        continue

    timestamp_ms += 1

    # OpenCV kasutab BGR värviruumi
    # MediaPipe vajab RGB pilti
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Loome MediaPipe pildiobjekti
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    # Käe tuvastamine
    result = landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )

    # Joonistame kõik käepunktid
    if result.hand_landmarks:

        for hand in result.hand_landmarks:

            for point in hand:

                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

    cv2.imshow(
        "Hand Detection",
        frame
    )

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()