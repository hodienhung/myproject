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
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    # Gắn google vào app để gọi trong routes
    app.google = google

    # Đăng ký Blueprint
    app.register_blueprint(routes)

    return app
