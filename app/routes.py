import os
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, current_app
from .models import Testimonial, db, Booking, Advisory
from datetime import datetime
from .vnpay import vnpay
from .telegram import send_telegram_message
from zoneinfo import ZoneInfo
from sqlalchemy import text
import time
from flask import session
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
routes = Blueprint('routes', __name__)


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
# FORM ĐĂNG KÝ KHÓA HỌC
# ==========================

@routes.route("/register_course", methods=["POST"])
def register_course():
    fullname = request.form.get("fullname")
    phone = request.form.get("phone")
    email = request.form.get("email")
    course = request.form.get("course")
    note = request.form.get("note")
    payment_method = request.form.get("payment_method")

    try:
        sql = text("""
    INSERT INTO course_registration 
    (fullname, phone, email, course, note, payment_method)
    VALUES 
    (:fullname, :phone, :email, :course, :note, :payment_method)
""")

        db.session.execute(sql, {
            'fullname': fullname,
            'phone': phone,
            'email': email,
            'course': course,
            'note': note,
            'payment_method': payment_method
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
    "success": True,
    "course": course,
    "email": email,
    "payment_method": payment_method
})
@routes.route("/registration-successful")
def registration_successful():
    return render_template(
        "registration-successful.html",
        course=request.args.get("course"),
        email=request.args.get("email"),
        payment_method=request.args.get("payment_method")
    )
# ==========================
# TESTIMONIALS
# ==========================
UPLOAD_FOLDER = "static/uploads/testimonials"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.route("/testimonial", methods=["POST"])
def add_testimonial():
    name = request.form.get("name")
    content = request.form.get("content")
    rating = int(request.form.get("rating", 5))
    image_file = request.files.get("image")

    if not name or not content:
        return jsonify({"success": False, "message": "Thiếu dữ liệu"}), 400

    image_url = None
    if image_file and allowed_file(image_file.filename):

        # ✅ Tạo đường dẫn tuyệt đối từ root_path
        save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(save_path, exist_ok=True)

        filename = secure_filename(image_file.filename)
        filename = f"{int(time.time())}_{filename}"

        image_path = os.path.join(save_path, filename)
        image_file.save(image_path)

        # ✅ URL để frontend load ảnh
        image_url = f"/{UPLOAD_FOLDER}/{filename}"

    t = Testimonial(
        name=name,
        content=content,
        rating=rating,
        image=image_url
    )

    db.session.add(t)
    db.session.commit()

    return jsonify({"success": True, "testimonial": {
        "name": t.name,
        "content": t.content,
        "rating": t.rating,
        "image_url": t.image
    }})


    db.session.add(t)
    db.session.commit()

    return jsonify({"success": True, "testimonial": {
        "name": t.name,
        "content": t.content,
        "rating": t.rating,
        "image_url": t.image
    }})


@routes.route("/testimonials")
def get_testimonials():
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()

    return jsonify([
        {
            "name": t.name,
            "content": t.content,
            "rating": t.rating,
            "image_url": t.image  # trả về URL để frontend hiển thị
        } for t in testimonials
    ])
#Đăng nhập bằng gg
@routes.route('/authorize')
def authorize():
    token = current_app.google.authorize_access_token()
    resp = current_app.google.get('userinfo')
    user_info = resp.json()
    session['user'] = user_info
    return redirect('/')




# ==========================
# ROUTE TRANG GET
# ==========================
@routes.route('/')
def index():
    return render_template('index.html')
@routes.route('/booking', methods=['GET'])
def booking_page():
    return render_template('booking.html')


@routes.route('/contact', methods=['GET'])
def contact_page():
    return render_template('contact.html')


@routes.route('/advisory', methods=['GET'])
def advisory_page():
    return render_template('advisory.html')

@routes.route('/learnes', methods=['GET'])
def learnes_page():
    return render_template('learnes.html')

@routes.route('/services', methods=['GET'])
def services_page():
    return render_template('services.html')

@routes.route('/register-course', methods=['GET'])
def register_course_page():
    return render_template('register-course.html')

@routes.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

from flask import current_app, session, redirect, url_for

@routes.route('/login/google')
def login_google():
    redirect_uri = url_for('routes.authorize', _external=True)
    return current_app.google.authorize_redirect(redirect_uri)



