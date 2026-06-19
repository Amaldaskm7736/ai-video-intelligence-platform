import cv2
import sys
import httpx
import asyncio
from tracker import ObjectTracker
from zone_monitor import ZoneMonitor

# Backend URL
BACKEND_URL = "http://localhost:8000"

def send_alert(alert: dict):
    """Send alert to FastAPI backend"""
    try:
        with httpx.Client() as client:
            # Save incident to database
            client.post(
                f"{BACKEND_URL}/incidents/",
                json={
                    "camera_id": 1,
                    "object_class": alert["class"],
                    "object_id": alert["object_id"],
                    "zone_name": alert["zone"],
                    "confidence": alert["confidence"],
                    "bbox": alert.get("bbox", [])
                },
                timeout=2.0
            )
            # Broadcast alert via WebSocket
            client.post(
                f"{BACKEND_URL}/alerts/trigger",
                json={
                    "type": "alert",
                    "object_id": alert["object_id"],
                    "object_class": alert["class"],
                    "zone_name": alert["zone"],
                    "confidence": alert["confidence"],
                    "timestamp": alert["time"],
                    "camera_id": 1
                },
                timeout=2.0
            )
    except Exception as e:
        print(f"Backend not reachable: {e}")

def main():
    tracker = ObjectTracker()
    zone_monitor = ZoneMonitor()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Cannot open webcam")
        return

    print("Zone monitoring active. Press Q to quit.")
    print("Alerts will be saved to database automatically!")

    # track which alerts already sent (avoid duplicates)
    sent_alerts = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Step 1: track objects
        tracked_objects = tracker.track(frame)

        # Step 2: draw zones
        frame = zone_monitor.draw_zones(frame)

        # Step 3: check intrusions
        current_alerts = zone_monitor.check_intrusion(tracked_objects, frame)

        # Step 4: draw tracking boxes
        frame = tracker.draw_tracks(frame, tracked_objects)

        # Step 5: draw alerts on frame
        frame = zone_monitor.draw_alerts(frame, current_alerts)

        # Step 6: send new alerts to backend
        for alert in current_alerts:
            alert_key = f"{alert['object_id']}_{alert['zone']}_{alert['time']}"
            if alert_key not in sent_alerts:
                sent_alerts.add(alert_key)
                # find confidence for this object
                for obj in tracked_objects:
                    if obj["id"] == alert["object_id"]:
                        alert["confidence"] = obj["confidence"]
                        alert["bbox"] = obj["bbox"]
                        break
                send_alert(alert)
                print(f"ALERT saved! {alert['class']} #{alert['object_id']} in {alert['zone']}")

        # keep sent_alerts from growing too large
        if len(sent_alerts) > 100:
            sent_alerts = set(list(sent_alerts)[-50:])

        # show count
        cv2.putText(frame, f"Tracking: {len(tracked_objects)} objects", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Backend: Connected", (10, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("AI Video Intelligence", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()