from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.hackathon import (
    HackathonCreate,
    HackathonResponse,
    HackathonRegistrationCreate,
    HackathonRegistrationResponse,
    HackathonStatsResponse,
)
from services.hackathon import HackathonService
from dependencies.auth import (
    get_current_user,
    require_admin_principal_hod,
    require_admin_principal_hod_teacher,
)

router = APIRouter(prefix="/hackathons", tags=["Hackathons"])


@router.post("/", response_model=HackathonResponse, status_code=status.HTTP_201_CREATED)
def create_hackathon(
    payload: HackathonCreate,
    current_user: dict = Depends(require_admin_principal_hod_teacher),
):
    created = HackathonService.create_hackathon(payload.dict(), current_user)
    return HackathonResponse(**created)


@router.get("/", response_model=List[HackathonResponse])
def list_hackathons(include_inactive: bool = False, current_user: dict = Depends(get_current_user)):
    items = HackathonService.list_hackathons(include_inactive)
    return [HackathonResponse(**i) for i in items]


@router.delete("/{hackathon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hackathon(
    hackathon_id: str,
    current_user: dict = Depends(require_admin_principal_hod_teacher),
):
    HackathonService.delete_hackathon(hackathon_id)
    return None


@router.post("/{hackathon_id}/register", response_model=HackathonRegistrationResponse)
def register_for_hackathon(
    hackathon_id: str,
    payload: HackathonRegistrationCreate,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access required")

    reg = HackathonService.register_for_hackathon(hackathon_id, current_user, payload.dict())
    return HackathonRegistrationResponse(**reg)


@router.get("/{hackathon_id}/registrations", response_model=List[HackathonRegistrationResponse])
def list_registrations(
    hackathon_id: str,
    current_user: dict = Depends(require_admin_principal_hod_teacher),
):
    rows = HackathonService.list_registrations(hackathon_id)
    return [HackathonRegistrationResponse(**r) for r in rows]


@router.patch("/registrations/{registration_id}/acknowledge", response_model=HackathonRegistrationResponse)
def acknowledge_registration(
    registration_id: str,
    status_value: str,
    note: str | None = None,
    current_user: dict = Depends(require_admin_principal_hod_teacher),
):
    updated = HackathonService.acknowledge_registration(registration_id, current_user, status_value, note)
    return HackathonRegistrationResponse(**updated)


@router.get("/{hackathon_id}/stats", response_model=HackathonStatsResponse)
def hackathon_stats(
    hackathon_id: str,
    current_user: dict = Depends(require_admin_principal_hod_teacher),
):
    stats = HackathonService.get_hackathon_stats(hackathon_id)
    return HackathonStatsResponse(**stats)
