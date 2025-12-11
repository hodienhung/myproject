from flask import Flask
from .models import db
from .route import routes

def create_app():
    app = Flask(__name__)

    # Cấu hình database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kidscare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Khởi tạo DB
    db.init_app(app)

    # Đăng ký Blueprint
    app.register_blueprint(routes)

    # Tạo bảng
    with app.app_context():
        db.create_all()

    return app
