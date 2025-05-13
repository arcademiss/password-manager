import hashlib
from hashlib import pbkdf2_hmac as pbkdf2
import requests
from password_generator import check_password


def create_vault_key(username, password, secret_key, salt):
    master_pwd = password + secret_key
    private_key = bytes(master_pwd + username, 'utf-8')
    key = hashlib.pbkdf2_hmac('sha256', private_key, salt.encode('utf-8'), 100_000, dklen=32)

    return master_pwd, key


def create_creds(username, password, client_secret, salt_secret):
    master_pwd, vault_key = create_vault_key(username, password, client_secret, salt_secret)
    vault_key_hex = vault_key.hex()
    auth_key_plain = bytes(master_pwd + vault_key_hex, 'utf-8')
    auth_key = pbkdf2('sha256', auth_key_plain, salt_secret.encode('utf-8'), 100_000, dklen=32)
    return auth_key, master_pwd, vault_key


def send_to_server(auth_key, username, req_type):
    if req_type != "login" and req_type != "register":
        raise ValueError
    if req_type == 'register':
        url = 'http://127.0.0.1:8000/register'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            'username': username,
            'password': auth_key.hex()
        }
        response = requests.post(url, headers=headers, json=data)
        # Optional: Check the response
    if req_type == 'login':
        url = 'http://127.0.0.1:8000/login'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            'username': username,
            'password': auth_key.hex()
        }
        response = requests.post(url, headers=headers, json=data)
    return response


def check_password(password):
    return None
