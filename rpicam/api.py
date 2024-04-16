from redis import Redis
import rpicam

from flask import Blueprint, make_response

r = Redis("127.0.0.1", port=6379)

blueprint = Blueprint(name="devices", import_name=__name__)


@blueprint.route("/status", methods=["GET"])
def status():
    return {"status": "ok"}


@blueprint.route("/capture", methods=["GET"])
def capture():
    rpicam.capture_and_send(1, r)
    return {"status": "ok"}


@blueprint.route("/image<id>.jpg")
def get_image(id):
    resp = rpicam.get_from_redis(id, r)
    response = make_response(resp["image"])
    response.headers.set("Content-Type", "image/jpeg")
    return response
