from ultralytics import YOLO
import cv2

class ObjectTracker:
    def __init__(self, model_path="yolov8n.pt", confidence=0.5):
        self.model = YOLO(model_path)
        self.confidence = confidence
        # track_history stores last 30 positions for each object ID
        self.track_history = {}

    def track(self, frame):
        results = self.model.track(
            frame,
            conf=self.confidence,
            persist=True,       # keeps IDs consistent across frames
            tracker="bytetrack.yaml",
            verbose=False
        )
        tracked_objects = []

        for r in results:
            if r.boxes.id is None:
                continue  # no tracks detected this frame

            for box, track_id in zip(r.boxes, r.boxes.id):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                tid = int(track_id)

                # store center point history for trail drawing
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                if tid not in self.track_history:
                    self.track_history[tid] = []
                self.track_history[tid].append((cx, cy))
                # keep only last 30 points
                self.track_history[tid] = self.track_history[tid][-30:]

                tracked_objects.append({
                    "id": tid,
                    "bbox": [x1, y1, x2, y2],
                    "class": class_name,
                    "confidence": round(confidence, 2),
                    "center": (cx, cy)
                })

        return tracked_objects

    def draw_tracks(self, frame, tracked_objects):
        for obj in tracked_objects:
            x1, y1, x2, y2 = obj["bbox"]
            tid = obj["id"]
            label = f"{obj['class']} #{tid} ({obj['confidence']})"

            # draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # draw label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - 25), (x1 + w, y1), (0, 255, 0), -1)
            cv2.putText(frame, label, (x1, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            # draw movement trail
            history = self.track_history.get(tid, [])
            for i in range(1, len(history)):
                alpha = i / len(history)
                color = (0, int(255 * alpha), int(255 * (1 - alpha)))
                cv2.line(frame, history[i - 1], history[i], color, 2)

        return frame