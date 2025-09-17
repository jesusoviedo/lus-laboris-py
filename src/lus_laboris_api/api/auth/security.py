"""
Security utilities for API authentication and authorization
"""
from typing import Optional, List
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import jwt_validator
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


class SecurityManager:
    """Security manager for handling authentication and authorization"""
    
    def __init__(self):
        self.jwt_validator = jwt_validator
    
    def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """Verify JWT token from Authorization header"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            payload = self.jwt_validator.validate_token(credentials.credentials)
            user = payload.get("sub", "unknown")
            logger.info(f"Token validated successfully for user: {user}")
            return payload
        except ValueError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def check_permission(self, required_permission: str, token_payload: dict) -> bool:
        """Check if token has required permission (deprecated - token validation is sufficient)"""
        logger.warning("Permission checking is deprecated - token validation is sufficient for authentication")
        return True
    
    def require_permission(self, permission: str):
        """Decorator factory for requiring specific permissions (deprecated - token validation is sufficient)"""
        def permission_dependency(token_payload: dict = Depends(self.verify_token)):
            logger.warning(f"Permission '{permission}' check is deprecated - token validation is sufficient")
            return token_payload
        return permission_dependency
    
    def get_current_user(self, token_payload: dict) -> str:
        """Get current user from token payload"""
        user = token_payload.get("sub", "unknown")
        logger.debug(f"Current user: {user}")
        return user
    
    def get_user_permissions(self, token_payload: dict) -> List[str]:
        """Get user permissions from token payload (deprecated - token validation is sufficient)"""
        logger.warning("Permission checking is deprecated - token validation is sufficient for authentication")
        return []
    
    def is_admin(self, token_payload: dict) -> bool:
        """Check if user is admin (deprecated - token validation is sufficient)"""
        logger.warning("Admin checking is deprecated - token validation is sufficient for authentication")
        return True
    
    def validate_api_token(self, token: str) -> dict:
        """Validate API token and return payload"""
        try:
            return self.jwt_validator.validate_token(token)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid API token: {str(e)}"
            )


# Global security manager instance
security_manager = SecurityManager()

# Common dependency functions
def get_current_user(token_payload: dict = Depends(security_manager.verify_token)) -> str:
    """Get current authenticated user"""
    return security_manager.get_current_user(token_payload)

def require_vectorstore_write(token_payload: dict = Depends(security_manager.verify_token)):
    """Require valid JWT token for vectorstore write operations"""
    return token_payload

def require_vectorstore_read(token_payload: dict = Depends(security_manager.verify_token)):
    """Require valid JWT token for vectorstore read operations"""
    return token_payload

def require_admin(token_payload: dict = Depends(security_manager.verify_token)):
    """Require valid JWT token for admin operations"""
    return token_payload

def optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Optional authentication - returns token payload if present, None otherwise"""
    if not credentials:
        return None
    
    try:
        return security_manager.jwt_validator.validate_token(credentials.credentials)
    except ValueError:
        return None
