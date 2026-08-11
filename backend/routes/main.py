from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.models.contact import Contact
from backend.database import db

main = Blueprint("main", __name__)

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
    return render_template("index.html")


@main.route("/shop")
def shop():
    return render_template("shop.html")


@main.route("/checkout")
def checkout():
    return render_template("checkout.html")


@main.route("/success")
def success():
    return render_template("success.html")


@main.route("/product")
def product():
    return render_template("pages/product.html")


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


@main.route("/login")
def login():
    return render_template("pages/login.html")

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