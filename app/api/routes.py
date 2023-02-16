from aiohttp import web, web_request

from models import User, Transaction, db


def validate_post_fields(*fields, data):
    """
    Представим что я юзаю pydantic
    """
    for field in fields:
        if field not in data:
            raise web.HTTPBadRequest()


async def create_user(request: web_request.Request):
    data = await request.post()
    data = dict(data)
    validate_post_fields("name", data=data)
    user = await User.create(name=data.get("name"), balance=0)
    return web.json_response(user.to_dict(), status=web.HTTPCreated.status_code)


async def get_user_balance(request: web_request.Request):
    user_id = int(request.match_info.get("id"))
    user = await User.select("balance").where(User.id == user_id).gino.first()
    if user is None:
        raise web.HTTPBadRequest()
    return web.json_response({"balance": user.balance})


async def add_transaction(request: web_request.Request):
    data = await request.post()
    data = dict(data)
    validate_post_fields("user_id", "amount", "type", data=data)

    # fields
    type = data.get("type").upper()
    user_id = int(data.get("user_id"))
    if type == "DEPOSIT":
        money = int(data.get("amount"))
    else:
        money = -int(data.get("amount"))

    # Check user and his balance
    user = await User.select("balance").where(User.id == user_id).gino.first()
    if user is None:
        raise web.HTTPBadRequest()
    balance = user.balance
    if balance + int(money) < 0:
        raise web.HTTPBadRequest()

    # executing
    async with db.transaction():
        new_balance = balance + money
        await user.update(balance=new_balance).apply()
        await Transaction.create(user_id=user_id, type=type, amount=abs(money))

    return web.json_response(data)


async def get_transaction(request: web_request.Request):
    tr_id = int(request.match_info.get("id"))
    transaction = await Transaction.query.where(User.id == tr_id).gino.first()
    if transaction is None:
        raise web.HTTPBadRequest()
    data = transaction.to_dict()
    data["created"] = str(data.get("created"))
    return web.json_response(data)


def add_routes(app):
    app.router.add_route("POST", r"/v1/user", create_user, name="create_user")
    app.router.add_route(
        "GET", r"/v1/user/{id}/balance", get_user_balance, name="get_user_balance"
    )
    app.router.add_route(
        "POST", r"/v1/transaction", add_transaction, name="add_transaction"
    )
    app.router.add_route(
        "GET", r"/v1/transaction/{id}", get_transaction, name="incoming_transaction"
    )
