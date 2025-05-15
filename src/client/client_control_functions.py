import hashlib
from hashlib import pbkdf2_hmac as pbkdf2
import requests
from password_generator import check_password
from Crypto.Cipher import AES


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


import requests


def get_credentials(token: str, user: str):
    url = 'http://127.0.0.1:8000/Cred'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'  # JWT in the correct header
    }
    params = {'user': user}  # Send user as a query parameter

    response = requests.get(
        url,
        headers=headers,
        params=params  # GET requests should use params, not json
    )

    return response

def decrypt_field(cred: str, nonce: str, key: bytes):
    cred_bin = bytes.fromhex(cred)
    nonce_bin = bytes.fromhex(nonce)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce_bin)
    return cipher.decrypt(cred_bin)


def derive_aes_key(master_password: str, client_key: str, salt: bytes) -> bytes:
    combined = (master_password + client_key).encode()
    return pbkdf2(
        'sha256',
        combined,
        salt,
        600_000,        # High iteration count
        dklen=32        # 256 bits for AES-256
    )