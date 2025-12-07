from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from .models import SignupRequest
from .hash_utils import hash_password, verify_password
from .jwt_handler import create_access_token, verify_token
from ..config.db import users_collection

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to validate the token and retrieve the current user.
    Used by protected routes.
    """
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    role = payload.get("role")
    
    if username is None or role is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return {"username": username, "role": role}

@router.post("/signup")
def signup(req: SignupRequest):
    if users_collection.find_one({"username": req.username}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    users_collection.insert_one({
        "username": req.username,
        "password": hash_password(req.password),
        "role": req.role
    })
    return {"message": "User created successfully"}

class LoginRequest(SignupRequest):
    pass

@router.post("/login")
def login(req: LoginRequest):
    """
    Verifies credentials and returns a JWT access token.
    """
    user = users_collection.find_one({"username": req.username})
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create Token
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user["username"],
        "role": user["role"]
    }