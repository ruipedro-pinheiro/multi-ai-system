"""Waitlist routes for CHIKA"""
from fastapi import APIRouter, Request
from database import SessionLocal, WaitlistEntry
from pydantic import BaseModel

router = APIRouter(prefix="/waitlist", tags=["waitlist"])

class WaitlistRequest(BaseModel):
    email: str

@router.get("/stats")
async def get_waitlist_stats():
    """Get waitlist statistics"""
    db = SessionLocal()
    try:
        total_signups = db.query(WaitlistEntry).count()
        return {
            "total_signups": total_signups,
            "success": True
        }
    finally:
        db.close()

@router.post("/add")
async def add_to_waitlist(
    request: Request,
    data: WaitlistRequest
):
    """Add email to waitlist"""
    db = SessionLocal()
    try:
        # Check if already exists
        existing = db.query(WaitlistEntry).filter(WaitlistEntry.email == data.email).first()
        if existing:
            return {"success": False, "message": "Already registered"}
        
        # Add new entry
        entry = WaitlistEntry(
            email=data.email,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "")[:500]
        )
        db.add(entry)
        db.commit()
        
        return {
            "success": True,
            "message": "Added to waitlist",
            "total": db.query(WaitlistEntry).count()
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()
