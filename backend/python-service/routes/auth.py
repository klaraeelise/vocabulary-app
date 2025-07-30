from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.hash import bcrypt
import jwt
import os
from database import get_connection

# Encryption key for JWT, stored in .env file
SECRET_KEY = os.getenv("SECRET_KEY")

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

    # Generate JWT token
    token = jwt.encode(
        {"id": user["id"], "email": user["email"], "type": user["type"]},
        SECRET_KEY,
        algorithm="HS256"
    )
    print("Generated token:", token)  # Debug log

    return {"token": token} #Token can be used in frontend to allow user to access protected routes


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
