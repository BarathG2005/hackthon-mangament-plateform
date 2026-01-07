# 🔐 How to Login and Add Users - Step by Step

## 🎯 Quick Answer

**Login Endpoint:** http://127.0.0.1:8000/docs (Swagger UI)
- Or directly: `POST http://127.0.0.1:8000/auth/login`

**Add User Endpoint:** `POST http://127.0.0.1:8000/admin/add-student`
- (Must be logged in as admin first)

---

## ⚠️ IMPORTANT: First-Time Setup Required

Before you can login, you MUST:
1. ✅ Create the `college_users` table in Supabase
2. ✅ Create your first admin user
3. ✅ Then you can login!

**If you haven't done this yet, follow the steps below:**

---

## 📋 STEP 1: Create Table in Supabase (One-Time Setup)

### Quick SQL Method (30 seconds):
1. Go to https://app.supabase.com
2. Select your project
3. Click **SQL Editor** → **New Query**
4. Copy and paste this:

```sql
CREATE TABLE college_users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    college_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'principal', 'hod', 'teacher', 'student')),
    department VARCHAR(100),
    auth_user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_college_users_college_id ON college_users(college_id);
CREATE INDEX idx_college_users_email ON college_users(email);
CREATE INDEX idx_college_users_auth_user_id ON college_users(auth_user_id);
CREATE INDEX idx_college_users_role ON college_users(role);

ALTER TABLE college_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own data" ON college_users FOR SELECT USING (auth.uid() = auth_user_id);
CREATE POLICY "Service role has full access" ON college_users FOR ALL USING (auth.role() = 'service_role');
```

5. Click **Run**

✅ **Expected:** "Success. No rows returned"

---

## 👤 STEP 2: Create Your First Admin User

### A. Create Admin in Supabase Auth
1. Go to **Authentication** → **Users**
2. Click **Add user** → **Create new user**
3. Fill in:
   ```
   Email: admin@college.edu
   Password: Admin@123456
   ✓ Auto Confirm User (check this box)
   ```
4. Click **Create user**
5. **COPY THE USER ID** (looks like: `abc-123-def-456...`)

### B. Link Admin to college_users Table
1. Go to **Table Editor** → `college_users` → Click **Insert** → **Insert row**
2. Fill in these fields:
   ```
   college_id: ADMIN001
   name: System Administrator  
   email: admin@college.edu
   role: admin
   auth_user_id: [PASTE THE USER ID YOU COPIED]
   is_active: true
   ```
3. Click **Save**

**OR use SQL Editor:**
```sql
INSERT INTO college_users (college_id, name, email, role, auth_user_id, is_active)
VALUES (
    'ADMIN001',
    'System Administrator',
    'admin@college.edu',
    'admin',
    'PASTE-YOUR-USER-ID-HERE',  -- Replace with actual UUID
    TRUE
);
```

✅ **You now have an admin account!**

---

## 🔑 STEP 3: Login as Admin

### Option A: Using Swagger UI (Easiest)

1. **Open:** http://127.0.0.1:8000/docs

2. **Find the login endpoint:**
   - Scroll to **Authentication** section
   - Click `POST /auth/login`
   - Click **Try it out**

3. **Enter credentials:**
   ```json
   {
     "email": "admin@college.edu",
     "password": "Admin@123456"
   }
   ```

4. **Click Execute**

5. **Copy the access_token** from the response:
   ```json
   {
     "access_token": "eyJhbGc...",  ← Copy this!
     "token_type": "Bearer",
     "user": {
       "college_id": "ADMIN001",
       "role": "admin",
       ...
     }
   }
   ```

6. **Authorize in Swagger:**
   - Click **🔒 Authorize** button (top right)
   - Enter: `Bearer YOUR_TOKEN_HERE`
   - Click **Authorize**
   - Click **Close**

✅ **You're now logged in as admin!**

---

### Option B: Using cURL (Terminal)

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@college.edu",
    "password": "Admin@123456"
  }'
