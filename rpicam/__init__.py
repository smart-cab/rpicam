import cv2
import base64

from redis import Redis
from datetime import datetime, timezone


def send_to_redis(id, image_as_base64: str, r: Redis):
    r.hset(
        f"webcam:{id}",
        mapping={
            "image": image_as_base64,
            "datetime": datetime.now(timezone.utc).timestamp() * 1000,
        },
    )


def get_from_redis(id: str, r: Redis):
    if (image := r.hget(f"webcam:{id}", "image")) is None or (
        dt := r.hget(f"webcam:{id}", "datetime")
    ) is None:
        return

    image = base64.b64decode(image)
    dt = datetime.fromtimestamp(float(dt) / 1000)

    return {"image": image, "datetime": dt}


def cv2_image_to_bytes(image):
    retval, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("ascii")


def capture_and_send(id, r):
    cap = cv2.VideoCapture(0)
    retval, image = cap.read()
    image = cv2_image_to_bytes(image)
    send_to_redis(id, image, r)
    cap.release()
