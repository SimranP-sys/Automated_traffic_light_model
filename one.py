import cv2
import numpy as np

import serial
import time

esp = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)

last_sent = None

cap = cv2.VideoCapture("http://10.49.238.188:8080/video")

background = None

# Wait for the first camera frame to get image dimensions
ret, frame = cap.read()

if not ret:
    print("Camera not connected")
    cap.release()
    raise SystemExit

h, w = frame.shape[:2]
print("Frame size:", w, "x", h)

# Lane boundary points, relative to the image dimensions.
# These approximate the paper boundaries in your photo.
# Adjust them after viewing the live camera window.

# Normalized lane boundary coordinates (x, y)

top_left = (0.28, 0.22)
top_middle = (0.49, 0.23)
top_right = (0.70, 0.22)

bottom_left = (0.00, 0.88)
bottom_middle = (0.58, 0.88)
bottom_right = (0.95, 0.88)


def point(p):
    return (int(p[0] * w), int(p[1] * h))


# Four corners of each lane
lane1 = np.array([
    point(top_left),
    point(top_middle),
    point(bottom_middle),
    point(bottom_left)
], dtype=np.int32)

lane2 = np.array([
    point(top_middle),
    point(top_right),
    point(bottom_right),
    point(bottom_middle)
], dtype=np.int32)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Camera feed lost")
        break

    h, w = frame.shape[:2]
    raw = frame.copy()

    # Draw lane boundaries
    cv2.polylines(frame, [lane1], True, (0, 255, 0), 2)
    cv2.polylines(frame, [lane2], True, (0, 255, 0), 2)

    cv2.putText(frame, "LANE 1", point((0.20, 0.55)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.putText(frame, "LANE 2", point((0.55, 0.55)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    key = cv2.waitKey(1) & 0xFF

    # Capture empty road
    if key == ord('b'):
        background = raw.copy()
        print("Empty-road background captured!")

    if background is not None:

        # Difference between current frame and empty road
        diff = cv2.absdiff(background, raw)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        _, mask = cv2.threshold(
            gray, 30, 255, cv2.THRESH_BINARY
        )

        mask = cv2.morphologyEx(
            mask, cv2.MORPH_OPEN,
            np.ones((3, 3), np.uint8)
        )

        mask = cv2.morphologyEx(
            mask, cv2.MORPH_CLOSE,
            np.ones((9, 9), np.uint8)
        )

        # Keep pixels only inside Lane 1 and Lane 2
        roi = np.zeros((h, w), dtype=np.uint8)

        cv2.fillPoly(roi, [lane1, lane2], 255)

        mask = cv2.bitwise_and(mask, roi)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        count1 = 0
        count2 = 0

        for c in contours:

            area = cv2.contourArea(c)

            if area < 500:
                continue

            x, y, bw, bh = cv2.boundingRect(c)

            cx = x + bw // 2
            cy = y + bh // 2

            inside1 = cv2.pointPolygonTest(
                lane1, (float(cx), float(cy)), False
            ) >= 0

            inside2 = cv2.pointPolygonTest(
                lane2, (float(cx), float(cy)), False
            ) >= 0

            if inside1:
                count1 += 1

            elif inside2:
                count2 += 1

            else:
                continue

            cv2.rectangle(
                frame, (x, y), (x + bw, y + bh),
                (0, 255, 0), 2
            )

        total = count1 + count2

        traffic = "LOW" if total <= 5 else "HIGH"
        
        if traffic != last_sent:
            if traffic == "HIGH":
               esp.write(b'H')
            else:
               esp.write(b'L')

        last_sent = traffic
        print("Sent to ESP32:", traffic)


        cv2.putText(
            frame,
            f"Lane 1: {count1}  Lane 2: {count2}",
            (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 255), 2
        )

        cv2.putText(
            frame,
            f"Total: {total} | Traffic: {traffic}",
            (20, 70), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 255), 2
        )

    else:
        cv2.putText(
            frame, "Empty road? Press B",
            (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 255), 2
        )

    cv2.imshow("Two-Lane Traffic Detection", frame)

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
