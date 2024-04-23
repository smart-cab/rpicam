import cv2
import base64

from redis import Redis
from datetime import datetime, timezone


def append_to_redis(image_as_base64: str, r: Redis) -> int:
    id = r.scard("webcams") + 1
    name = f"webcam:{id}"
    r.sadd("webcams", name)
    r.hset(
        name,
        mapping={
            "image": image_as_base64,
            "datetime": datetime.now(timezone.utc).timestamp() * 1000,
        },
    )
    return id


def get_from_redis(name: str, r: Redis):
    if (image := r.hget(name, "image")) is None or (
        dt := r.hget(name, "datetime")
    ) is None:
        return

    image = base64.b64decode(image)
    dt = datetime.fromtimestamp(float(dt) / 1000)

    return {"image": image, "datetime": dt}


def get_last_nth_from_redis(n: int, r: Redis):
    print("000000000000")
    return [
        get_from_redis(name, r)
        for name in r.sort("webcams", start=0, num=n, by="*->timestamp", desc=True)
    ]


def cv2_image_to_bytes(image):
    retval, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("ascii")


def capture_and_send(r) -> int:
    cap = cv2.VideoCapture(0)
    retval, image = cap.read()
    image = cv2_image_to_bytes(image)
    cap.release()
    return append_to_redis(image, r)
