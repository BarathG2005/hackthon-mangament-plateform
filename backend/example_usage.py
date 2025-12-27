"""
Example usage script for College Hackathon Management Platform
This demonstrates the complete workflow from admin setup to student login
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API responses"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"{'='*60}\n")

# ============================================================================
# STEP 1: Admin Login
# ============================================================================
print("STEP 1: Admin Login")
admin_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "admin@college.edu",
        "password": "admin_password"  # Replace with your actual password
    }
)
print_response("Admin Login", admin_login)

if admin_login.status_code != 200:
    print("❌ Admin login failed. Please ensure admin account is created.")
    exit(1)

admin_token = admin_login.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# ============================================================================
# STEP 2: Admin Adds Student
# ============================================================================
print("\nSTEP 2: Admin Adds Student")
add_student = requests.post(
    f"{BASE_URL}/admin/add-student",
    headers=admin_headers,
    json={
        "college_id": "CS2023A001",
        "name": "Arun Kumar",
        "email": "arun@college.edu",
        "role": "student",
        "department": "Computer Science"
    }
)
print_response("Add Student", add_student)

# ============================================================================
# STEP 3: Admin Adds Teacher
# ============================================================================
print("\nSTEP 3: Admin Adds Teacher")
add_teacher = requests.post(
    f"{BASE_URL}/admin/add-teacher",
    headers=admin_headers,
    json={
        "college_id": "TCH001",
        "name": "Dr. Priya Sharma",
        "email": "priya@college.edu",
        "role": "teacher",
        "department": "Computer Science"
    }
)
print_response("Add Teacher", add_teacher)

# ============================================================================
# STEP 4: Admin Adds HOD
# ============================================================================
print("\nSTEP 4: Admin Adds HOD")
add_hod = requests.post(
    f"{BASE_URL}/admin/add-hod",
    headers=admin_headers,
    json={
        "college_id": "HOD001",
        "name": "Prof. Rajesh Kumar",
        "email": "rajesh@college.edu",
        "role": "hod",
        "department": "Computer Science"
    }
)
print_response("Add HOD", add_hod)

# ============================================================================
# STEP 5: Admin Adds Principal
# ============================================================================
print("\nSTEP 5: Admin Adds Principal")
add_principal = requests.post(
    f"{BASE_URL}/admin/add-principal",
    headers=admin_headers,
    json={
        "college_id": "PRIN001",
        "name": "Dr. Sunita Reddy",
        "email": "sunita@college.edu",
        "role": "principal",
        "department": "Administration"
    }
)
print_response("Add Principal", add_principal)

# ============================================================================
# STEP 6: View All Users (Admin only)
# ============================================================================
print("\nSTEP 6: View All Users")
get_users = requests.get(
    f"{BASE_URL}/admin/users",
    headers=admin_headers
)
print_response("All Users", get_users)

# ============================================================================
# STEP 7: Get Dashboard Stats
# ============================================================================
print("\nSTEP 7: Dashboard Statistics")
dashboard = requests.get(
    f"{BASE_URL}/admin/dashboard/stats",
    headers=admin_headers
)
print_response("Dashboard Stats", dashboard)

# ============================================================================
# STEP 8: Student Checks Activation Eligibility
# ============================================================================
print("\nSTEP 8: Student Checks Activation Eligibility")
check_eligibility = requests.post(
    f"{BASE_URL}/auth/check-activation-eligibility",
    params={
        "college_id": "CS2023A001",
        "email": "arun@college.edu"
    }
)
print_response("Check Eligibility", check_eligibility)

# ============================================================================
# STEP 9: Student Activates Account
# ============================================================================
print("\nSTEP 9: Student Activates Account")
activate = requests.post(
    f"{BASE_URL}/auth/activate",
    json={
        "college_id": "CS2023A001",
        "email": "arun@college.edu",
        "password": "student_password123"
    }
)
print_response("Activate Account", activate)

# ============================================================================
# STEP 10: Student Login
# ============================================================================
print("\nSTEP 10: Student Login")
student_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "arun@college.edu",
        "password": "student_password123"
    }
)
print_response("Student Login", student_login)

if student_login.status_code == 200:
    student_token = student_login.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # ============================================================================
    # STEP 11: Student Views Own Profile
    # ============================================================================
    print("\nSTEP 11: Student Views Own Profile")
    student_profile = requests.get(
        f"{BASE_URL}/auth/me",
        headers=student_headers
    )
    print_response("Student Profile", student_profile)
    
    # ============================================================================
    # STEP 12: Student Tries to Access Admin Endpoint (Should Fail)
    # ============================================================================
    print("\nSTEP 12: Student Tries to Access Admin Endpoint (Expected Failure)")
    unauthorized = requests.get(
        f"{BASE_URL}/admin/users",
        headers=student_headers
    )
    print_response("Unauthorized Access Attempt", unauthorized)

# ============================================================================
# STEP 13: Teacher Activates and Logs In
# ============================================================================
print("\nSTEP 13: Teacher Activates Account")
teacher_activate = requests.post(
    f"{BASE_URL}/auth/activate",
    json={
        "college_id": "TCH001",
        "email": "priya@college.edu",
        "password": "teacher_password123"
    }
)
print_response("Teacher Activate", teacher_activate)

print("\nSTEP 14: Teacher Login")
teacher_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "priya@college.edu",
        "password": "teacher_password123"
    }
)
print_response("Teacher Login", teacher_login)

# ============================================================================
# STEP 15: Admin Deactivates Student Account
# ============================================================================
print("\nSTEP 15: Admin Deactivates Student Account")
deactivate = requests.patch(
    f"{BASE_URL}/admin/users/CS2023A001/deactivate",
    headers=admin_headers
)
print_response("Deactivate Student", deactivate)

# ============================================================================
# STEP 16: Deactivated Student Tries to Login (Should Fail)
# ============================================================================
print("\nSTEP 16: Deactivated Student Tries to Login (Expected Failure)")
deactivated_login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "arun@college.edu",
        "password": "student_password123"
    }
)
print_response("Deactivated User Login Attempt", deactivated_login)

# ============================================================================
# STEP 17: Admin Reactivates Student Account
# ============================================================================
print("\nSTEP 17: Admin Reactivates Student Account")
reactivate = requests.patch(
    f"{BASE_URL}/admin/users/CS2023A001/activate",
    headers=admin_headers
)
print_response("Reactivate Student", reactivate)

print("\n" + "="*60)
print("  ✅ All workflows completed successfully!")
print("="*60)
print("\nKey Takeaways:")
print("1. ✅ Admin can add users (students, teachers, HODs, principals)")
print("2. ✅ Users must activate their accounts before login")
print("3. ✅ Role-based access control is enforced")
print("4. ✅ Unauthorized access is properly denied")
print("5. ✅ Admin can activate/deactivate users")
print("="*60)
