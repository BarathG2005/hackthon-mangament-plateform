from datetime import datetime
from typing import List, Dict
from fastapi import HTTPException, status
from config.supabase import supabase_admin


class HackathonService:
    """Service layer for hackathon posts and registrations"""

    @staticmethod
    def create_hackathon(payload: Dict, creator: Dict) -> Dict:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            record = {
                "title": payload["title"],
                "description": payload.get("description"),
                "link": payload["link"],
                "domain": payload.get("domain"),
                "deadline": payload.get("deadline"),
                "is_active": payload.get("is_active", True),
                "created_by_college_id": creator.get("college_id"),
                "created_at": datetime.utcnow().isoformat(),
            }
            res = supabase_admin.table("hackathons").insert(record).execute()
            return res.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating hackathon: {e}")

    @staticmethod
    def list_hackathons(include_inactive: bool = False) -> List[Dict]:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            query = supabase_admin.table("hackathons").select("*")
            if not include_inactive:
                query = query.eq("is_active", True)
            res = query.order("deadline", desc=False).order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching hackathons: {e}")

    @staticmethod
    def register_for_hackathon(hackathon_id: str, student: Dict, payload: Dict) -> Dict:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            # prevent duplicate registration per student per hackathon
            existing = (
                supabase_admin.table("hackathon_registrations")
                .select("id")
                .eq("hackathon_id", hackathon_id)
                .eq("student_college_id", student.get("college_id"))
                .execute()
            )
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already registered for this hackathon",
                )

            record = {
                "hackathon_id": hackathon_id,
                "student_college_id": student.get("college_id"),
                "link_submission": payload.get("link_submission"),
                "notes": payload.get("notes"),
                "status": "applied",
                "created_at": datetime.utcnow().isoformat(),
            }
            res = supabase_admin.table("hackathon_registrations").insert(record).execute()
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error registering: {e}")

    @staticmethod
    def list_registrations(hackathon_id: str) -> List[Dict]:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            res = (
                supabase_admin.table("hackathon_registrations")
                .select("*")
                .eq("hackathon_id", hackathon_id)
                .execute()
            )
            return res.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching registrations: {e}")

    @staticmethod
    def delete_hackathon(hackathon_id: str) -> None:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            res = supabase_admin.table("hackathons").delete().eq("id", hackathon_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Hackathon not found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting hackathon: {e}")

    @staticmethod
    def acknowledge_registration(registration_id: str, reviewer: Dict, status_value: str, note: str | None = None) -> Dict:
        if status_value not in {"acknowledged", "rejected"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            res = (
                supabase_admin.table("hackathon_registrations")
                .update(
                    {
                        "status": status_value,
                        "acknowledged_by": reviewer.get("college_id"),
                        "notes": note,
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .eq("id", registration_id)
                .execute()
            )
            if not res.data:
                raise HTTPException(status_code=404, detail="Registration not found")
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating registration: {e}")
