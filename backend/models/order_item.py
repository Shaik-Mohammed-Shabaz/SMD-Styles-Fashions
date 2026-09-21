from backend.database import db


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    product_name = db.Column(
        db.String(150),
        nullable=False
    )

    size = db.Column(
        db.String(20),
        nullable=True
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    unit_price = db.Column(
        db.Float,
        nullable=False
    )

    subtotal = db.Column(
        db.Float,
        nullable=False
    )

    product = db.relationship(
        "Product",
        backref=db.backref("order_items", lazy=True)
    )

    def __repr__(self):
        return f"<OrderItem {self.product_name}>"