import os
from dotenv import load_dotenv

# Chỉ cần ở local dev để đọc file .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # VNPay Config
    VNP_TMN_CODE = os.getenv("VNP_TMN_CODE")
    VNP_HASH_SECRET = os.getenv("VNP_HASH_SECRET")
    VNP_URL = os.getenv("VNP_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
    VNPAY_RETURN_URL = os.getenv("VNPAY_RETURN_URL", "http://127.0.0.1:5000/vnpay_return")

    # Google OAuth

