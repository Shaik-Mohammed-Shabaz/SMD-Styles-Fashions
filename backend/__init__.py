from flask import Flask

from .config import Config
from .database import db


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static"
    )

    app.config.from_object(Config)

    db.init_app(app)
    from .models.user import User
    from .models.product import Product
    from .models.wishlist import Wishlist
    from .models.password_reset_token import PasswordResetToken
    from .models.order import Order
    from .models.order_item import OrderItem

    from .routes.main import main
    app.register_blueprint(main)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app