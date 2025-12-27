from fastapi import APIRouter, Depends, HTTPException, status
from models.user import AddUserRequest, UserResponse, UserRole
from services.auth import AuthService
from dependencies.auth import require_admin, require_admin_or_principal, get_current_user
from config.supabase import supabase
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/add-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_user(user_data: AddUserRequest,current_user: dict = Depends(require_admin)):
  
    new_user = AuthService.add_user(user_data)
    return UserResponse(**new_user)

@router.post("/add-student", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_student(
    user_data: AddUserRequest,
    current_user: dict = Depends(require_admin)
):
    """
    Convenience endpoint for adding students
    Only accessible by admin
    """
    # Force role to be student
    user_data.role = UserRole.STUDENT
    new_user = AuthService.add_user(user_data)
    return UserResponse(**new_user)

@router.post("/add-teacher", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_teacher(
    user_data: AddUserRequest,
    current_user: dict = Depends(require_admin_or_principal)
):
    """
    Endpoint for adding teachers
    Accessible by admin or principal
    """
    # Force role to be teacher
    user_data.role = UserRole.TEACHER
    new_user = AuthService.add_user(user_data)
    return UserResponse(**new_user)

@router.post("/add-hod", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_hod(
    user_data: AddUserRequest,
    current_user: dict = Depends(require_admin_or_principal)
):
    """
    Endpoint for adding HODs
    Accessible by admin or principal
    """
    # Force role to be HOD
    user_data.role = UserRole.HOD
    
    if not user_data.department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department is required for HOD role"
        )
    
    new_user = AuthService.add_user(user_data)
    return UserResponse(**new_user)

@router.post("/add-principal", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_principal(
    user_data: AddUserRequest,
    current_user: dict = Depends(require_admin)
):
    """
    Endpoint for adding principals
    Only accessible by admin
    """
    # Force role to be principal
    user_data.role = UserRole.PRINCIPAL
    new_user = AuthService.add_user(user_data)
    return UserResponse(**new_user)

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    role: str = None,
    department: str = None,
    current_user: dict = Depends(require_admin)
):
    """
    Get all users with optional filters
    Only accessible by admin
    
    - **role**: Filter by role (optional)
    - **department**: Filter by department (optional)
    """
    try:
        query = supabase.table("college_users").select("*")
        
        if role:
            query = query.eq("role", role)
        
        if department:
            query = query.eq("department", department)
        
        response = query.execute()
        
        return [UserResponse(**user) for user in response.data]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.get("/users/{college_id}", response_model=UserResponse)
def get_user_by_id(
    college_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Get user details by college_id
    Only accessible by admin
    """
    user = AuthService.get_user_by_college_id(college_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)

@router.patch("/users/{college_id}/deactivate")
def deactivate_user(
    college_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Deactivate a user account
    Only accessible by admin
    """
    try:
        user = AuthService.get_user_by_college_id(college_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        supabase.table("college_users").update({
            "is_active": False
        }).eq("college_id", college_id).execute()
        
        return {"message": f"User {college_id} deactivated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating user: {str(e)}"
        )

@router.patch("/users/{college_id}/activate")
def activate_user(
    college_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Reactivate a user account
    Only accessible by admin
    """
    try:
        user = AuthService.get_user_by_college_id(college_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        supabase.table("college_users").update({
            "is_active": True
        }).eq("college_id", college_id).execute()
        
        return {"message": f"User {college_id} activated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating user: {str(e)}"
        )

@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_user: dict = Depends(require_admin)
):
    """
    Get dashboard statistics for admin
    Returns counts of users by role and activation status
    """
    try:
        # Get all users
        all_users = supabase.table("college_users").select("role, auth_user_id, is_active").execute()
        
        users_data = all_users.data
        
        stats = {
            "total_users": len(users_data),
            "activated_users": len([u for u in users_data if u.get("auth_user_id")]),
            "pending_activation": len([u for u in users_data if not u.get("auth_user_id")]),
            "by_role": {
                "admin": len([u for u in users_data if u.get("role") == "admin"]),
                "principal": len([u for u in users_data if u.get("role") == "principal"]),
                "hod": len([u for u in users_data if u.get("role") == "hod"]),
                "teacher": len([u for u in users_data if u.get("role") == "teacher"]),
                "student": len([u for u in users_data if u.get("role") == "student"])
            },
            "active_users": len([u for u in users_data if u.get("is_active", True)]),
            "inactive_users": len([u for u in users_data if not u.get("is_active", True)])
        }
        
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard stats: {str(e)}"
        )
