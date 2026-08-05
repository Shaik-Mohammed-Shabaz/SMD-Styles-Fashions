from flask import Flask, render_template, send_from_directory
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(
    __name__,
    template_folder="templates",
    static_folder=os.path.join(project_root, "frontend"),
    static_url_path=""
)

assets_folder = os.path.join(project_root, "assets")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/shop")
def shop():
    return render_template("shop.html")


@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/product")
def product():
    return render_template("pages/product.html")


@app.route("/about")
def about():
    return render_template("pages/about.html")


@app.route("/contact")
def contact():
    return render_template("pages/contact.html")


@app.route("/login")
def login():
    return render_template("pages/login.html")


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(assets_folder, filename)


if __name__ == "__main__":
    app.run(debug=True)