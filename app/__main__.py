import logging

import uvloop
from aiohttp import web

from app import init_app


def main() -> None:
    uvloop.install()
    app = init_app()
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, host=app["config"].HOST, port=app["config"].PORT)


if __name__ == "__main__":
    main()
