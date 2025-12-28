from flask import Flask
from .models import db
from .routes import routes
from config import Config
from authlib.integrations.flask_client import OAuth


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo DB
    db.init_app(app)

    # Khởi tạo OAuth
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET,
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v2/',
        client_kwargs={'scope': 'openid email profile'}
    )

    # 👉 Gắn google vào app để có thể gọi trong routes
    app.google = google

    # Đăng ký Blueprint
    app.register_blueprint(routes)

    return app
