from typing import Annotated
import psycopg
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
from hashlib import pbkdf2_hmac as pbkdf2
from Crypto.Cipher import AES
import uvicorn
import uuid
from utils import create_access_token

from models import UserRegistration, UserLogin

load_dotenv()
SERVER_SECRET = os.getenv('SERVER_SECRET')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('db_name')
DB_PASSWORD = os.getenv('db_password')
DB_USER = os.getenv('db_user')
DB_CONNECT_STR = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} connect_timeout=10 password={DB_PASSWORD} " \
                 f"user={DB_USER} "

app = FastAPI()


def hash_password(password: str, salt: bytes) -> str:
    return pbkdf2('sha256', password.encode('utf-8'), salt, 600_000, dklen=32).hex()

def encrypt_password(password):
    cipher = AES.new(bytes.fromhex(SERVER_SECRET), AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(bytes.fromhex(password))

    return ciphertext, nonce, tag

def decrypt_password(password, nonce):
    cipher = AES.new(bytes.fromhex(SERVER_SECRET), AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(bytes.fromhex(password))

@app.post("/register")
async def register_user(user: UserRegistration):
    with psycopg.connect(DB_CONNECT_STR) as conn:
        with conn.cursor() as curr:
            # Check if username exists
            curr.execute("SELECT username FROM users WHERE username = %s", (user.username,))
            if curr.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")

            # Generate salt and hash
            salt = os.urandom(16)  # 16-byte salt
            hashed_password = hash_password(user.password, salt)
            # todo: encrypt hashed password

            encrypted_password, nonce, tag = encrypt_password(hashed_password)

            # Insert into DB
            user_uuid = uuid.uuid4()
            curr.execute(
                "INSERT INTO users (uuid, username, hashed_password, salt, encryption_nonce, encryption_tag) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (user_uuid, user.username, encrypted_password.hex(), salt.hex(), nonce, tag)
            )
            conn.commit()
            return {"status": "User created"}


@app.post('/login')
async def login_user(user: UserLogin):
    with psycopg.connect(DB_CONNECT_STR) as conn:
        with conn.cursor() as curr:
            curr.execute("""
                SELECT uuid, hashed_password, salt, encryption_nonce, encryption_tag FROM users WHERE username = %s
            """, (user.username,))
            result = curr.fetchone()

            if not result:
                raise HTTPException(status_code=401, detail="Invalid Credentials")

            user_uuid, hashed_password, salt_hex, nonce, encryption_tag = result
            salt = bytes.fromhex(salt_hex)  # Correctly decode hex string to bytes

            user_pass_hash = hash_password(user.password, salt)

            decrypted_password = decrypt_password(hashed_password, nonce).hex()

            if user_pass_hash == decrypted_password:
                return {
                    "access_token": create_access_token(user.username)
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid Credentials")



