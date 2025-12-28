import os


class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://kidcare_user:RM6eDLHspfhCNWrl8n4IwGeeLMSICD4U@dpg-d4t4h5chg0os73clbqb0-a.oregon-postgres.render.com:5432/kidcare"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # VNPay Config
    VNP_TMN_CODE = "NJFA55LY"   # Mã định danh merchant
    VNP_HASH_SECRET = "BN6AYXN4DSTT4ENVLFGUDHD96XV34UIM"  # Chuỗi bí mật tạo checksum
    VNP_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"  # URL sandbox
    VNPAY_RETURN_URL = "http://127.0.0.1:5000/vnpay_return"
  # URL nhận kết quả trả về
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")