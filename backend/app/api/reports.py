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
    ).scalar() or 0
    
    return {
        "total_cases": total_cases,
        "total_amount": round(total_amount, 2),
        "recovered_amount": round(recovered_amount, 2),
        "recovery_rate": round(recovery_rate, 2),
        "active_dcas": active_dcas,
        "sla_breaches": sla_breaches,
        "cases_this_month": cases_this_month,
        "status_breakdown": status_breakdown,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/performance/dcas")
async def get_dca_performance_report(
    period_days: int = Query(30, description="Report period in days"),
    dca_id: Optional[str] = Query(None, description="Specific DCA ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get DCA performance report"""
    
    period_start = datetime.utcnow() - timedelta(days=period_days)
    
    # Base query
    query = db.query(DCA).filter(DCA.is_active == True)
    
    if dca_id:
        query = query.filter(DCA.id == dca_id)
    
    dcas = query.all()
    
    performance_data = []
    
    for dca in dcas:
        # Cases assigned in period
        cases_assigned = db.query(func.count(Case.id)).filter(
            Case.dca_id == dca.id,
            Case.allocation_date >= period_start
        ).scalar() or 0
        
        # Cases resolved in period
        cases_resolved = db.query(func.count(Case.id)).filter(
            Case.dca_id == dca.id,
            Case.resolved_date >= period_start,
            Case.status == CaseStatus.RESOLVED
        ).scalar() or 0
        
        # Amount assigned and recovered
        amount_assigned = db.query(func.sum(Case.original_amount)).filter(
            Case.dca_id == dca.id,
            Case.allocation_date >= period_start
        ).scalar() or 0
        
        amount_recovered = db.query(func.sum(Case.original_amount - Case.current_amount)).filter(
            Case.dca_id == dca.id,
            Case.resolved_date >= period_start,
            Case.status == CaseStatus.RESOLVED
        ).scalar() or 0
        
        # Calculate metrics
        resolution_rate = (cases_resolved / cases_assigned * 100) if cases_assigned > 0 else 0
        recovery_rate = (amount_recovered / amount_assigned * 100) if amount_assigned > 0 else 0
        
        # Average resolution time
        avg_resolution_days = db.query(
            func.avg(func.julianday(Case.resolved_date) - func.julianday(Case.allocation_date))
        ).filter(
            Case.dca_id == dca.id,
            Case.resolved_date >= period_start,
            Case.status == CaseStatus.RESOLVED
        ).scalar() or 0
        
        # SLA compliance
        total_cases_with_sla = db.query(func.count(Case.id)).filter(
            Case.dca_id == dca.id,
            Case.allocation_date >= period_start,
            Case.sla_resolution_deadline.isnot(None)
        ).scalar() or 0
        
        sla_compliant_cases = db.query(func.count(Case.id)).filter(
            Case.dca_id == dca.id,
            Case.allocation_date >= period_start,
            Case.resolved_date <= Case.sla_resolution_deadline
        ).scalar() or 0
        
        sla_compliance = (sla_compliant_cases / total_cases_with_sla * 100) if total_cases_with_sla > 0 else 0
        
        performance_data.append({
            "dca_id": dca.id,
            "dca_name": dca.name,
            "dca_code": dca.code,
            "cases_assigned": cases_assigned,
            "cases_resolved": cases_resolved,
            "resolution_rate": round(resolution_rate, 2),
            "amount_assigned": round(amount_assigned, 2),
            "amount_recovered": round(amount_recovered, 2),
            "recovery_rate": round(recovery_rate, 2),
            "avg_resolution_days": round(avg_resolution_days, 1),
            "sla_compliance": round(sla_compliance, 2),
            "performance_score": dca.performance_score
        })
    
    # Sort by performance score
    performance_data.sort(key=lambda x: x["performance_score"], reverse=True)
    
    return {
        "period_start": period_start.isoformat(),
        "period_end": datetime.utcnow().isoformat(),
        "period_days": period_days,
        "total_dcas": len(performance_data),
        "performance_data": performance_data
    }


@router.get("/recovery/trends")
async def get_recovery_trends(
    period_days: int = Query(90, description="Report period in days"),
    granularity: str = Query("daily", description="Data granularity: daily, weekly, monthly"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get recovery trends over time"""
    
    period_start = datetime.utcnow() - timedelta(days=period_days)
    
    # Determine date grouping based on granularity
    if granularity == "weekly":
        date_format = "%Y-%W"
        date_trunc = func.strftime('%Y-%W', Case.resolved_date)
    elif granularity == "monthly":
        date_format = "%Y-%m"
        date_trunc = func.strftime('%Y-%m', Case.resolved_date)
    else:  # daily
        date_format = "%Y-%m-%d"
        date_trunc = func.date(Case.resolved_date)
    
    # Recovery trends
    recovery_trends = db.query(
        date_trunc.label('period'),
        func.count(Case.id).label('cases_resolved'),
        func.sum(Case.original_amount - Case.current_amount).label('amount_recovered'),
        func.avg(Case.recovery_score).label('avg_recovery_score')
    ).filter(
        Case.resolved_date >= period_start,
        Case.status == CaseStatus.RESOLVED
    ).group_by(date_trunc).order_by(date_trunc).all()
    
# TODO: implement edge case handling
