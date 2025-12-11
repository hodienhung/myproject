from flask import Blueprint, render_template, request, redirect, url_for, current_app
from .models import db, Booking
from datetime import datetime
from .vnpay import vnpay
from .telegram import send_telegram_message

routes = Blueprint('routes', __name__)

# ==========================
# TRANG CHỦ
# ==========================
@routes.route('/')
def index():
    return render_template('index.html')


# ==========================
# XỬ LÝ ĐẶT LỊCH + GỬI TELEGRAM
# ==========================
@routes.route('/booking', methods=['POST'])
def booking():
    parent_name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    child_name = request.form.get('child_name')
    child_age = int(request.form.get('age', 0))
    service_type = request.form.get('service')
    combo_list = request.form.getlist('combo[]')
    services_selected = ", ".join(combo_list) if combo_list else None
    start_date = datetime.strptime(request.form.get('start_date'), "%Y-%m-%d").date()
    end_date = datetime.strptime(request.form.get('end_date'), "%Y-%m-%d").date()
    notes = request.form.get('note')
    deposit_paid = int(float(request.form.get('deposit_paid_amount', 0)))

    # Lưu booking vào database
    new_booking = Booking(
        parent_name=parent_name,
        email=email,
        phone=phone,
        address=address,
        child_name=child_name,
        child_age=child_age,
        service_type=service_type,
        services_selected=services_selected,
        start_date=start_date,
        end_date=end_date,
        notes=notes,
        deposit_amount=deposit_paid,
        deposit_checked=deposit_paid > 0
    )

    db.session.add(new_booking)
    db.session.commit()

    # Gửi Telegram nếu đã cọc trực tiếp
    if deposit_paid > 0:
        msg = (
            f"✅ New Booking!\n"
            f"Tên: {parent_name}\n"
            f"SĐT: {phone}\n"
            f"Gmail: {email}\n"
            f"Địa chỉ: {address}\n"
            f"Số tiền cọc: {deposit_paid} VND"
        )
        send_telegram_message(msg)

    return redirect(url_for('routes.payment', booking_id=new_booking.id))


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
    vnp = vnpay()

    vnp.requestData = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": current_app.config['VNP_TMN_CODE'],
        "vnp_Amount": 200000 * 100,  # cố định 200k  # Sử dụng số tiền thực tế
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": str(booking.id),
        "vnp_OrderInfo": f"Thanh toan don hang {booking.id}",
        "vnp_OrderType": "billpayment",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": current_app.config['VNPAY_RETURN_URL'],
        "vnp_IpAddr": request.remote_addr,
        "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S")
    }

    payment_url = vnp.get_payment_url(
        current_app.config['VNP_URL'],
        current_app.config['VNP_HASH_SECRET']
    )

    print("🔗 VNPay URL:", payment_url)
    return redirect(payment_url)


# ==========================
# NHẬN KẾT QUẢ TRẢ VỀ TỪ VNPay
# ==========================
@routes.route("/vnpay_return")
def vnpay_return():
    input_data = request.args.to_dict()
    booking_id = input_data.get("vnp_TxnRef")
    booking = Booking.query.get(booking_id)

    if booking and input_data.get("vnp_ResponseCode") == "00":
        booking.deposit_checked = True
        db.session.commit()

        # Gửi Telegram khi thanh toán VNPay thành công
        msg = (
            f"💰 Thanh toán VNPay thành công!\n"
            f"Tên: {booking.parent_name}\n"
            f"SĐT: {booking.phone}\n"
            f"Gmail: {booking.email}\n"
            f"Địa chỉ: {booking.address}\n"
            f"Số tiền: {booking.deposit_amount} VND"
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
# TRANG THÀNH CÔNG
# ==========================
@routes.route('/success')
def success():
    return "<h2>🎉 Thanh toán thành công! Cảm ơn bạn đã đặt lịch.</h2>"
