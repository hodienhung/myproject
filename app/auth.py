from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Product, User, db

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

# ===== LOGIN (email/password) =====
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)

            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            return redirect(url_for('main.index'))

        flash("Sai tài khoản hoặc mật khẩu!")

    return render_template("login.html")   # file chứa cả login + register


# ===== REGISTER =====
@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    requestpass = request.form.get("requestpass")

    if password != requestpass:
        return render_template("login.html", message="Mật khẩu không trùng khớp!")

    if User.query.filter_by(email=email).first():
        return render_template("login.html", message="Email đã tồn tại!")

    new_user = User(username=username, email=email, is_admin=False)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return render_template("login.html", message="Đăng ký thành công! Hãy đăng nhập.")


# ===== LOGOUT =====
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# ===== ADD PRODUCT (chỉ admin) =====
@auth_bp.route('/add_product', methods=['POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        flash("Bạn không có quyền thêm sản phẩm!")
        return redirect(url_for('main.index'))

    name = request.form['name']
    price = request.form['price']
    image_url = request.form['image_url']
    description = request.form.get('description', "")

    new_product = Product(
        name=name,
        price=price,
        image=image_url,
        description=description
    )
    db.session.add(new_product)
    db.session.commit()

    return redirect(url_for('admin.admin_dashboard'))


# ===== GOOGLE LOGIN =====
@auth_bp.route('/login/google')
def login_google():
    google = current_app.extensions['authlib.integrations.flask_client'].google
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize/google')
def authorize_google():
    google = current_app.extensions['authlib.integrations.flask_client'].google
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    email = user_info['email']

    # kiểm tra user trong DB
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=user_info.get('name', email), email=email, is_admin=False)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('main.index'))
