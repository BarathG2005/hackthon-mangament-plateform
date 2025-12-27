from supabase import create_client, Client
from config.settings import settings

# Initialize Supabase client (for user operations)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

# Initialize Supabase admin client (for admin operations like creating users)
supabase_admin: Client = create_client(
    settings.SUPABASE_URL, 
    settings.SUPABASE_SERVICE_ROLE_KEY
) if settings.SUPABASE_SERVICE_ROLE_KEY else None
