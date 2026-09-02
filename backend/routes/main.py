from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.models.contact import Contact
from backend.models.user import User
from backend.models.product import Product
from backend.models.wishlist import Wishlist
from backend.database import db
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint("main", __name__)

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

    return render_template(
        "admin/dashboard.html",
        message_count=message_count
    )

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