from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Booking

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        service = request.form.get('service')
        combo = request.form.getlist('combo[]')
        name = request.form.get('name')
        phone = request.form.get('phone')
        note = request.form.get('note')

        combo_str = ", ".join(combo) if combo else None

        new_booking = Booking(
            name=name,
            phone=phone,
            service=service,
            combo=combo_str,
            note=note
        )

        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for('routes.success'))

    return render_template('booking.html')

@routes.route('/success')
def success():
    return "<h2>✅ Đặt lịch thành công!</h2>"
