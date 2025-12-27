-- College Hackathon Management Platform
-- Supabase SQL Schema

-- Create college_users table
CREATE TABLE IF NOT EXISTS college_users (
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

-- Create indexes for better query performance
CREATE INDEX idx_college_users_college_id ON college_users(college_id);
CREATE INDEX idx_college_users_email ON college_users(email);
CREATE INDEX idx_college_users_auth_user_id ON college_users(auth_user_id);
CREATE INDEX idx_college_users_role ON college_users(role);
CREATE INDEX idx_college_users_department ON college_users(department);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_college_users_updated_at
    BEFORE UPDATE ON college_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE college_users ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can read their own data
CREATE POLICY "Users can view own data"
    ON college_users
    FOR SELECT
    USING (auth.uid() = auth_user_id);

-- RLS Policy: Service role can do everything (for admin operations)
CREATE POLICY "Service role has full access"
    ON college_users
    FOR ALL
    USING (auth.role() = 'service_role');

-- Comments for documentation
COMMENT ON TABLE college_users IS 'Stores all college users with role-based access control';
COMMENT ON COLUMN college_users.college_id IS 'Unique college ID or roll number';
COMMENT ON COLUMN college_users.auth_user_id IS 'Links to Supabase auth.users table, NULL until account is activated';
COMMENT ON COLUMN college_users.role IS 'User role: admin, principal, hod, teacher, or student';
COMMENT ON COLUMN college_users.is_active IS 'Whether the account is active';
