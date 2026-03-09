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
    
    # Case creation trends
    creation_trends = db.query(
        date_trunc.label('period'),
        func.count(Case.id).label('cases_created'),
        func.sum(Case.original_amount).label('amount_created')
    ).filter(
        Case.created_at >= period_start
    ).group_by(date_trunc).order_by(date_trunc).all()
    
    # Combine data
    trends_data = []
    recovery_dict = {str(trend.period): trend for trend in recovery_trends}
    creation_dict = {str(trend.period): trend for trend in creation_trends}
    
    all_periods = set(recovery_dict.keys()) | set(creation_dict.keys())
    
    for period in sorted(all_periods):
        recovery = recovery_dict.get(period)
        creation = creation_dict.get(period)
        
        trends_data.append({
            "period": period,
            "cases_created": creation.cases_created if creation else 0,
            "amount_created": float(creation.amount_created or 0) if creation else 0,
            "cases_resolved": recovery.cases_resolved if recovery else 0,
            "amount_recovered": float(recovery.amount_recovered or 0) if recovery else 0,
            "avg_recovery_score": float(recovery.avg_recovery_score or 0) if recovery else 0
        })
    
    return {
        "period_start": period_start.isoformat(),
        "period_end": datetime.utcnow().isoformat(),
        "granularity": granularity,
        "trends": trends_data
    }


