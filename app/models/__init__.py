from gino import Gino
from sqlalchemy.dialects.postgresql import UUID


db = Gino()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(31), nullable=False, unique=True)
    balance = db.Column(db.Numeric(12, 2), nullable=False)

    __table_args__ = (db.CheckConstraint("balance >= 0"),)


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(UUID, unique=True, index=True, nullable=False)
    created = db.Column(
        db.TIMESTAMP,
        server_default=db.func.now(),
        nullable=False,
    )
    type = db.Column(db.String(15), nullable=False)
    old_balance = db.Column(db.Numeric(12, 2), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = db.Column(
        db.TIMESTAMP,
        nullable=False,
    )

    __table_args__ = (
        db.CheckConstraint("amount > 0"),
        db.CheckConstraint("type = 'DEPOSIT' or type = 'WITHDRAW'"),
    )
