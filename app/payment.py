from flask import Blueprint, request, current_app, redirect, jsonify, render_template
from datetime import datetime
from app import db
from app.models import Booking
from .vnpay import vnpay
from .telegram import send_telegram_message

payment_bp = Blueprint("payment", __name__)

# Route tạo thanh toán VNPAY
@payment_bp.route("/vnpay_payment/<int:booking_id>", methods=["POST"])
def vnpay_payment(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking không tồn tại"}), 404

    # Lấy số tiền (hardcode hoặc từ booking)
    amount = int(booking.amount)  # VNĐ

    # Khởi tạo VNPAY
    vnp = vnpay()
    vnp.requestData["vnp_Version"] = "2.1.0"
    vnp.requestData["vnp_Command"] = "pay"
    vnp.requestData["vnp_TmnCode"] = current_app.config.get("VNP_TMN_CODE")
    vnp.requestData["vnp_Amount"] = str(amount * 100)  # VNPay yêu cầu *100
    vnp.requestData["vnp_CurrCode"] = "VND"
    vnp.requestData["vnp_TxnRef"] = str(booking.id)
    vnp.requestData["vnp_OrderInfo"] = f"Thanh toán booking #{booking.id}"
    vnp.requestData["vnp_OrderType"] = "other"
    vnp.requestData["vnp_Locale"] = "vn"
    vnp.requestData["vnp_CreateDate"] = datetime.now().strftime("%Y%m%d%H%M%S")
    vnp.requestData["vnp_IpAddr"] = request.remote_addr
    vnp.requestData["vnp_ReturnUrl"] = current_app.config.get("VNP_RETURN_URL")

    payment_url = vnp.get_payment_url(
        current_app.config.get("VNP_URL"),
        current_app.config.get("VNP_HASH_SECRET")
    )

    return jsonify({"vnpay_url": payment_url})

# Route nhận kết quả thanh toán
@payment_bp.route("/vnpay_return")
def vnpay_return():
    input_data = request.args.to_dict()
    if not input_data:
        return render_template("payment_return.html", result="Không có dữ liệu")

    vnp = vnpay()
    vnp.responseData = input_data
    secret_key = current_app.config.get("VNP_HASH_SECRET")
    is_valid = vnp.validate_response(secret_key)

    booking_id = input_data.get("vnp_TxnRef")
    booking = Booking.query.get(booking_id)
    amount = int(input_data.get("vnp_Amount", 0)) // 100
    response_code = input_data.get("vnp_ResponseCode")

    if is_valid and response_code == "00":
        result = "Thành công"
        if booking:
            msg = (
                f"💰 Thanh toán VNPay thành công!\n"
                f"👤 Phụ huynh: {booking.parent_name}\n"
                f"📞 SĐT: {booking.phone}\n"
                f"📧 Gmail: {booking.email}\n"
                f"🗓 Ngày: {booking.start_datetime}\n"
                f"💵 Số tiền: {amount:,} VND\n"
            )
            send_telegram_message(msg)
    elif not is_valid:
        result = "Sai checksum"
    else:
        result = f"Lỗi thanh toán (code {response_code})"

    return render_template("payment_return.html", result=result, amount=amount)
