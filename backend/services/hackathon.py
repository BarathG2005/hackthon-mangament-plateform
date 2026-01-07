from datetime import datetime
from typing import List, Dict
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from config.supabase import supabase_admin


class HackathonService:
    """Service layer for hackathon posts and registrations"""

    @staticmethod
    def create_hackathon(payload: Dict, creator: Dict) -> Dict:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            source = payload.get("source", "manual") or "manual"
            approval_status = "pending" if source == "ai" else "approved"
            is_active = payload.get("is_active", True) if approval_status == "approved" else False
            record = jsonable_encoder(
                {
                    "title": payload["title"],
                    "description": payload.get("description"),
                    "link": payload.get("link"),
                    "domain": payload.get("domain"),
                    "deadline": payload.get("deadline"),
                    "is_active": is_active,
                    "source": source,
                    "approval_status": approval_status,
                    "approved_by": None,
                    "created_by_college_id": creator.get("college_id"),
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
            # Keep optional AI metadata only if the column exists in the DB; fallback without it when missing.
            if payload.get("suggested_by_model") is not None:
                record["suggested_by_model"] = payload.get("suggested_by_model")

            try:
                res = supabase_admin.table("hackathons").insert(record).execute()
                return res.data[0]
            except Exception as exc:
                msg = str(exc)
                if "suggested_by_model" in msg and "schema cache" in msg:
                    record.pop("suggested_by_model", None)
                    res = supabase_admin.table("hackathons").insert(record).execute()
                    return res.data[0]
                raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating hackathon: {e}")

    @staticmethod
    def ai_suggest(payload: Dict, creator: Dict) -> Dict:
        # force AI source + pending approval
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")

        link = payload.get("link")
        title = payload.get("title")

        try:
            # Prevent duplicates (approved/pending/rejected) on same link or title
            existing = (
                supabase_admin.table("hackathons")
                .select("id, approval_status")
                .or_(f"link.eq.{link},title.eq.{title}")
                .limit(1)
                .execute()
            )
            if existing.data:
                status_value = existing.data[0].get("approval_status")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hackathon already present with status '{status_value}', not suggesting again",
                )

            enriched = {
                **payload,
                "source": "ai",
                "is_active": False,
            }
            return HackathonService.create_hackathon(enriched, creator)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error suggesting hackathon: {e}")

    @staticmethod
    def list_hackathons(include_inactive: bool = False) -> List[Dict]:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            query = supabase_admin.table("hackathons").select("*").eq("approval_status", "approved")
            if not include_inactive:
                query = query.eq("is_active", True)
            res = query.order("deadline", desc=False).order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching hackathons: {e}")

    @staticmethod
    def list_pending() -> List[Dict]:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            res = (
                supabase_admin.table("hackathons")
                .select("*")
                .eq("approval_status", "pending")
                .order("created_at", desc=True)
                .execute()
            )
            return res.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching pending hackathons: {e}")

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

            record = jsonable_encoder(
                {
                    "hackathon_id": hackathon_id,
                    "student_college_id": student.get("college_id"),
                    "link_submission": payload.get("link_submission"),
                    "notes": payload.get("notes"),
                    "status": "applied",
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
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
    def approve_hackathon(hackathon_id: str, approver: Dict) -> Dict:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            existing = (
                supabase_admin.table("hackathons")
                .select("approval_status")
                .eq("id", hackathon_id)
                .limit(1)
                .execute()
            )
            if not existing.data:
                raise HTTPException(status_code=404, detail="Hackathon not found")
            status_value = existing.data[0].get("approval_status")
            if status_value != "pending":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already decided")

            res = (
                supabase_admin.table("hackathons")
                .update(
                    {
                        "approval_status": "approved",
                        "approved_by": approver.get("college_id"),
                        "is_active": True,
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .eq("id", hackathon_id)
                .execute()
            )
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error approving hackathon: {e}")

    @staticmethod
    def reject_hackathon(hackathon_id: str, approver: Dict, note: str | None = None) -> Dict:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")
        try:
            existing = (
                supabase_admin.table("hackathons")
                .select("approval_status")
                .eq("id", hackathon_id)
                .limit(1)
                .execute()
            )
            if not existing.data:
                raise HTTPException(status_code=404, detail="Hackathon not found")
            status_value = existing.data[0].get("approval_status")
            if status_value != "pending":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already decided")

            res = (
                supabase_admin.table("hackathons")
                .update(
                    {
                        "approval_status": "rejected",
                        "approved_by": approver.get("college_id"),
                        "is_active": False,
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .eq("id", hackathon_id)
                .execute()
            )
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error rejecting hackathon: {e}")

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

    @staticmethod
    def get_hackathon_stats(hackathon_id: str) -> Dict:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Service role key not configured")

        try:
            hackathon_res = (
                supabase_admin.table("hackathons")
                .select("id, title")
                .eq("id", hackathon_id)
                .limit(1)
                .execute()
            )
            if not hackathon_res.data:
                raise HTTPException(status_code=404, detail="Hackathon not found")
            hackathon = hackathon_res.data[0]

            regs_res = (
                supabase_admin.table("hackathon_registrations")
                .select("student_college_id")
                .eq("hackathon_id", hackathon_id)
                .execute()
            )
            reg_ids = [row.get("student_college_id") for row in regs_res.data or [] if row.get("student_college_id")]

            # Total students per department
            totals_res = (
                supabase_admin.table("college_users")
                .select("department")
                .eq("role", "student")
                .execute()
            )
            total_by_dept: Dict[str | None, int] = {}
            for row in totals_res.data or []:
                dept = row.get("department")
                total_by_dept[dept] = total_by_dept.get(dept, 0) + 1

            registered_by_dept: Dict[str | None, int] = {}
            if reg_ids:
                students_res = (
                    supabase_admin.table("college_users")
                    .select("college_id, department")
                    .in_("college_id", reg_ids)
                    .execute()
                )
                for row in students_res.data or []:
                    dept = row.get("department")
                    registered_by_dept[dept] = registered_by_dept.get(dept, 0) + 1

            per_dept_stats = []
            for dept, total in total_by_dept.items():
                registered_count = registered_by_dept.get(dept, 0)
                remaining = max(total - registered_count, 0)
                per_dept_stats.append(
                    {
                        "department": dept,
                        "registered": registered_count,
                        "remaining": remaining,
                        "total_students": total,
                    }
                )

            return jsonable_encoder(
                {
                    "hackathon_id": hackathon.get("id"),
                    "title": hackathon.get("title"),
                    "total_registered": len(reg_ids),
                    "per_department": per_dept_stats,
                    "last_updated": datetime.utcnow(),
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching stats: {e}")
