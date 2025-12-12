from flask import Blueprint, request, current_app, redirect, render_template
from flask_login import login_required, current_user
from datetime import datetime
import urllib

from app.models import CartItem, Order
from app import db
from app.routes.booking import Booking   # nếu model booking ở đây
from .vnpay import vnpay
from .utils import get_client_ip
from .telegram import send_telegram_message

payment_bp = Blueprint("payment", __name__)

# Hàm tính tổng tiền giỏ hàng
def get_cart_total():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    return total_amount, cart_items


# ------------------ THANH TOÁN ------------------
@payment_bp.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    if request.method == "POST":
        method = request.form.get("method")
        order_id = request.form.get("order_id")

        raw_amount = request.form.get("amount", "0")
        amount = int(float(raw_amount))

        order_desc = request.form.get("order_desc")
        order_type = request.form.get("order_type")
        bank_code = request.form.get("bank_code")
        language = request.form.get("language")
        ipaddr = get_client_ip(request)

        if method == "cash":
            order = Order(txn_ref=order_id, amount=amount, status="pending")
            db.session.add(order)
            db.session.commit()
            return "Đơn hàng đã được tạo, thanh toán khi nhận hàng."

        elif method == "vnpay":
            vnp = vnpay()
            vnp.requestData["vnp_Version"] = "2.1.0"
            vnp.requestData["vnp_Command"] = "pay"
            vnp.requestData["vnp_TmnCode"] = current_app.config.get("VNP_TMN_CODE")
            vnp.requestData["vnp_Amount"] = str(amount * 100)
            vnp.requestData["vnp_CurrCode"] = "VND"
            vnp.requestData["vnp_TxnRef"] = order_id
            vnp.requestData["vnp_OrderInfo"] = urllib.parse.quote_plus(order_desc)
            vnp.requestData["vnp_OrderType"] = order_type
            vnp.requestData["vnp_Locale"] = language if language else "vn"

            if bank_code:
                vnp.requestData["vnp_BankCode"] = bank_code

            vnp.requestData["vnp_CreateDate"] = datetime.now().strftime("%Y%m%d%H%M%S")
            vnp.requestData["vnp_IpAddr"] = ipaddr
            vnp.requestData["vnp_ReturnUrl"] = current_app.config.get("VNP_RETURN_URL")

            payment_url = vnp.get_payment_url(
                current_app.config.get("VNP_URL"),
                current_app.config.get("VNP_HASH_SECRET")
            )
            return redirect(payment_url)

        return "Phương thức thanh toán không hợp lệ!"

    else:
        order_id = "DH" + datetime.now().strftime("%Y%m%d%H%M%S")
        total_amount, cart_items = get_cart_total()
        return render_template("checkout.html", order_id=order_id, amount=total_amount)


# ------------------ KẾT QUẢ THANH TOÁN ------------------
@payment_bp.route("/payment_return")
def payment_return():
    input_data = request.args.to_dict()

    if input_data:
        vnp = vnpay()
        vnp.responseData = input_data

        order_id = input_data.get("vnp_TxnRef")
        order_desc = input_data.get("vnp_OrderInfo")
        vnp_TransactionNo = input_data.get("vnp_TransactionNo")
        vnp_ResponseCode = input_data.get("vnp_ResponseCode")

        # Parse số tiền
        try:
            amount = int(input_data.get("vnp_Amount", "0")) // 100
        except:
            amount = 0

        # Xác minh checksum
        secret_key = current_app.config.get("VNP_HASH_SECRET")
        is_valid = vnp.validate_response(secret_key)

        # ---- Lấy thông tin booking ----
        booking_id = order_id.replace("DH", "")[:14]   # hoặc cách bạn đang sinh ID
        booking = Booking.query.filter_by(id=booking_id).first()

        if booking:
            # Format ngày giờ
            start_dt = datetime.strptime(booking.start_datetime, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(booking.end_datetime, "%Y-%m-%d %H:%M")

            start_str = start_dt.strftime("%d/%m/%Y %H:%M")
            end_str = end_dt.strftime("%d/%m/%Y %H:%M")

        if is_valid:
            if vnp_ResponseCode == "00":
                result = "Thành công"

                # ------ Gửi TELEGRAM đầy đủ ------
                msg = (
                    f"💰 Thanh toán VNPay thành công!\n\n"
                    f"👤 Phụ huynh: {booking.parent_name}\n"
                    f"📞 SĐT: {booking.phone}\n"
                    f"📧 Gmail: {booking.email}\n"
                    f"🏠 Địa chỉ: {booking.address}\n\n"
                    f"🗓 Ngày bắt đầu: {start_str}\n"
                    f"🗓 Ngày kết thúc: {end_str}\n"
                    f"💵 Số tiền: {amount:,} VND\n"
                )
                send_telegram_message(msg)
            else:
                result = "Lỗi"
        else:
            result = "Sai checksum"

        return render_template(
            "payment_return.html",
            result=result,
            order_id=order_id,
            amount=amount,
            order_desc=order_desc,
            vnp_TransactionNo=vnp_TransactionNo,
            vnp_ResponseCode=vnp_ResponseCode
        )

    return render_template("payment_return.html", result="Không có dữ liệu")