@router.get("/sla/compliance")
async def get_sla_compliance_report(
    period_days: int = Query(30, description="Report period in days"),
    dca_id: Optional[str] = Query(None, description="Specific DCA ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get SLA compliance report"""
    
    period_start = datetime.utcnow() - timedelta(days=period_days)
    now = datetime.utcnow()
    
    # Base query
    query = db.query(Case).filter(Case.created_at >= period_start)
    
    if dca_id:
        query = query.filter(Case.dca_id == dca_id)
    
    # Contact SLA compliance
    contact_sla_total = query.filter(Case.sla_contact_deadline.isnot(None)).count()
    contact_sla_met = query.filter(
        Case.first_contact_date <= Case.sla_contact_deadline
    ).count()
    contact_sla_breached = query.filter(
        and_(
            Case.sla_contact_deadline < now,
            Case.first_contact_date.is_(None)
        )
    ).count()
    
    # Resolution SLA compliance
    resolution_sla_total = query.filter(Case.sla_resolution_deadline.isnot(None)).count()
    resolution_sla_met = query.filter(
        Case.resolved_date <= Case.sla_resolution_deadline
    ).count()
    resolution_sla_breached = query.filter(
        and_(
            Case.sla_resolution_deadline < now,
            Case.resolved_date.is_(None)
        )
    ).count()
    
    # Calculate compliance rates
    contact_compliance_rate = (contact_sla_met / contact_sla_total * 100) if contact_sla_total > 0 else 0
    resolution_compliance_rate = (resolution_sla_met / resolution_sla_total * 100) if resolution_sla_total > 0 else 0
    
    # SLA breaches by priority
    priority_breaches = db.query(
        Case.priority,
        func.count(Case.id).label('breach_count')
    ).filter(
        Case.created_at >= period_start,
        or_(
            and_(Case.sla_contact_deadline < now, Case.first_contact_date.is_(None)),
            and_(Case.sla_resolution_deadline < now, Case.resolved_date.is_(None))
        )
    ).group_by(Case.priority).all()
    
    priority_breach_breakdown = {priority: count for priority, count in priority_breaches}
    
    return {
        "period_start": period_start.isoformat(),
        "period_end": datetime.utcnow().isoformat(),
        "contact_sla": {
            "total_cases": contact_sla_total,
            "met": contact_sla_met,
            "breached": contact_sla_breached,
            "compliance_rate": round(contact_compliance_rate, 2)
        },
        "resolution_sla": {
            "total_cases": resolution_sla_total,
            "met": resolution_sla_met,
            "breached": resolution_sla_breached,
            "compliance_rate": round(resolution_compliance_rate, 2)
        },
        "priority_breach_breakdown": priority_breach_breakdown,
        "overall_compliance_rate": round((contact_compliance_rate + resolution_compliance_rate) / 2, 2)
    }


@router.get("/portfolio/analysis")
async def get_portfolio_analysis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive portfolio analysis"""
    
    # Total portfolio value
    total_portfolio_value = db.query(func.sum(Case.original_amount)).scalar() or 0
    current_portfolio_value = db.query(func.sum(Case.current_amount)).scalar() or 0
    recovered_value = total_portfolio_value - current_portfolio_value
    
    # Cases by priority
    priority_breakdown = db.query(
        Case.priority,
        func.count(Case.id).label('count'),
        func.sum(Case.original_amount).label('amount')
    ).group_by(Case.priority).all()
    
    priority_data = {}
    for priority, count, amount in priority_breakdown:
        priority_data[priority] = {
            "count": count,
            "amount": float(amount or 0),
            "percentage": round(count / db.query(func.count(Case.id)).scalar() * 100, 2)
        }
    
    # Cases by recovery score band
    recovery_bands = db.query(
        Case.recovery_score_band,
        func.count(Case.id).label('count'),
        func.sum(Case.original_amount).label('amount'),
        func.avg(Case.recovery_score).label('avg_score')
    ).group_by(Case.recovery_score_band).all()
    
    recovery_band_data = {}
    for band, count, amount, avg_score in recovery_bands:
        recovery_band_data[band] = {
            "count": count,
            "amount": float(amount or 0),
            "avg_recovery_score": round(float(avg_score or 0), 2)
        }
    
    # Age distribution
    age_ranges = [
        ("0-30 days", 0, 30),
        ("31-60 days", 31, 60),
        ("61-90 days", 61, 90),
        ("91-180 days", 91, 180),
        ("180+ days", 181, 9999)
    ]
    
    age_distribution = {}
    for label, min_days, max_days in age_ranges:
        if max_days == 9999:
            count = db.query(func.count(Case.id)).filter(Case.days_delinquent >= min_days).scalar() or 0
            amount = db.query(func.sum(Case.original_amount)).filter(Case.days_delinquent >= min_days).scalar() or 0
        else:
            count = db.query(func.count(Case.id)).filter(
                and_(Case.days_delinquent >= min_days, Case.days_delinquent <= max_days)
            ).scalar() or 0
            amount = db.query(func.sum(Case.original_amount)).filter(
                and_(Case.days_delinquent >= min_days, Case.days_delinquent <= max_days)
            ).scalar() or 0
        
        age_distribution[label] = {
            "count": count,
            "amount": float(amount or 0)
        }
    
    # DCA allocation summary
    dca_allocation = db.query(
        DCA.name,
        DCA.code,
        func.count(Case.id).label('cases_assigned'),
        func.sum(Case.original_amount).label('amount_assigned')
    ).join(Case, DCA.id == Case.dca_id).group_by(DCA.id, DCA.name, DCA.code).all()
    
    dca_data = []
    for name, code, cases, amount in dca_allocation:
        dca_data.append({
            "dca_name": name,
            "dca_code": code,
            "cases_assigned": cases,
            "amount_assigned": float(amount or 0)
        })
    
    # Unallocated cases
    unallocated_cases = db.query(func.count(Case.id)).filter(Case.dca_id.is_(None)).scalar() or 0
    unallocated_amount = db.query(func.sum(Case.original_amount)).filter(Case.dca_id.is_(None)).scalar() or 0
    
    return {
        "portfolio_summary": {
            "total_cases": db.query(func.count(Case.id)).scalar() or 0,
            "total_portfolio_value": round(total_portfolio_value, 2),
            "current_portfolio_value": round(current_portfolio_value, 2),
            "recovered_value": round(recovered_value, 2),
            "recovery_rate": round((recovered_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0, 2)
        },
        "priority_breakdown": priority_data,
        "recovery_band_breakdown": recovery_band_data,
        "age_distribution": age_distribution,
        "dca_allocation": dca_data,
        "unallocated": {
            "cases": unallocated_cases,
            "amount": float(unallocated_amount or 0)
        },
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/export/cases")
async def export_cases_report(
    format: str = Query("json", description="Export format: json, csv"),
    status: Optional[str] = Query(None, description="Filter by status"),
    dca_id: Optional[str] = Query(None, description="Filter by DCA"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin", "collection_manager"]))
):
    """Export cases report in specified format"""
    
    # Build query with filters
    query = db.query(Case)
    
    if status:
        query = query.filter(Case.status == status)
    
    if dca_id:
        query = query.filter(Case.dca_id == dca_id)
    
    if date_from:
        query = query.filter(Case.created_at >= date_from)
    
    if date_to:
        query = query.filter(Case.created_at <= date_to)
    
    cases = query.all()
    
    # Prepare export data
    export_data = []
    for case in cases:
        dca_name = ""
        if case.dca_id:
            dca = db.query(DCA).filter(DCA.id == case.dca_id).first()
            dca_name = dca.name if dca else ""
        
        export_data.append({
            "case_id": case.id,
            "account_id": case.account_id,
            "debtor_name": case.debtor_name,
            "debtor_email": case.debtor_email,
            "debtor_phone": case.debtor_phone,
            "original_amount": case.original_amount,
            "current_amount": case.current_amount,
            "days_delinquent": case.days_delinquent,
            "status": case.status,
            "priority": case.priority,
            "recovery_score": case.recovery_score,
            "dca_name": dca_name,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "allocation_date": case.allocation_date.isoformat() if case.allocation_date else None,
            "resolved_date": case.resolved_date.isoformat() if case.resolved_date else None
        })
    
    if format.lower() == "csv":
        # For CSV format, return structured data that frontend can convert
        return {
            "format": "csv",
            "filename": f"cases_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
            "data": export_data,
            "total_records": len(export_data)
        }
    
    # Default JSON format
    return {
        "format": "json",
        "filename": f"cases_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        "data": export_data,
        "total_records": len(export_data),
        "export_metadata": {
            "exported_by": current_user["email"],
            "exported_at": datetime.utcnow().isoformat(),
            "filters_applied": {
                "status": status,
                "dca_id": dca_id,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None
            }
        }
    }


# ============================================================
# DASHBOARD ENDPOINTS — Real data for frontend charts & KPIs
# ============================================================

@router.get("/dashboard/kpis")
async def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get KPI cards data for dashboard overview"""

    # Total cases
    total_cases = db.query(func.count(Case.id)).scalar() or 0

    # Active cases (not resolved or closed)
    active_cases = db.query(func.count(Case.id)).filter(
        Case.status.notin_([CaseStatus.RESOLVED, "closed"])
    ).scalar() or 0

    # Total amounts
    total_outstanding = db.query(func.sum(Case.current_amount)).scalar() or 0
    total_original = db.query(func.sum(Case.original_amount)).scalar() or 0
    recovered_amount = total_original - total_outstanding

    # Recovery rate
    recovery_rate = (recovered_amount / total_original * 100) if total_original > 0 else 0

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

    # High priority count
    high_priority = db.query(func.count(Case.id)).filter(
        Case.priority == CasePriority.HIGH
    ).scalar() or 0

    # Cases this month vs last month for change %
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if month_start.month == 1:
        last_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        last_month_start = month_start.replace(month=month_start.month - 1)

    cases_this_month = db.query(func.count(Case.id)).filter(
        Case.created_at >= month_start
    ).scalar() or 0
    cases_last_month = db.query(func.count(Case.id)).filter(
        and_(Case.created_at >= last_month_start, Case.created_at < month_start)
    ).scalar() or 0

    cases_change = ((cases_this_month - cases_last_month) / max(cases_last_month, 1)) * 100

    return {
        "total_cases": total_cases,
        "active_cases": active_cases,
        "total_outstanding": round(total_outstanding, 2),
        "total_original": round(total_original, 2),
        "recovered_amount": round(recovered_amount, 2),
        "recovery_rate": round(recovery_rate, 1),
        "active_dcas": active_dcas,
        "sla_breaches": sla_breaches,
        "high_priority_cases": high_priority,
        "cases_this_month": cases_this_month,
        "cases_change_pct": round(cases_change, 1),
        "last_updated": now.isoformat()
    }


@router.get("/dashboard/recovery-chart")
async def get_dashboard_recovery_chart(
    months: int = Query(10, description="Number of months of data"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get monthly recovery data for line/area charts"""

    now = datetime.utcnow()
    start_date = now - timedelta(days=months * 30)

    # Monthly recovery data from resolved cases
    recovery_by_month = db.query(
        func.strftime('%Y-%m', Case.resolved_date).label('month'),
        func.sum(Case.original_amount - Case.current_amount).label('recovered'),
        func.count(Case.id).label('cases_resolved')
    ).filter(
        Case.resolved_date >= start_date,
        Case.status == CaseStatus.RESOLVED
    ).group_by(func.strftime('%Y-%m', Case.resolved_date)).order_by(
        func.strftime('%Y-%m', Case.resolved_date)
    ).all()

    # Monthly case creation data
    creation_by_month = db.query(
        func.strftime('%Y-%m', Case.created_at).label('month'),
        func.sum(Case.original_amount).label('amount_created'),
        func.count(Case.id).label('cases_created')
    ).filter(
        Case.created_at >= start_date
    ).group_by(func.strftime('%Y-%m', Case.created_at)).order_by(
        func.strftime('%Y-%m', Case.created_at)
    ).all()

    # Build combined data
    recovery_dict = {r.month: {"recovered": float(r.recovered or 0), "cases_resolved": r.cases_resolved} for r in recovery_by_month}
    creation_dict = {c.month: {"amount_created": float(c.amount_created or 0), "cases_created": c.cases_created} for c in creation_by_month}

    all_months = sorted(set(recovery_dict.keys()) | set(creation_dict.keys()))

    # Map month strings to short names
    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    chart_data = []
    for m in all_months:
        month_num = m.split('-')[1] if '-' in m else m
        short_name = month_names.get(month_num, m)
        rec = recovery_dict.get(m, {"recovered": 0, "cases_resolved": 0})
        cre = creation_dict.get(m, {"amount_created": 0, "cases_created": 0})

        chart_data.append({
            "name": short_name,
            "month_key": m,
            "recovery": round(rec["recovered"], 2),
            "cases_resolved": rec["cases_resolved"],
            "amount_created": round(cre["amount_created"], 2),
            "cases_created": cre["cases_created"],
        })

    # Generate simple forecast for next 3 months
    forecast_data = []
    if chart_data:
        recent = chart_data[-3:] if len(chart_data) >= 3 else chart_data
        avg_recovery = sum(d["recovery"] for d in recent) / len(recent)
        growth_factor = 1.1  # 10% growth assumption

        for i in range(1, 4):
            future_month_num = (now.month + i - 1) % 12 + 1
            future_name = month_names.get(f'{future_month_num:02d}', f'M+{i}')
            forecasted = round(avg_recovery * (growth_factor ** i), 2)
            forecast_data.append({
                "name": future_name,
                "forecast": forecasted,
                "recovery": None,
            })

    return {
        "chart_data": chart_data,
        "forecast_data": forecast_data,
        "total_months": len(chart_data),
    }


@router.get("/dashboard/top-dcas")
async def get_dashboard_top_dcas(
    limit: int = Query(5, description="Number of top DCAs"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get top performing DCAs for dashboard sidebar"""

    dcas = db.query(DCA).filter(DCA.is_active == True).order_by(
        DCA.performance_score.desc()
    ).limit(limit).all()

    top_dcas = []
    for dca in dcas:
        # Get case stats for this DCA
        total_assigned = db.query(func.count(Case.id)).filter(
            Case.dca_id == dca.id
        ).scalar() or 0

        resolved = db.query(func.count(Case.id)).filter(
            Case.dca_id == dca.id,
            Case.status == CaseStatus.RESOLVED
        ).scalar() or 0

        amount_assigned = db.query(func.sum(Case.original_amount)).filter(
            Case.dca_id == dca.id
        ).scalar() or 0

        amount_recovered = db.query(
            func.sum(Case.original_amount - Case.current_amount)
        ).filter(
            Case.dca_id == dca.id,
            Case.status == CaseStatus.RESOLVED
        ).scalar() or 0

        recovery_pct = round((amount_recovered / amount_assigned * 100) if amount_assigned > 0 else 0, 1)

        top_dcas.append({
            "id": dca.id,
            "name": dca.name,
            "code": dca.code,
            "performance_score": round((dca.performance_score or 0) * 100, 0),
            "recovery_rate": round(dca.recovery_rate or 0, 1),
            "sla_compliance": round((dca.sla_compliance_rate or 0) * 100, 0),
            "total_assigned": total_assigned,
            "resolved": resolved,
            "actual_recovery_pct": recovery_pct,
        })

    return {"top_dcas": top_dcas}


@router.get("/dashboard/reports-data")
async def get_dashboard_reports_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive data for the Reports page charts"""

    now = datetime.utcnow()
    six_months_ago = now - timedelta(days=180)

    # --- Recovery by DCA (for bar chart comparison) ---
    dcas = db.query(DCA).filter(DCA.is_active == True).limit(5).all()
    recovery_by_dca = {}

    for dca in dcas:
        monthly = db.query(
            func.strftime('%Y-%m', Case.resolved_date).label('month'),
            func.sum(Case.original_amount - Case.current_amount).label('recovered')
        ).filter(
            Case.dca_id == dca.id,
            Case.resolved_date >= six_months_ago,
            Case.status == CaseStatus.RESOLVED
        ).group_by(func.strftime('%Y-%m', Case.resolved_date)).order_by(
            func.strftime('%Y-%m', Case.resolved_date)
        ).all()

        for row in monthly:
            if row.month not in recovery_by_dca:
                recovery_by_dca[row.month] = {"month": row.month}
            recovery_by_dca[row.month][dca.code] = round(float(row.recovered or 0), 2)

    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    recovery_comparison = []
    for m in sorted(recovery_by_dca.keys()):
        entry = recovery_by_dca[m]
        month_num = m.split('-')[1]
        entry["month"] = month_names.get(month_num, m)
        recovery_comparison.append(entry)

    dca_keys = [{"key": dca.code, "name": dca.name} for dca in dcas]

    # --- SLA Compliance Trends ---
    sla_trends = []
    for i in range(6):
        month_offset = 5 - i
        m_start = (now - timedelta(days=month_offset * 30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_offset == 0:
            m_end = now
        else:
            m_end = (now - timedelta(days=(month_offset - 1) * 30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_with_sla = db.query(func.count(Case.id)).filter(
            Case.created_at >= m_start,
            Case.created_at < m_end,
            Case.sla_resolution_deadline.isnot(None)
        ).scalar() or 0

        compliant = db.query(func.count(Case.id)).filter(
            Case.created_at >= m_start,
            Case.created_at < m_end,
            Case.resolved_date <= Case.sla_resolution_deadline
        ).scalar() or 0

        compliant_pct = round((compliant / total_with_sla * 100) if total_with_sla > 0 else 95, 1)
        breached_pct = round(100 - compliant_pct, 1)

        month_num = f'{m_start.month:02d}'
        sla_trends.append({
            "month": month_names.get(month_num, str(m_start.month)),
            "compliant": compliant_pct,
            "breached": breached_pct,
        })

    # --- Ageing Distribution ---
    age_buckets = [
        {"bucket": "0-30", "min": 0, "max": 30},
        {"bucket": "31-60", "min": 31, "max": 60},
        {"bucket": "61-90", "min": 61, "max": 90},
        {"bucket": "90+", "min": 91, "max": 99999},
    ]

    ageing_data = []
    for bucket in age_buckets:
        if bucket["max"] == 99999:
            count = db.query(func.count(Case.id)).filter(
                Case.days_delinquent >= bucket["min"]
            ).scalar() or 0
            amount = db.query(func.sum(Case.original_amount)).filter(
                Case.days_delinquent >= bucket["min"]
            ).scalar() or 0
        else:
            count = db.query(func.count(Case.id)).filter(
                and_(Case.days_delinquent >= bucket["min"], Case.days_delinquent <= bucket["max"])
            ).scalar() or 0
            amount = db.query(func.sum(Case.original_amount)).filter(
                and_(Case.days_delinquent >= bucket["min"], Case.days_delinquent <= bucket["max"])
            ).scalar() or 0

        ageing_data.append({
# TODO: implement edge case handling
