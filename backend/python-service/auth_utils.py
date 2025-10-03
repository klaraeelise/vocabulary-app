"""
Authentication utilities for JWT token verification.
Can be imported by other route modules to protect endpoints.
"""
from fastapi import HTTPException, Header
from typing import Optional
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")


def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency function to verify JWT token and extract user information.
    Use this as a dependency in protected routes: user = Depends(get_current_user)
    
    Returns:
        dict: User information from token (id, email, type)
    
    Raises:
        HTTPException: If token is missing, invalid, or expired
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
