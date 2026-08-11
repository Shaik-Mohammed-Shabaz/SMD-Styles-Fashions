from database import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Float, nullable=False)

    category = db.Column(db.String(100), nullable=False)

    image = db.Column(db.String(255), nullable=False)

    stock = db.Column(db.Integer, default=0)

    is_featured = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Product {self.name}>"