from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    parent_name = db.Column(db.String(100), nullable=False)  # Tên mẹ/khách hàng
    email = db.Column(db.String(120))                        # Email tùy chọn
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200))                      # Địa chỉ nếu có

    service_type = db.Column(db.String(100), nullable=False)
    services_selected = db.Column(db.Text)                  # Dịch vụ chi tiết nếu cần

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    notes = db.Column(db.Text)                              # Ghi chú từ form

    deposit_amount = db.Column(db.Integer, default=200000)  # Số tiền cọc
    deposit_checked = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Advisory(db.Model):
    __tablename__ = "advisory"

    id = db.Column(db.Integer, primary_key=True)
    mother_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255))
    note = db.Column(db.Text)
    service = db.Column(db.String(100))
    date = db.Column(db.Date)
    time = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Advisory {self.id} - {self.mother_name}>"
class CourseRegistration(db.Model):
    __tablename__ = "course_registration"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255))
    note = db.Column(db.Text)
    course = db.Column(db.String(255))  # sửa 'coures' -> 'course'
    payment_method = db.Column(db.String(50))  # sửa 'comlum' -> 'Column' và 'Text' -> 'String(50)'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CourseRegistration {self.fullname} - {self.course}>"
