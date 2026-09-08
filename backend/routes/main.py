from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.models.contact import Contact
from backend.models.user import User
from backend.models.product import Product
from backend.models.wishlist import Wishlist
from backend.database import db
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint("main", __name__)
@main.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    flash("Image is too large. Maximum file size is 5 MB.", "error")
    return redirect(url_for("main.admin_products"))

# ==========================
# Product Image Upload Settings
# ==========================

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "error")
            return redirect(url_for("main.login"))

        return view(*args, **kwargs)

    return wrapped_view

# ==========================
# Prevent Admin Page Caching
# ==========================

@main.after_request
def prevent_admin_cache(response):

    if request.path.startswith("/admin"):

        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response

@main.route("/")
def home():

    # Get featured products from database
    products = Product.query.filter_by(is_featured=True).all()

    # Get user's wishlist product IDs
    wishlist_product_ids = set()

    if session.get("user_id"):

        wishlist_product_ids = {
            item.product_id
            for item in Wishlist.query.filter_by(
                user_id=session["user_id"]
            ).all()
        }

    return render_template(
        "index.html",
        products=products,
        wishlist_product_ids=wishlist_product_ids
    )

@main.route("/shop")
def shop():

    # Get all products from database
    products = Product.query.order_by(Product.id.desc()).all()

    # Get user's wishlist product IDs
    wishlist_product_ids = set()

    if session.get("user_id"):

        wishlist_product_ids = {
            item.product_id
            for item in Wishlist.query.filter_by(
                user_id=session["user_id"]
            ).all()
        }

    return render_template(
        "shop.html",
        products=products,
        wishlist_product_ids=wishlist_product_ids
    )

# ==========================
# Wishlist
# ==========================

@main.route("/wishlist/toggle", methods=["POST"])
@login_required
def toggle_wishlist():

    product_id = request.form.get("product_id", type=int)

    if not product_id:
        return {"success": False, "message": "Invalid product."}, 400

    product = Product.query.get(product_id)

    if not product:
        return {"success": False, "message": "Product not found."}, 404

    existing_item = Wishlist.query.filter_by(
        user_id=session["user_id"],
        product_id=product_id
    ).first()

    if existing_item:
        db.session.delete(existing_item)
        db.session.commit()

        return {
            "success": True,
            "added": False,
            "message": "Removed from Wishlist"
        }

    wishlist_item = Wishlist(
        user_id=session["user_id"],
        product_id=product_id
    )

    db.session.add(wishlist_item)
    db.session.commit()

    return {
        "success": True,
        "added": True,
        "message": "Added to Wishlist"
    }


@main.route("/wishlist")
@login_required
def wishlist():

    wishlist_items = Wishlist.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Wishlist.created_at.desc()).all()

    return render_template(
        "pages/wishlist.html",
        wishlist_items=wishlist_items
    )

@main.route("/checkout")
@login_required
def checkout():
    return render_template("checkout.html")


@main.route("/success")
def success():
    return render_template("success.html")


@main.route("/cart")
def cart():
    return render_template("pages/cart.html")


@main.route("/product/<int:product_id>")
def product(product_id):

    product = Product.query.get_or_404(product_id)

    return render_template(
        "pages/product.html",
        product=product
    )


@main.route("/about")
def about():
    return render_template("pages/about.html")


@main.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        new_contact = Contact(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        db.session.add(new_contact)
        db.session.commit()

        flash("Your message has been sent successfully!", "success")

        return redirect(url_for("main.contact"))

    return render_template("pages/contact.html")


@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return redirect(url_for("main.login"))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password.", "error")
            return redirect(url_for("main.login"))

        if not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("main.login"))

        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_email"] = user.email

        flash("Login successful!", "success")

        return redirect(url_for("main.home"))

    return render_template("pages/login.html")

# ==========================
# Customer Account
# ==========================

@main.route("/account")
@login_required
def account():

    user = User.query.get_or_404(session["user_id"])

    wishlist_count = Wishlist.query.filter_by(
        user_id=session["user_id"]
    ).count()

    return render_template(
        "pages/account.html",
        user=user,
        wishlist_count=wishlist_count
    )

# ==========================
# Customer Change Password
# ==========================

