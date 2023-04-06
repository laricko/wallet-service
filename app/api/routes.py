import asyncio

from aiohttp import web, web_request

import crud


async def get_post_data(*fields, request: web_request.Request) -> dict:
    """
    Представим что я юзаю pydantic
    """
    data = await request.post()
    data = dict(data)
    for field in fields:
        if field not in data:
            raise web.HTTPBadRequest(reason=f"{field} is required")
    return data


async def create_user(request: web_request.Request):
    data = await get_post_data("name", request=request)
    user = await crud.create_user(data)
    return web.json_response(user.to_dict(), status=web.HTTPCreated.status_code)


async def get_user(request: web_request.Request):
    user_id = int(request.match_info.get("id"))
    date = request.query.get("date")
    user = await crud.get_user(user_id, date)
    return web.json_response(user.to_dict())


async def add_transaction(request: web_request.Request):
    data = await get_post_data(
        "uid", "user_id", "amount", "type", "timestamp", request=request
    )
    await crud.create_transaction(data)
    notify_transaction(data)
    return web.json_response(data)


async def get_transaction(request: web_request.Request):
    tr_uid = request.match_info.get("uid")
    transaction = await crud.get_transaction(tr_uid)
    return web.json_response(transaction.to_dict())


def notify_transaction(data: dict) -> None:
    # Notify transaction complited
    # connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    # channel = connection.channel()
    # channel.queue_bind(
    #     QUEUE_NAME_TO_SOME_SERVICE, EXCHANGER, ROUTING_KEY_TO_SOME_SERVICE
    # )
    # channel.basic_publish(
    #     EXCHANGER, ROUTING_KEY_TO_SOME_SERVICE, json.dumps(data)).encode()
    # )
    return


def add_routes(app):
    app.router.add_route("POST", r"/v1/user", create_user, name="create_user")
    app.router.add_route("GET", r"/v1/user/{id}", get_user, name="get_user")
    app.router.add_route(
        "POST", r"/v1/transaction", add_transaction, name="add_transaction"
    )
    app.router.add_route(
        "GET", r"/v1/transaction/{uid}", get_transaction, name="incoming_transaction"
    )
