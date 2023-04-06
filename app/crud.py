from datetime import datetime
from decimal import Decimal

from gino.crud import CRUDModel
from aiohttp import web
from sqlalchemy import and_

from models import User, Transaction, db


async def create_user(data: dict) -> CRUDModel:
    user = await User.select("id").where(User.name == data.get("name")).gino.first()
    if user:
        raise web.HTTPBadRequest(reason="name already exists")
    user = await User.create(name=data.get("name"), balance=Decimal("0.00"))
    user.balance = str(user.balance)
    return user


async def get_user(user_id: int, date: str | None = None) -> CRUDModel:
    user = await User.get(user_id)
    if not user:
        raise web.HTTPNotFound()
    if date:
        balance = await _get_user_balance_on_date(user.id, date)
        user.balance = balance
    user.balance = str(user.balance)
    return user


async def create_transaction(data: dict) -> CRUDModel:
    # check user exists
    user_id = int(data["user_id"])
    user = await User.get(user_id)
    if not user:
        raise web.HTTPBadRequest(reason="user not found")

    # check idempotent transaction
    transaction = await Transaction.query.where(
        Transaction.uid == data["uid"]
    ).gino.first()
    if transaction:
        return _jsonable_transaction(transaction)

    amount = Decimal(data["amount"])
    money_vector = amount if data["type"] == "DEPOSIT" else -amount
    new_balance = Decimal(user.balance) + money_vector

    if new_balance < 0:
        raise web.HTTPPaymentRequired(reason="not enough balance")

    # executing
    async with db.transaction():
        transaction = await Transaction.create(
            user_id=user_id,
            type=data["type"],
            amount=amount,
            old_balance=user.balance,
            uid=data["uid"],
            timestamp=_get_datetime(data["timestamp"]),
        )
        await user.update(balance=new_balance).apply()

    return _jsonable_transaction(transaction)


async def get_transaction(transaction_uid: int) -> CRUDModel:
    transaction = await Transaction.query.where(
        Transaction.uid == transaction_uid
    ).gino.first()
    if transaction is None:
        raise web.HTTPNotFound()
    return _jsonable_transaction(transaction)


def _jsonable_transaction(transaction: CRUDModel) -> CRUDModel:
    transaction.amount = str(transaction.amount)
    transaction.old_balance = str(transaction.old_balance)
    transaction.uid = str(transaction.uid)
    transaction.created = str(transaction.created)
    transaction.timestamp = str(transaction.timestamp)
    return transaction


async def _get_user_balance_on_date(user_id: int, date: str) -> Decimal:
    # Не знаю как сделать через гино, заджоинить таблицу, обычно юзаю алхимию
    date = _get_datetime(date)
    transaction = (
        await Transaction.select("old_balance")
        .where(and_(Transaction.user_id == user_id, Transaction.timestamp >= date))
        .gino.first()
    )
    return transaction and transaction.old_balance or Decimal("0.00")


def _get_datetime(date: str) -> datetime:
    try:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
    except:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
