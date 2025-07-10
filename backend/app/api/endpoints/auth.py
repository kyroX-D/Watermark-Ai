# File: backend/app/api/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ...core.database import get_db
from ...core.security import verify_password, get_password_hash, create_access_token
from ...core.config import settings
from ...models.user import User
from ...schemas.user import UserCreate, UserResponse, Token
from ...services.stripe_service import StripeService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
    )

    # Create Stripe customer if API key is configured
    if settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY != "sk_test_dummy":
        stripe_service = StripeService()
        try:
            user.stripe_customer_id = await stripe_service.create_customer(
                user_data.email, user_data.username
            )
        except Exception as e:
            print(f"Stripe customer creation failed: {e}")
            # Continue without Stripe customer ID

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Login with email and password"""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/google")
async def google_login():
    """Initiate Google OAuth login"""
    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "dummy-client-id":
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Please contact support."
        )
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
    )
    return {"auth_url": google_auth_url}


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    if not settings.GOOGLE_CLIENT_SECRET or settings.GOOGLE_CLIENT_SECRET == "dummy-client-secret":
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Please contact support."
        )
    
    # Exchange code for token
    import httpx

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to exchange code for token"
                )
            
            token_json = token_response.json()

            # Get user info
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_json['access_token']}"},
            )
            
            if user_info_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user info from Google"
                )
            
            user_info = user_info_response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to Google: {str(e)}"
        )

    # Find or create user
    user = db.query(User).filter(User.google_id == user_info["id"]).first()

    if not user:
        user = db.query(User).filter(User.email == user_info["email"]).first()

        if not user:
            # Create new user
            user = User(
                email=user_info["email"],
                username=user_info["email"].split("@")[0],
                google_id=user_info["id"],
                is_verified=True,
            )

            # Create Stripe customer if configured
            if settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY != "sk_test_dummy":
                stripe_service = StripeService()
                try:
                    user.stripe_customer_id = await stripe_service.create_customer(
                        user_info["email"], user_info.get("name", user_info["email"])
                    )
                except Exception as e:
                    print(f"Stripe customer creation failed: {e}")

            db.add(user)
        else:
            # Link existing user to Google
            user.google_id = user_info["id"]
            user.is_verified = True

        db.commit()
        db.refresh(user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Redirect to frontend with token
    frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
    return {"redirect_url": frontend_url}