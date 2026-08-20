from backend.database import db
from datetime import datetime


class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref("wishlist_items", lazy=True)
    )

    product = db.relationship(
        "Product",
        backref=db.backref("wishlist_items", lazy=True)
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "product_id",
            name="unique_user_product_wishlist"
        ),
    )

    def __repr__(self):
        return f"<Wishlist User {self.user_id} Product {self.product_id}>"