@main.route("/account/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not current_password or not new_password or not confirm_password:
            flash("Please fill in all password fields.", "error")
            return redirect(url_for("main.change_password"))

        if not check_password_hash(user.password_hash, current_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("main.change_password"))

        if len(new_password) < 6:
            flash("New password must be at least 6 characters.", "error")
            return redirect(url_for("main.change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return redirect(url_for("main.change_password"))

        if check_password_hash(user.password_hash, new_password):
            flash("New password must be different from your current password.", "error")
            return redirect(url_for("main.change_password"))

        user.password_hash = generate_password_hash(new_password)

        db.session.commit()

        flash("Password changed successfully.", "success")

        return redirect(url_for("main.account"))

    return render_template("pages/change_password.html")

# ==========================
# Customer Registration
# ==========================

@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Basic validation
        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("main.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("main.register"))

        # Check whether email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "error")
            return redirect(url_for("main.register"))

        # Create new customer
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")

        return redirect(url_for("main.login"))

    return render_template("pages/register.html")

@main.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_email", None)

    flash("You have been logged out.", "success")

    return redirect(url_for("main.home"))

# ==========================
# Admin Dashboard
# ==========================

@main.route("/admin")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("main.admin_login"))

    message_count = Contact.query.count()
    product_count = Product.query.count()

    return render_template(
        "admin/dashboard.html",
        message_count=message_count,
        product_count=product_count
    )

# ==========================
# Admin Product Management
# ==========================

@main.route("/admin/products")
def admin_products():

    if not session.get("admin_logged_in"):
        return redirect(url_for("main.admin_login"))

    products = Product.query.order_by(Product.id.desc()).all()

    return render_template(
        "admin/products.html",
        products=products
    )

# ==========================
# Admin Add Product
# ==========================

@main.route("/admin/products/add", methods=["GET", "POST"])
def admin_add_product():

    if not session.get("admin_logged_in"):
        return redirect(url_for("main.admin_login"))

    if request.method == "POST":

        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")
        stock = request.form.get("stock")
        is_featured = bool(request.form.get("is_featured"))

        # ==========================
        # Handle Product Image Upload
        # ==========================

        image_file = request.files.get("image")
        image_path = ""

        if image_file and image_file.filename:

            if not allowed_image(image_file.filename):
                flash(
                    "Invalid image format. Please upload JPG, JPEG, PNG, or WEBP.",
                    "error"
                )
                return redirect(url_for("main.admin_add_product"))

            original_filename = secure_filename(image_file.filename)
            extension = original_filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{extension}"

            upload_folder = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "static",
                "images",
                "products"
            )

            os.makedirs(upload_folder, exist_ok=True)

            image_file.save(
                os.path.join(upload_folder, filename)
            )

            image_path = f"images/products/{filename}"

        product = Product(
            name=name,
            description=description,
            price=float(price),
            category=category,
            image=image_path,
            stock=int(stock),
            is_featured=is_featured
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added successfully.", "success")

        return redirect(url_for("main.admin_products"))

    return render_template("admin/add_product.html")


# ==========================
# Admin Edit Product
# ==========================

@main.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
def admin_edit_product(product_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("main.admin_login"))

    product = Product.query.get_or_404(product_id)

    if request.method == "POST":

        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = float(request.form.get("price"))
        product.category = request.form.get("category")
        product.stock = int(request.form.get("stock"))
        product.is_featured = bool(request.form.get("is_featured"))

        # ==========================
        # Handle New Product Image
        # ==========================

        image_file = request.files.get("image")

        if image_file and image_file.filename:

            if not allowed_image(image_file.filename):
                flash(
                    "Invalid image format. Please upload JPG, JPEG, PNG, or WEBP.",
                    "error"
                )
                return redirect(
                    url_for(
                        "main.admin_edit_product",
                        product_id=product.id
                    )
                )

            original_filename = secure_filename(image_file.filename)
            extension = original_filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{extension}"

            upload_folder = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "static",
                "images",
                "products"
            )

            os.makedirs(upload_folder, exist_ok=True)

            image_file.save(
                os.path.join(upload_folder, filename)
            )

            product.image = f"images/products/{filename}"

        # If no new image is selected,
        # the existing product.image remains unchanged.

        db.session.commit()

        flash("Product updated successfully.", "success")

        return redirect(url_for("main.admin_products"))

    return render_template(
        "admin/edit_product.html",
        product=product
    )

# ==========================
# Admin Delete Product
# ==========================

@main.route("/admin/products/delete/<int:product_id>", methods=["POST"])
def admin_delete_product(product_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("main.admin_login"))

    product = Product.query.get_or_404(product_id)

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully.", "success")

    return redirect(url_for("main.admin_products"))

# ==========================
# Admin Login
# ==========================

@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["admin_logged_in"] = True

            return redirect(url_for("main.admin_dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin/login.html")

# ==========================
# Admin Contact Messages
# ==========================

@main.route("/admin/messages")
def admin_messages():

    if not session.get("admin_logged_in"):
        return redirect(url_for("main.admin_login"))

    messages = Contact.query.order_by(Contact.id.desc()).all()

    return render_template(
        "admin/messages.html",
        messages=messages
    )

# ==========================
# Delete Admin Contact Message
# ==========================

@main.route("/admin/messages/delete/<int:message_id>", methods=["POST"])
def admin_delete_message(message_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("main.admin_login"))

    message = Contact.query.get_or_404(message_id)

    db.session.delete(message)
    db.session.commit()

    flash("Message deleted successfully.", "success")

    return redirect(url_for("main.admin_messages"))

# ==========================
# Admin Logout
# ==========================

@main.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("main.admin_login"))
