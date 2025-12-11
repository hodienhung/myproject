import urllib.parse, hmac, hashlib

class vnpay:
    def __init__(self):
        self.requestData = {}

    def get_payment_url(self, base_url, secret_key):
        if not base_url or not secret_key:
            raise ValueError("base_url hoặc secret_key không được để trống")

        # Lọc bỏ tham số rỗng và vnp_SecureHash nếu có
        params = {k: v for k, v in self.requestData.items() if v not in [None, ""] and k != "vnp_SecureHash"}

        # Sắp xếp theo key alphabet
        sorted_params = sorted(params.items())

        # Tạo query string (URL-encode giá trị)
        query_list = []
        for k, v in sorted_params:
            query_list.append(f"{k}={urllib.parse.quote_plus(str(v).strip())}")
        query_string = "&".join(query_list)

        # Tạo secure hash bằng HMAC-SHA512
        secure_hash = hmac.new(
            secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()

        # Gắn chữ ký vào cuối query
        return f"{base_url}?{query_string}&vnp_SecureHash={secure_hash}"
