from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    parent_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)  # Đảm bảo NOT NULL

    child_name = db.Column(db.String(100), nullable=False)
    child_age = db.Column(db.Integer)

    service_type = db.Column(db.String(100), nullable=False)
    services_selected = db.Column(db.Text)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    notes = db.Column(db.Text)

    deposit_amount = db.Column(db.Integer, default=200000)  # Lưu số tiền người dùng nhập
    deposit_checked = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
