from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from passlib.hash import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional
from database import get_connection

# Encryption key for JWT, stored in .env file
SECRET_KEY = os.getenv("SECRET_KEY")
# Token expiry: 24 hours
TOKEN_EXPIRY_HOURS = 24

router = APIRouter(prefix="/auth")

class RegisterRequest(BaseModel):
    email: str
    password: str
    type: str = "basic"  # Default user type is "basic"

class LoginRequest(BaseModel):
    email: str
    password: str


###Login
@router.post("/login")
def login(data: LoginRequest):
    print("Login attempt:", data.email)  # Debug log

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (data.email,)) #SQL query to fetch user from phpMyadmin Database
    user = cursor.fetchone()

    cursor.close()
    db.close()

    # Verify user exists and password is correct
    if not user or not bcrypt.verify(data.password, user["password_hash"]):
        print("Invalid login attempt")  # Debug log
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token with expiration time (24 hours)
    expiry_time = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    token = jwt.encode(
        {
            "id": user["id"], 
            "email": user["email"], 
            "type": user["type"],
            "exp": expiry_time  # Add expiration to token payload
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    print("Generated token:", token)  # Debug log

    return {
        "token": token,
        "expires_at": expiry_time.isoformat()  # Return expiry time to frontend
    } #Token can be used in frontend to allow user to access protected routes


###Registration
@router.post("/register")
def register(data: RegisterRequest):
    db = get_connection()
    cursor = db.cursor(dictionary=True) #Dictionary also stores the column names as keys, which makes further data manipulation easier

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email=%s", (data.email,)) # SQL query to check if email is already registered
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = bcrypt.hash(data.password)

    # Insert user
    cursor.execute(
        "INSERT INTO users (email, password_hash, type) VALUES (%s, %s, %s)", #SQL query to insert new user into phpMyadmin Database
        (data.email, hashed_password, data.type),
    )
    db.commit()

    cursor.close()
    db.close()

    return {"message": "User registered successfully"}


# Utility function to verify JWT token
def verify_token(authorization: Optional[str] = Header(None)):
    """
    Dependency function to verify JWT token from Authorization header.
    Returns decoded token data if valid, raises HTTPException if invalid/expired.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    try:
        # Decode and verify token (jwt.decode automatically checks expiry)
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Endpoint to verify if current token is still valid
@router.get("/verify")
def verify_token_endpoint(token_data: dict = Depends(verify_token)):
    """
    Endpoint to check if the current token is still valid.
    Frontend can call this to verify token before making requests.
    """
    return {
        "valid": True,
        "user_id": token_data.get("id"),
        "email": token_data.get("email"),
        "type": token_data.get("type")
    }
