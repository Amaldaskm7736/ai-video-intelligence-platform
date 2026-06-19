import cv2
import numpy as np
from datetime import datetime
import os

# Create snapshots folder
SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

class ZoneMonitor:
    def __init__(self):
        self.zones = [
            {
                "name": "Restricted Zone 1",
                "points": np.array([[100, 100], [400, 100], [400, 350], [100, 350]]),
                "color": (0, 0, 255),
                "alert_color": (0, 0, 180),
                "triggered": False
            }
        ]
        self.alerts = []
        self.last_snapshot_time = {}  # prevent too many snapshots

    def save_snapshot(self, frame, alert):
        """Save frame as snapshot when alert triggers"""
        object_id = alert["object_id"]
        now = datetime.now()

        # only save snapshot once every 5 seconds per object
        last = self.last_snapshot_time.get(object_id)
        if last and (now - last).seconds < 5:
            return None

        self.last_snapshot_time[object_id] = now
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"{SNAPSHOT_DIR}/alert_{alert['class']}_{object_id}_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Snapshot saved: {filename}")
        return filename

    def check_intrusion(self, tracked_objects, frame=None):
        current_alerts = []

        for zone in self.zones:
            zone["triggered"] = False

            for obj in tracked_objects:
                cx, cy = obj["center"]
                result = cv2.pointPolygonTest(zone["points"], (cx, cy), False)

                if result >= 0:
                    zone["triggered"] = True
                    alert = {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "object_id": obj["id"],
                        "class": obj["class"],
                        "zone": zone["name"],
                        "confidence": obj.get("confidence", 0.0),
                        "bbox": obj.get("bbox", []),
                        "snapshot": None
                    }

                    # save snapshot if frame provided
                    if frame is not None:
                        snapshot_path = self.save_snapshot(frame, alert)
                        alert["snapshot"] = snapshot_path

                    current_alerts.append(alert)
                    self.alerts.append(alert)
                    self.alerts = self.alerts[-20:]

        return current_alerts

    def draw_zones(self, frame):
        for zone in self.zones:
            color = zone["alert_color"] if zone["triggered"] else zone["color"]
            overlay = frame.copy()
            cv2.fillPoly(overlay, [zone["points"]], color)
            cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
            cv2.polylines(frame, [zone["points"]], True, color, 2)
            x, y = zone["points"][0]
            cv2.putText(frame, zone["name"], (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        return frame

    def draw_alerts(self, frame, current_alerts):
        if current_alerts:
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (0, 0, 255), -1)
            alert = current_alerts[0]
            msg = f"ALERT! {alert['class']} #{alert['object_id']} in {alert['zone']} at {alert['time']}"
            cv2.putText(frame, msg, (10, 33),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        for i, alert in enumerate(reversed(self.alerts[-5:])):
            snap = "📸" if alert.get("snapshot") else ""
            msg = f"{alert['time']} | {alert['class']} #{alert['object_id']} | {alert['zone']} {snap}"
            y = frame.shape[0] - 20 - (i * 22)
            cv2.putText(frame, msg, (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        return frame