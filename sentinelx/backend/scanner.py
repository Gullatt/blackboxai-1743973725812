from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import ScanResult, SessionLocal
import json
import requests
from typing import Optional
from datetime import datetime

def perform_scan(target: str, user_id: Optional[int] = None):
    """
    Perform a security scan on the target (URL or IP)
    Returns a dictionary with scan results
    """
    if not target.startswith(('http://', 'https://')):
        target = f"http://{target}"
    
    try:
        response = requests.get(target, timeout=5, verify=False)
        response.raise_for_status()
    except requests.RequestException:
        raise HTTPException(status_code=400, detail="Could not connect to target")
    
    # Mock scan results
    findings = [
        {
            "id": "1",
            "title": "Outdated Software",
            "severity": "high",
            "description": "The target is running outdated software with known vulnerabilities.",
            "recommendation": "Update to the latest version immediately."
        },
        {
            "id": "2",
            "title": "Weak SSL/TLS Configuration",
            "severity": "medium",
            "description": "The server supports weak encryption protocols.",
            "recommendation": "Disable support for TLS 1.0 and 1.1, and use strong cipher suites."
        }
    ]
    
    if user_id:
        db = SessionLocal()
        try:
            scan_result = ScanResult(
                user_id=user_id,
                target=target,
                findings=json.dumps(findings)
            )
            db.add(scan_result)
            db.commit()
        finally:
            db.close()
    
    return {"target": target, "findings": findings}

def fix_issue(issue_id: str, target: str, user_id: Optional[int] = None):
    db = SessionLocal()
    try:
        if user_id:
            scan_result = db.query(ScanResult)\
                .filter(ScanResult.user_id == user_id)\
                .filter(ScanResult.target == target)\
                .order_by(ScanResult.created_at.desc())\
                .first()
            
            if scan_result:
                scan_result.fixed_at = datetime.utcnow()
                db.commit()
    finally:
        db.close()
    
    return {
        "message": f"Issue {issue_id} fixed successfully",
        "target": target
    }