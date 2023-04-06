from aiohttp import web

from models import db


async def init_db(app: web.Application):
    await app["db"].set_bind(app["config"].DATABASE_URI)
    await app["db"].gino.create_all()
