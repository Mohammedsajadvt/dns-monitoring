import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_database
from app.models import UserCreate, UserLogin, UserResponse, TokenResponse
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    db = await get_database()
    existing_user = await db.users.find_one({"email": user_data.email.lower().strip()})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
        
    user_id = str(uuid.uuid4())
    new_user = {
        "user_id": user_id,
        "email": user_data.email.lower().strip(),
        "password_hash": get_password_hash(user_data.password),
        "full_name": user_data.full_name,
        "role": user_data.role,
        "created_at": datetime.utcnow()
    }
    await db.users.insert_one(new_user)
    
    # Also ensure an auto-detected network exists for the new user
    from app.network_detector import detect_current_wifi_network
    wifi_info = detect_current_wifi_network()
    
    default_net_id = f"net_{user_id[:8]}"
    existing_net = await db.networks.find_one({"network_id": default_net_id})
    if not existing_net:
        await db.networks.insert_one({
            "network_id": default_net_id,
            "user_id": user_id,
            "name": wifi_info["name"],
            "location": wifi_info["location"],
            "description": f"Auto-detected active wireless gateway ({wifi_info['subnet']})",
            "subnet": wifi_info["subnet"],
            "created_at": datetime.utcnow()
        })
    
    access_token = create_access_token(data={"sub": new_user["email"], "role": new_user["role"], "user_id": user_id})
    user_resp = UserResponse(
        id=user_id,
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"],
        created_at=new_user["created_at"]
    )
    return TokenResponse(access_token=access_token, user=user_resp)

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    db = await get_database()
    user = await db.users.find_one({"email": login_data.email.lower().strip()})
    if not user or not verify_password(login_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user["email"], "role": user.get("role", "admin"), "user_id": user.get("user_id")})
    user_resp = UserResponse(
        id=user.get("user_id", str(user.get("_id", ""))),
        email=user["email"],
        full_name=user.get("full_name", "Administrator"),
        role=user.get("role", "admin"),
        created_at=user.get("created_at", datetime.utcnow())
    )
    return TokenResponse(access_token=access_token, user=user_resp)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    user = await db.users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.get("user_id", str(user.get("_id", ""))),
        email=user["email"],
        full_name=user.get("full_name", "Administrator"),
        role=user.get("role", "admin"),
        created_at=user.get("created_at", datetime.utcnow())
    )
