
import cv2
import numpy as np

cap = cv2.VideoCapture("http://10.49.238.188:8080/video")
background = None

while True:
    ret, frame = cap.read()

    if not ret:
        print("Camera not connected")
        break

    raw = frame.copy()
    h, w = frame.shape[:2]

    # Detect blue pen lines
    hsv = cv2.cvtColor(raw, cv2.COLOR_BGR2HSV)
    blue = cv2.inRange(
        hsv, np.array([90, 40, 30]),
        np.array([140, 255, 255])
    )

    blue = cv2.morphologyEx(
        blue, cv2.MORPH_OPEN,
        np.ones((3, 3), np.uint8)
    )

    edges = cv2.Canny(blue, 50, 150)

    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, 60,
        minLineLength=int(h * 0.18),
        maxLineGap=40
    )

    candidates = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = np.array(line).reshape(-1)[:4]

            if abs(y2-y1) > 0 and abs(x2-x1) < abs(y2-y1)*0.45:
                length = np.hypot(x2-x1, y2-y1)
                candidates.append((length, x1, y1, x2, y2))

    candidates.sort(reverse=True)
    chosen = []

    for length, x1, y1, x2, y2 in candidates:
        xm = (x1+x2)/2

        if all(abs(xm-(a[1]+a[3])/2) > w*0.08 for a in chosen):
            chosen.append((length, x1, y1, x2, y2))

        if len(chosen) == 2:
            break

    if len(chosen) == 2:
        chosen.sort(key=lambda a: (a[1]+a[3])/2)

        def extend(line):
            _, ax, ay, bx, by = line
            slope = (bx-ax)/(by-ay)
            return (
                int(ax-slope*ay), 0,
                int(ax+slope*(h-ay)), h
            )

        left = extend(chosen[0])
        right = extend(chosen[1])

        cv2.line(frame, left[:2], left[2:], (0, 255, 0), 3)
        cv2.line(frame, right[:2], right[2:], (0, 255, 0), 3)

        # Label the three regions
        y = int(h*0.55)
        xl = int(left[0] + (left[2]-left[0])*0.55)
        xr = int(right[0] + (right[2]-right[0])*0.55)

        cv2.putText(frame, "LANE 1", (max(10, xl//2), y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.putText(frame, "LANE 2", ((xl+xr)//2, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.putText(frame, "LANE 3 - PARKING",
                    (min(w-180, (xr+w)//2), y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Count objects only in Lanes 1 and 2
        if background is not None:
            diff = cv2.absdiff(background, raw)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            _, mask = cv2.threshold(
                gray, 35, 255, cv2.THRESH_BINARY
            )

            mask = cv2.morphologyEx(
                mask, cv2.MORPH_OPEN,
                np.ones((3, 3), np.uint8)
            )

            mask = cv2.morphologyEx(
                mask, cv2.MORPH_CLOSE,
                np.ones((9, 9), np.uint8)
            )

            lane1 = np.array([
                [0, 0], [left[0], 0],
                [left[2], h], [0, h]
            ], dtype=np.int32)

            lane2 = np.array([
                [left[0], 0], [right[0], 0],
                [right[2], h], [left[2], h]
            ], dtype=np.int32)

            roi = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(roi, [lane1, lane2], 255)
            mask = cv2.bitwise_and(mask, roi)

            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            count = 0

            for c in contours:
                if cv2.contourArea(c) < 500:
                    continue

                x, y0, bw, bh = cv2.boundingRect(c)
                cx, cy = x+bw//2, y0+bh//2

                in1 = cv2.pointPolygonTest(
                    lane1, (float(cx), float(cy)), False
                ) >= 0

                in2 = cv2.pointPolygonTest(
                    lane2, (float(cx), float(cy)), False
                ) >= 0

                if in1 or in2:
                    count += 1
                    cv2.rectangle(
                        frame, (x, y0), (x+bw, y0+bh),
                        (0, 255, 0), 2
                    )

            traffic = "LOW" if count <= 3 else "HIGH"

            cv2.putText(
                frame, f"Objects: {count} | {traffic}",
                (20, 70), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 255, 255), 2
            )

            print(f"Objects: {count} | Traffic: {traffic}")

        else:
            cv2.putText(
                frame, "Empty lanes? Press B to set background",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 255, 255), 2
            )

    else:
        cv2.putText(
            frame, "Lane boundaries not found",
            (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 0, 255), 2
        )

    cv2.imshow("Three Lane Detection", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('b'):
        background = raw.copy()
        print("Background captured! Keep camera still.")

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()