from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(120), nullable=False)
    combo = db.Column(db.String(300))
    note = db.Column(db.Text)
