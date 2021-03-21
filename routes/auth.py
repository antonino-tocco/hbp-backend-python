import os
import hashlib
import jwt
from icecream import ic
from datetime import datetime
from flask import request, Response, make_response
from . import routes_api


@routes_api.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        allowed_username = os.getenv('USERNAME') or ''
        allowed_password = hashlib.md5(os.getenv('PASSWORD').encode('utf-8')) if os.getenv('PASSWORD') else hashlib.md5(''.encode('utf-8'))
        jwt_secret = os.getenv('JWT_SECRET') or ''
        username = data['username'] if 'username' in data else None
        password = data['password'] if 'password' in data else None
        if not username or not password:
            return "Bad request", 400
        allowed_password_digest = allowed_password.hexdigest()
        if username != allowed_username or hashlib.md5(password.encode('utf8')).hexdigest() != allowed_password_digest:
            return "Wrong user or password", 401
        jwt_payload = {
            'username': username,
            'date': datetime.now().ctime()
        }
        res = make_response()
        res.set_cookie('hbp_auth_cookie', value=jwt.encode(jwt_payload, jwt_secret, algorithm="HS256"))
        return res
    except Exception as ex:
        return f"Exception {ex}", 500


@routes_api.route('/auth/verify_token', methods=['POST'])
def verify_token():
    try:
        data = request.get_json()
        token = data['token'] if 'token' in data else None
        if not token:
            return "Bad request", 400
        jwt_secret = os.getenv('JWT_SECRET') or ''
        decrypted_token = jwt.decode(token, key=jwt_secret, algorithms=["HS256"])
        username = decrypted_token['username'] if 'username' in decrypted_token else ''
        allowed_username = os.getenv('USERNAME') or ''
        if username != allowed_username:
            return "Authentication expired", 401

        jwt_payload = {
            'username': username,
            'date': datetime.now().ctime()
        }
        res = make_response()
        res.set_cookie('hbp_auth_cookie', value=jwt.encode(jwt_payload, jwt_secret, algorithm="HS256"))
        return res
    except Exception as ex:
        return f"Exception {ex}", 500


