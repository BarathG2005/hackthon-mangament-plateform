from fastapi import APIRouter, Depends, HTTPException, status
from models.user import (
    ActivateAccountRequest, 
    LoginRequest, 
    TokenResponse, 
    UserResponse
)
from services.auth import AuthService
from dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/activate", status_code=status.HTTP_200_OK)
def activate_account(activation_data: ActivateAccountRequest):
    """
    Activate user account (for students, teachers, HODs, principals)
    
    Users must:
    1. Be pre-registered by admin
    2. Provide correct college_id
    3. Provide matching email
    4. Set a password
    
    This creates their Supabase auth account and links it to their college profile.
    
    - **college_id**: College ID / Roll Number
    - **email**: Registered email address
    - **password**: New password (min 6 characters)
    """
    result = AuthService.activate_account(activation_data)
    return result

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    """
    Login with email and password
    
    Returns JWT access token and user profile
    
    - **email**: User's email address
    - **password**: User's password
    """
    result = AuthService.login(login_data.email, login_data.password)
    return result

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile
    
    Requires valid JWT token in Authorization header
    """
    return UserResponse(**current_user)

@router.post("/logout")
def logout():
    """
    Logout user (client-side token removal)
    
    Note: JWT tokens are stateless, so actual logout is handled client-side
    by removing the token from storage
    """
    return {
        "message": "Logout successful. Please remove the token from client storage."
    }

@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    
    Requires valid JWT token and correct old password
    
    - **old_password**: Current password
    - **new_password**: New password (min 6 characters)
    """
    try:
        # Verify old password by attempting login
        AuthService.login(current_user["email"], old_password)
        
        # Update password using Supabase
        from config.supabase import supabase
        supabase.auth.update_user({
            "password": new_password
        })
        
        return {"message": "Password changed successfully"}
    
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect"
            )
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error changing password: {str(e)}"
        )

@router.post("/check-activation-eligibility")
def check_activation_eligibility(college_id: str, email: str):
    """
    Check if a user is eligible for account activation
    
    Returns user details if eligible (without auth_user_id)
    
    - **college_id**: College ID / Roll Number
    - **email**: Email address
    """
    user = AuthService.get_user_by_college_id(college_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please contact admin."
        )
    
    if user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email does not match college ID"
        )
    
    if user.get("auth_user_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already activated. Please login."
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact admin."
        )
    
    return {
        "eligible": True,
        "name": user["name"],
        "role": user["role"],
        "department": user.get("department"),
        "message": "You can proceed with account activation"
    }
