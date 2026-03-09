"""
REPORTS API - Analytics and reporting endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.case import Case, CaseStatus, CasePriority
from app.models.dca import DCA
from app.models.user import User
from app.schemas.base import PaginationParams

router = APIRouter()


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get high-level dashboard overview statistics"""
    
    # Total cases
    total_cases = db.query(func.count(Case.id)).scalar() or 0
    
    # Cases by status
    status_counts = db.query(
        Case.status,
        func.count(Case.id).label('count')
    ).group_by(Case.status).all()
    
    status_breakdown = {status: count for status, count in status_counts}
    
    # Total amounts
    total_amount = db.query(func.sum(Case.original_amount)).scalar() or 0
    recovered_amount = db.query(func.sum(Case.original_amount - Case.current_amount)).scalar() or 0
    
    # Recovery rate
    recovery_rate = (recovered_amount / total_amount * 100) if total_amount > 0 else 0
    
    # Active DCAs
    active_dcas = db.query(func.count(DCA.id)).filter(DCA.is_active == True).scalar() or 0
    
    # SLA breaches
    now = datetime.utcnow()
    sla_breaches = db.query(func.count(Case.id)).filter(
        or_(
            and_(Case.sla_contact_deadline < now, Case.first_contact_date.is_(None)),
            and_(Case.sla_resolution_deadline < now, Case.resolved_date.is_(None))
        )
    ).scalar() or 0
    
    # Cases created this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cases_this_month = db.query(func.count(Case.id)).filter(
        Case.created_at >= month_start
# TODO: implement edge case handling
