import psycopg
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from hashlib import pbkdf2_hmac as pbkdf2
from Crypto.Cipher import AES
import uuid
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.server.utils import JWT_SECRET_KEY
from utils import create_access_token

from models import UserRegistration, UserLogin
from jose import jwt, JWTError

load_dotenv()
SERVER_SECRET = os.getenv('SERVER_SECRET')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('db_name')
DB_PASSWORD = os.getenv('db_password')
DB_USER = os.getenv('db_user')
DB_CONNECT_STR = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} connect_timeout=10 password={DB_PASSWORD} " \
                 f"user={DB_USER} "


from fastapi import Body
from pydantic import BaseModel
from typing import List


class CredentialIn(BaseModel):
    title: str
    username: str
    password: str  # Already encrypted hex
    nonce: str     # Hex string
    last_modified: str  # ISO 8601 string, e.g. "2025-05-27T14:30:00"
class SyncPayload(BaseModel):
    user: str
    creds: List[CredentialIn]
app = FastAPI()

security = HTTPBearer()


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
                data = {
                    "info": "user login",
                    "user": user.username,
                }
                return {
                    "access_token": create_access_token(data)
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid Credentials")






@app.get('/Cred')
async def get_cred(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: str = None
):
    print("Request received!")  # Debugging
    try:
        token = credentials.credentials
        print("Token:", token)  # Debugging
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        print("Payload:", payload)  # Debugging

        if payload.get("user") != user:
            print("User mismatch!")  # Debugging
            raise HTTPException(status_code=403, detail="Not authorized for this user")

        with psycopg.connect(DB_CONNECT_STR) as conn:
            with conn.cursor() as curr:
                curr.execute("SELECT uuid FROM users WHERE username = %s", (user,))
                uuid_result = curr.fetchone()
                print("UUID Result:", uuid_result)  # Debugging

                if not uuid_result:
                    raise HTTPException(status_code=404, detail="User not found")

                uuid_id = uuid_result[0]
                curr.execute("SELECT * FROM credentials WHERE user_uuid = %s", (uuid_id,))
                credentials = curr.fetchall()
                print("Credentials:", credentials)  # Debugging

                return {"credentials": credentials}

    except JWTError as e:
        print("JWT Error:", e)  # Debugging
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print("Unexpected Error:", e)  # Debugging
        raise

@app.post("/sync")
async def sync_credentials(
    payload: SyncPayload,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        jwt_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])

        if jwt_payload.get("user") != payload.user:
            raise HTTPException(status_code=403, detail="Token does not match user")

        with psycopg.connect(DB_CONNECT_STR) as conn:
            with conn.cursor() as curr:
                curr.execute("SELECT uuid FROM users WHERE username = %s", (payload.user,))
                result = curr.fetchone()
                if not result:
                    raise HTTPException(status_code=404, detail="User not found")
                user_uuid = result[0]

                curr.execute("DELETE FROM credentials WHERE user_uuid = %s", (user_uuid,))

                for cred in payload.creds:
                    curr.execute("""
                        INSERT INTO credentials (user_uuid, title, username, password, nonce, last_modified)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        user_uuid,
                        cred.title,
                        cred.username,
                        cred.password,
                        cred.nonce,
                        cred.last_modified
                    ))
                conn.commit()

        return {"status": "Credentials synchronized"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
