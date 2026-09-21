from backend.database import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    order_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    customer_email = db.Column(
        db.String(120),
        nullable=False
    )

    customer_phone = db.Column(
        db.String(20),
        nullable=False
    )

    delivery_address = db.Column(
        db.Text,
        nullable=False
    )

    subtotal = db.Column(
        db.Float,
        nullable=False
    )

    discount = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    order_status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False
    )

    payment_status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = db.relationship(
        "User",
        backref=db.backref("orders", lazy=True)
    )

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order {self.order_number}>"