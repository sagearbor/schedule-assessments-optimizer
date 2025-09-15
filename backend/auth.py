from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
import uuid

from database import get_db, DBUser
from models import User, UserCreate, Token

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-" + str(uuid.uuid4()))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:
    """Handle authentication and authorization."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[DBUser]:
        """Authenticate a user by email and password."""
        user = db.query(DBUser).filter(DBUser.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> DBUser:
        """Create a new user."""
        # Check if user already exists
        existing_user = db.query(DBUser).filter(DBUser.email == user_create.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = DBUser(
            id=str(uuid.uuid4()),
            email=user_create.email,
            hashed_password=AuthService.get_password_hash(user_create.password),
            full_name=user_create.full_name,
            organization=user_create.organization,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """Get the current authenticated user from the token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        payload = AuthService.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Special case for demo user
        if email == "demo@example.com":
            return User(
                id="demo-user-id",
                email="demo@example.com",
                full_name="Demo User",
                organization="Demo Organization",
                role="user",
                created_at=datetime.utcnow(),
                is_active=True
            )
        
        user = db.query(DBUser).filter(DBUser.email == email).first()
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization=user.organization,
            role=user.role,
            created_at=user.created_at,
            is_active=user.is_active
        )
    
    @staticmethod
    def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
        """Ensure the current user is active."""
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    
    @staticmethod
    def check_admin(current_user: User = Depends(get_current_active_user)) -> User:
        """Check if the current user is an admin."""
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user


from fastapi import Header

# Optional user dependency - returns None if not authenticated
def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None."""
    if not authorization:
        return None

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None

    try:
        # Decode and verify the token directly
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None

        # For demo user, return a mock user object
        if email == "demo@example.com":
            return User(
                id="demo-user",
                email=email,
                full_name="Demo User",
                organization="Demo Org",
                role="user",
                created_at=datetime.utcnow(),
                is_active=True
            )

        # Get user from database
        user = db.query(DBUser).filter(DBUser.email == email).first()
        if user is None:
            return None

        return User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization=user.organization,
            role=user.role,
            created_at=user.created_at,
            is_active=user.is_active
        )
    except:
        return None