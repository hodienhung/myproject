# app/routes/utils.py
def get_client_ip(request):
    if request.headers.get("X-Forwarded-For"):
        ip = request.headers.get("X-Forwarded-For").split(",")[0]
    else:
        ip = request.remote_addr
    return ip
