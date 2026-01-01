from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from models.user import UserRole
from services.auth import AuthService

# Security scheme for Swagger UI
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current authenticated user
    Verifies JWT token and returns user data
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get the token from credentials
    token = credentials.credentials
    
    # Verify JWT token
    payload = AuthService.verify_jwt_token(token)
    auth_user_id = payload.get("sub")
    
    if not auth_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = AuthService.get_user_by_auth_id(auth_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    return user

def require_role(allowed_roles: List[UserRole]):
    """
    Dependency factory to check if user has required role
    Usage: Depends(require_role([UserRole.ADMIN, UserRole.PRINCIPAL]))
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if user_role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        
        return current_user
    
    return role_checker

# Convenience dependencies for specific roles
def require_admin(current_user: dict = Depends(get_current_user)):
    
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_principal(current_user: dict = Depends(get_current_user)):
   
    if current_user.get("role") != UserRole.PRINCIPAL.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal access required"
        )
    return current_user

def require_hod(current_user: dict = Depends(get_current_user)):
    """Dependency to require HOD role"""
    if current_user.get("role") != UserRole.HOD.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HOD access required"
        )
    return current_user

def require_teacher(current_user: dict = Depends(get_current_user)):
    """Dependency to require teacher role"""
    if current_user.get("role") != UserRole.TEACHER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    return current_user

def require_student(current_user: dict = Depends(get_current_user)):
    """Dependency to require student role"""
    if current_user.get("role") != UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user

def require_admin_or_principal(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin or principal role"""
    if current_user.get("role") not in [UserRole.ADMIN.value, UserRole.PRINCIPAL.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Principal access required"
        )
    return current_user

def require_admin_or_hod(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin or HOD role"""
    if current_user.get("role") not in [UserRole.ADMIN.value, UserRole.HOD.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HOD access required"
        )
    return current_user

# Combined role dependencies for creation permissions
def require_admin_principal_hod(current_user: dict = Depends(get_current_user)):
    """Allow admin, principal, or HOD"""
    if current_user.get("role") not in [UserRole.ADMIN.value, UserRole.PRINCIPAL.value, UserRole.HOD.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin, Principal, or HOD access required"
        )
    return current_user

def require_admin_principal_hod_teacher(current_user: dict = Depends(get_current_user)):
    """Allow admin, principal, HOD, or teacher"""
    if current_user.get("role") not in [
        UserRole.ADMIN.value,
        UserRole.PRINCIPAL.value,
        UserRole.HOD.value,
        UserRole.TEACHER.value,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin, Principal, HOD, or Teacher access required"
        )
    return current_user
