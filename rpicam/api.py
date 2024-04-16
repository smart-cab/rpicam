import rpicam
import argparse

from redis import Redis
from flask import Blueprint, abort, make_response


def get_redis_ip():
    REDIS_IP_FILENAME = "redis_ip"
    with open(f'{"/".join(__file__.split("/")[:-2])}/{REDIS_IP_FILENAME}') as file:
        return file.read().rstrip()


r = Redis(get_redis_ip(), port=6379)

blueprint = Blueprint(name="devices", import_name=__name__)


@blueprint.route("/status", methods=["GET"])
def status():
    return {"status": "ok"}


@blueprint.route("/capture", methods=["GET"])
def capture():
    id = rpicam.capture_and_send(r)
    return {"filename": f"image{id}.jpg"}


@blueprint.route("/image<id>.jpg")
def get_image(id):
    resp = rpicam.get_from_redis(f"webcam:{id}", r)
    if resp is None:
        abort(404)
    response = make_response(resp["image"])
    response.headers.set("Content-Type", "image/jpeg")
    return response
