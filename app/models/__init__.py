from gino import Gino

db = Gino()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(31), nullable=False)
    balance = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.CheckConstraint("balance >= 0"),)


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.TIMESTAMP,
        server_default=db.func.now(),
        onupdate=db.func.current_timestamp(),
        nullable=False,
    )
    type = db.Column(db.String(15), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.CheckConstraint("amount > 0"),
        db.CheckConstraint("type = 'DEPOSIT' or type = 'WITHDRAW'"),
    )