```

---

## 👥 STEP 4: Add Your First User (Student)

Now that you're logged in as admin, you can add users!

### In Swagger UI:

1. **Make sure you're authorized** (Step 3.6 above)

2. **Find:** `POST /admin/add-student`

3. **Click Try it out**

4. **Enter student details:**
   ```json
   {
     "college_id": "CS2023A001",
     "name": "John Doe",
     "email": "john@college.edu",
     "role": "student",
     "department": "Computer Science"
   }
   ```

5. **Click Execute**

✅ **Student added successfully!**

---

## 📚 Available Endpoints

### Authentication Endpoints (No login required):
- `POST /auth/login` - Login with email/password
- `POST /auth/activate` - Activate account (after admin adds you)
- `POST /auth/check-activation-eligibility` - Check if you can activate

### Admin Endpoints (Admin login required):
- `POST /admin/add-student` - Add a student
- `POST /admin/add-teacher` - Add a teacher
- `POST /admin/add-hod` - Add HOD
- `POST /admin/add-principal` - Add principal
- `GET /admin/users` - List all users
- `GET /admin/users/{college_id}` - Get specific user
- `PATCH /admin/users/{college_id}/activate` - Activate user
- `PATCH /admin/users/{college_id}/deactivate` - Deactivate user
- `GET /admin/dashboard/stats` - Get statistics

---

## 🔄 Complete User Flow Example

### 1. Admin adds a student:
```json
POST /admin/add-student
{
  "college_id": "CS2023A001",
  "name": "Jane Smith",
  "email": "jane@college.edu",
  "role": "student",
  "department": "Computer Science"
}
```

### 2. Student activates their account:
```json
POST /auth/activate
{
  "college_id": "CS2023A001",
  "email": "jane@college.edu",
  "password": "MySecurePassword123"
}
```

### 3. Student logs in:
```json
POST /auth/login
{
  "email": "jane@college.edu",
  "password": "MySecurePassword123"
}
```

---

## 🎯 Quick Test Checklist

- [ ] Server running at http://127.0.0.1:8000
- [ ] Can access http://127.0.0.1:8000/docs
- [ ] `college_users` table exists in Supabase
- [ ] Admin user created in Supabase Auth
- [ ] Admin record in `college_users` table
- [ ] Admin can login successfully
- [ ] Got access token from login
- [ ] Authorized in Swagger UI
- [ ] Can add a student
- [ ] Student added successfully

---

## 🆘 Troubleshooting

### "User not found" when logging in
→ Make sure admin exists in BOTH:
  - Supabase Auth (Authentication → Users)
  - college_users table (Table Editor)

### "Invalid credentials"
→ Check your password is correct: `Admin@123456`

### "Forbidden" or "Access denied"
→ Make sure you clicked **Authorize** in Swagger UI with your token

### "Table 'college_users' does not exist"
→ Go back to STEP 1 and create the table

### Can't add users
→ Make sure you're logged in as admin and authorized

---

## 💡 Pro Tips

1. **Keep Swagger UI open** - Easiest way to test APIs
2. **Use the Authorize button** - After login, click 🔒 and paste your token
3. **Check the response** - Green = success, Red = error
4. **Copy tokens immediately** - You'll need them for other requests
5. **Test with Postman** - For more advanced testing

---

## 🎉 Summary

**Login URL:** http://127.0.0.1:8000/docs
- Use `POST /auth/login` 
- Email: `admin@college.edu`
- Password: `Admin@123456`

**Add User:**
- First: Login as admin
- Then: Click 🔒 Authorize
- Then: Use `POST /admin/add-student`

**Your API is ready to use!** 🚀





eyJhbGciOiJFUzI1NiIsImtpZCI6IjljNjRhYTRjLThjY2ItNDA3Yy1hZDM5LTY2ZDMzNmNiNTgyNiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3BqenBla3Zjb3Rub2ljcWlsZGZmLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIwNjM4YjJlNS0xMWQzLTRkMTQtYjMyNy1kODM0YmIwN2Q4NzIiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY3NDE3NTU0LCJpYXQiOjE3Njc0MTM5NTQsImVtYWlsIjoiYmFyYXRoZy5jc2UyMDIzQGNpdGNoZW5uYWkubmV0IiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoicGFzc3dvcmQiLCJ0aW1lc3RhbXAiOjE3Njc0MTM5NTR9XSwic2Vzc2lvbl9pZCI6IjgwMmI3ZDI2LTM3NzAtNDY4NS1iMzRkLWM5YWYxM2FlYTkyZCIsImlzX2Fub255bW91cyI6ZmFsc2V9.uaCCs44KlxnpYjvwGr0dtAFqsNpmsGyYLM_q4PS_Nm5CB4G5vFTD1UlyLVeHDA2Ru6Vcl_FZfGgkDTJaxUFpdw