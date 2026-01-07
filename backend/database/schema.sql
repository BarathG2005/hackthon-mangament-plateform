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

-- Hackathons posted by staff
CREATE TABLE IF NOT EXISTS hackathons (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    link TEXT NOT NULL,
    domain TEXT,
    deadline TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by_college_id VARCHAR(50) REFERENCES college_users(college_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hackathons_deadline ON hackathons(deadline);
CREATE INDEX IF NOT EXISTS idx_hackathons_active ON hackathons(is_active);

-- Student registrations per hackathon
CREATE TABLE IF NOT EXISTS hackathon_registrations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    hackathon_id UUID REFERENCES hackathons(id) ON DELETE CASCADE,
    student_college_id VARCHAR(50) REFERENCES college_users(college_id) ON DELETE CASCADE,
    link_submission TEXT,
    notes TEXT,
    status TEXT DEFAULT 'applied' CHECK (status IN ('applied','acknowledged','rejected')),
    acknowledged_by VARCHAR(50) REFERENCES college_users(college_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hackathon_registrations_hackathon ON hackathon_registrations(hackathon_id);
CREATE INDEX IF NOT EXISTS idx_hackathon_registrations_student ON hackathon_registrations(student_college_id);
CREATE INDEX IF NOT EXISTS idx_hackathon_registrations_status ON hackathon_registrations(status);

-- Triggers for updated_at
CREATE TRIGGER update_hackathons_updated_at
    BEFORE UPDATE ON hackathons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hackathon_registrations_updated_at
    BEFORE UPDATE ON hackathon_registrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE hackathons ENABLE ROW LEVEL SECURITY;
ALTER TABLE hackathon_registrations ENABLE ROW LEVEL SECURITY;

-- Policies
-- Hackathons: anyone authenticated can view, service role can do all
CREATE POLICY "Hackathons select for authenticated" ON hackathons
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Hackathons service role all" ON hackathons
    FOR ALL USING (auth.role() = 'service_role');

-- Registrations: students can view/insert own, service role all
CREATE POLICY "Registrations select own" ON hackathon_registrations
    FOR SELECT USING (auth.uid() IS NOT NULL);

CREATE POLICY "Registrations insert own" ON hackathon_registrations
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Registrations service role all" ON hackathon_registrations
    FOR ALL USING (auth.role() = 'service_role');

-- Approval workflow fields for hackathons
ALTER TABLE hackathons
    ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual',
    ADD COLUMN IF NOT EXISTS approval_status TEXT DEFAULT 'approved' CHECK (approval_status IN ('pending','approved','rejected')),
    ADD COLUMN IF NOT EXISTS approved_by VARCHAR(50) REFERENCES college_users(college_id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS suggested_by_model TEXT;

-- Ensure existing rows are marked approved
UPDATE hackathons SET approval_status = COALESCE(approval_status, 'approved'), source = COALESCE(source, 'manual') WHERE approval_status IS NULL OR source IS NULL;
