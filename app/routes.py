from flask import Blueprint, jsonify, render_template, request, redirect, url_for, current_app
from .models import db, Booking, Advisory
from datetime import datetime
from .vnpay import vnpay
from .telegram import send_telegram_message
from zoneinfo import ZoneInfo
from sqlalchemy import text
import time

routes = Blueprint('routes', __name__)

# ==========================
# TRANG CHỦ
# ==========================
@routes.route('/')
def index():
    return render_template('index.html')


# ==========================
# HÀM PARSE DATE/DATETIME
# ==========================
def parse_datetime(dt_str):
    """Parse auto: YYYY-MM-DD hoặc YYYY-MM-DD HH:MM"""
    if not dt_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Format thời gian không hợp lệ: {dt_str}")


# ==========================
# XỬ LÝ ĐẶT LỊCH + GỬI TELEGRAM
# ==========================
@routes.route('/booking', methods=['POST'])
def booking():
    data = request.form

    # Kiểm tra trường bắt buộc
    required_fields = ["mother_name", "phone", "address", "service_type", "selected_datetime"]
    for f in required_fields:
        if not data.get(f):
            return jsonify({"error": f"Thiếu {f}"}), 400

    try:
        dt = parse_datetime(data.get("selected_datetime"))

        booking = Booking(
            parent_name=data.get("mother_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            service_type=data.get("service_type"),
            start_date=dt.date(),
            end_date=dt.date(),
            deposit_amount=int(data.get("deposit_amount", 200000)),
        )

        db.session.add(booking)
        db.session.commit()

        return jsonify({"success": True, "booking_id": booking.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ==========================
# TRANG THANH TOÁN
# ==========================
@routes.route('/payment/<int:booking_id>')
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('payment.html', booking=booking)


# ==========================
# TẠO URL THANH TOÁN VNPay
# ==========================
@routes.route('/vnpay_payment/<int:booking_id>', methods=['POST'])
def vnpay_payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.deposit_checked:
        return jsonify({"error": "Giao dịch đã được thanh toán"}), 400

    vnp = vnpay()
    txn_ref = f"{booking.id}_{int(time.time())}"
    amount = booking.deposit_amount * 100

    vnp.requestData = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": current_app.config['VNP_TMN_CODE'],
        "vnp_Amount": amount,
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": f"Thanh toan don hang {booking.id}",
        "vnp_OrderType": "billpayment",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": current_app.config['VNPAY_RETURN_URL'],
        "vnp_IpAddr": request.remote_addr or '127.0.0.1',
        "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S")
    }

    payment_url = vnp.get_payment_url(
        current_app.config['VNP_URL'],
        current_app.config['VNP_HASH_SECRET']
    )

    return jsonify({"vnpay_url": payment_url})


# ==========================
# NHẬN KẾT QUẢ TỪ VNPay
# ==========================
@routes.route("/vnpay_return")
def vnpay_return():
    input_data = request.args.to_dict()
    booking_id = input_data.get("vnp_TxnRef")
    booking = Booking.query.filter(Booking.id == int(booking_id.split("_")[0])).first()

    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    formatted_time = now_vn.strftime("%d/%m/%Y %H:%M:%S")

    if booking and input_data.get("vnp_ResponseCode") == "00":
        booking.deposit_checked = True
        db.session.commit()

        msg = (
            f"💰 Thanh toán VNPay thành công!\n"
            f"Tên: {booking.parent_name}\n"
            f"SĐT: {booking.phone}\n"
            f"Gmail: {booking.email}\n"
            f"Địa chỉ: {booking.address}\n"
            f"Số tiền: {booking.deposit_amount} VND\n"
            f"Ngày giờ: {formatted_time}"
        )
        send_telegram_message(msg)
        result = "Thanh toán thành công"
    else:
        result = "Thanh toán thất bại"

    return render_template(
        "payment_return.html",
        title="Kết quả thanh toán",
        result=result,
        order_id=booking_id,
        amount=booking.deposit_amount if booking else 0,
        order_desc=input_data.get("vnp_OrderInfo"),
        vnp_TransactionNo=input_data.get("vnp_TransactionNo"),
        vnp_ResponseCode=input_data.get("vnp_ResponseCode")
    )


# ==========================
# FORM TƯ VẤN
# ==========================
@routes.route("/advisory", methods=["POST"])
def advisory():
    mother_name = request.form.get("mother_name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    note = request.form.get("note")

    try:
        sql = text("""
            INSERT INTO advisory (mother_name, phone, email, note)
            VALUES (:mother_name, :phone, :email, :note)
        """)
        db.session.execute(sql, {
            'mother_name': mother_name,
            'phone': phone,
            'email': email,
            'note': note
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return redirect("/")


# ==========================
# ROUTE TRANG GET
# ==========================
@routes.route('/booking', methods=['GET'])
def booking_page():
    return render_template('booking.html')


@routes.route('/contact', methods=['GET'])
def contact_page():
    return render_template('contact.html')


@routes.route('/advisory', methods=['GET'])
def advisory_page():
    return render_template('advisory.html')
