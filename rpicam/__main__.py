import os
import ssl
import api
import logging
import multiprocessing
import gunicorn.app.base

from flask import Flask
from pathlib import Path
from flask_cors import CORS
from dotenv import find_dotenv, load_dotenv

BLUEPRINT_MODULES = {api}

PROD = os.getenv("PROD", "false") == "true"


def apply_blueprints(app: Flask):
    for module in BLUEPRINT_MODULES:
        app.register_blueprint(module.blueprint)


def running_within_docker() -> bool:
    cgroup = Path("/proc/self/cgroup")
    return (
        Path("/.dockerenv").is_file()
        or cgroup.is_file()
        and "docker" in cgroup.read_text()
    )


def make_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    app.config["DEBUG"] = not PROD
    app.config["ERROR_404_HELP"] = False

    CORS(app)
    apply_blueprints(app)

    logging.info("Application was created successfully")

    return app


class WSGIApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)
        self.cfg.set("cert_reqs", 0)

    def load(self):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.options['ssl_context'] = ssl_context
        return self.application


def main() -> None:
    load_dotenv(find_dotenv())

    logging.getLogger().setLevel(logging.DEBUG)

    WORKERS = (multiprocessing.cpu_count() * 2) + 1

    app = make_app()

    if PROD:
        logging.info("Running in production-mode - gunicorn server will be used")
        WSGIApplication(
            app,
            {
                "bind": f"0.0.0.0:5050",
                "workers": WORKERS,
                "certfile": "./certs/sch1357.ru.crt",
                "keyfile": "./certs/sch1357.ru.key",
            },
        ).run()
    else:
        logging.info("Running in development-mode - flask standard server will be used")
        app.run(host="0.0.0.0", port=5050, debug=True)


if __name__ == "__main__":
    main()
