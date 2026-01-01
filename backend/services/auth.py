from fastapi import HTTPException, status
from config.supabase import supabase, supabase_admin
from config.settings import settings
from models.user import UserRole, CollegeUser, AddUserRequest, ActivateAccountRequest
from typing import Optional, Dict
import jwt
from datetime import datetime

class AuthService:
    """Service for handling authentication and user management"""
    
    @staticmethod
    def verify_jwt_token(token: str) -> Dict:
        """
        Verify and decode JWT token from Supabase
        Returns the decoded token payload
        """
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]
            
            # Verify token using Supabase client
            response = supabase.auth.get_user(token)
            
            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Return user data from token
            return {
                "sub": response.user.id,
                "email": response.user.email,
                "role": response.user.role
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def get_user_by_auth_id(auth_user_id: str) -> Optional[Dict]:
        """
        Get user details from college_users table by auth_user_id
        """
        try:
            # Use service role to bypass RLS when looking up users by auth_user_id
            response = supabase_admin.table("college_users").select("*").eq("auth_user_id", auth_user_id).single().execute()
            return response.data
        except Exception as e:
            return None
    
    @staticmethod
    def get_user_by_college_id(college_id: str) -> Optional[Dict]:
        """
        Get user details from college_users table by college_id
        """
        try:
            # Use service role to bypass RLS
            response = supabase_admin.table("college_users").select("*").eq("college_id", college_id).single().execute()
            return response.data
        except Exception as e:
            return None
    
    @staticmethod
    def add_user(user_data: AddUserRequest) -> Dict:
        """
        Add a new user to college_users table (without auth credentials)
        This is called by admin to pre-register users
        """
        try:
            # Check if user already exists
            existing_user = AuthService.get_user_by_college_id(user_data.college_id)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with college_id {user_data.college_id} already exists"
                )
            
            # Check if email already exists
            email_check = supabase_admin.table("college_users").select("*").eq("email", user_data.email).execute()
            if email_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email {user_data.email} already exists"
                )
            
            # Insert user into college_users table (using service role to bypass RLS)
            user_dict = {
                "college_id": user_data.college_id,
                "name": user_data.name,
                "email": user_data.email,
                "role": user_data.role.value,
                "department": user_data.department,
                "is_active": True,
                "auth_user_id": None,  # Will be set during account activation
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = supabase_admin.table("college_users").insert(user_dict).execute()
            return response.data[0]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error adding user: {str(e)}"
            )
    
    @staticmethod
    def activate_account(activation_data: ActivateAccountRequest) -> Dict:
        """
        Activate a user account by creating Supabase auth user and linking it
        """
        try:
            # Step 1: Validate user exists in college_users
            user = AuthService.get_user_by_college_id(activation_data.college_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found. Please contact admin."
                )
            
            # Step 2: Validate email matches
            if user["email"] != activation_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email does not match college ID"
                )
            
            # Step 3: Check if account is already activated
            if user.get("auth_user_id"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account already activated. Please login."
                )
            
            # Step 4: Check if account is active
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is deactivated. Please contact admin."
                )
            
            # Step 5: Create Supabase Auth user
            if not supabase_admin:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Service role key not configured"
                )
            
            auth_response = supabase_admin.auth.admin.create_user({
                "email": activation_data.email,
                "password": activation_data.password,
                "email_confirm": True  # Auto-confirm email
            })
            
            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create auth user"
                )
            
            # Step 6: Link auth_user_id to college_users
            # Use service-role client to bypass RLS when writing auth_user_id
            supabase_admin.table("college_users").update({
                "auth_user_id": auth_response.user.id
            }).eq("college_id", activation_data.college_id).execute()
            
            return {
                "message": "Account activated successfully. You can now login.",
                "college_id": activation_data.college_id,
                "email": activation_data.email
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error activating account: {str(e)}"
            )
    
    @staticmethod
    def login(email: str, password: str) -> Dict:
        """
        Login user with email and password
        """
        try:
            # Authenticate with Supabase
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Get user details from college_users
            user = AuthService.get_user_by_auth_id(auth_response.user.id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is deactivated"
                )
            
            return {
                "access_token": auth_response.session.access_token,
                "token_type": "Bearer",
                "user": user
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Login failed: {str(e)}"
            )
