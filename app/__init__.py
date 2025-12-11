from flask import Flask
from .models import db
from .routes import routes
from config import Config

def create_app():
    app = Flask(__name__)

    # ✅ Load config
    app.config.from_object(Config)

    # ✅ Khởi tạo DB
    db.init_app(app)

    # ✅ Đăng ký Blueprint
    app.register_blueprint(routes)

    # ✅ Không dùng create_all() với PostgreSQL
    # Nếu block rỗng, phải dùng pass
    with app.app_context():
        pass

    return app
