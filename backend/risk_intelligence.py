"""
SchemaLock Risk Intelligence & Blast Radius Engine.

Provides deterministic, explainable operational risk breakdown into 4 categories:
1. Data Loss Risk
2. Locking Risk
3. Compatibility Risk
4. Performance Risk

Also calculates Blast Radius metrics (destructive operations, affected operations, application compatibility).
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class CategoryRisk(BaseModel):
    level: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    score: int = Field(ge=0, le=100)
    reasons: List[str]


class BlastRadius(BaseModel):
    level: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    destructive_operations: int
    affected_operations: int
    application_compatibility: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"


class RiskIntelligence(BaseModel):
    data_loss_risk: CategoryRisk
    locking_risk: CategoryRisk
    compatibility_risk: CategoryRisk
    performance_risk: CategoryRisk
    blast_radius: BlastRadius


SEVERITY_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

RULE_CATEGORY_MAPPINGS = {
    "DROP_TABLE": {
        "data_loss": ("CRITICAL", 95, "Potential permanent deletion of entire table and all data rows"),
        "locking": ("HIGH", 75, "Requires AccessExclusiveLock blocking all table access"),
        "compatibility": ("CRITICAL", 90, "Potential application breakage for queries referencing table"),
        "performance": ("MEDIUM", 40, "Invalidates cached plans and metadata"),
        "is_destructive": True
    },
    "TRUNCATE_TABLE": {
        "data_loss": ("CRITICAL", 95, "Potential immediate deletion of all table rows"),
        "locking": ("HIGH", 80, "Requires AccessExclusiveLock on target table"),
        "compatibility": ("HIGH", 75, "Empties data required by active application routines"),
        "performance": ("HIGH", 70, "Flushes table storage pages and index structures"),
        "is_destructive": True
    },
    "DROP_COLUMN": {
        "data_loss": ("HIGH", 75, "Potential permanent removal of column data"),
        "locking": ("MEDIUM", 50, "Requires brief AccessExclusiveLock for catalog change"),
        "compatibility": ("HIGH", 80, "Potential application breakage for code expecting column"),
        "performance": ("LOW", 10, "Minimal direct query performance impact"),
        "is_destructive": True
    },
    "ADD_COLUMN_NOT_NULL": {
        "data_loss": ("LOW", 0, "No data deletion risk"),
        "locking": ("HIGH", 80, "Potential AccessExclusiveLock during row validation/rewrite"),
        "compatibility": ("HIGH", 75, "Fails migration on existing rows if no default provided"),
        "performance": ("MEDIUM", 50, "Potential table scan for existing row validation"),
        "is_destructive": False
    },
    "ALTER_COLUMN_TYPE": {
        "data_loss": ("MEDIUM", 40, "Potential data truncation or type cast failure"),
        "locking": ("HIGH", 85, "Full table rewrite holding AccessExclusiveLock"),
        "compatibility": ("HIGH", 80, "Potential application type mismatch errors"),
        "performance": ("HIGH", 75, "Full table scan and complete index rebuild"),
        "is_destructive": False
    },
    "ADD_UNIQUE_CONSTRAINT": {
        "data_loss": ("LOW", 0, "No data deletion risk"),
        "locking": ("MEDIUM", 50, "Requires exclusive lock during constraint validation"),
        "compatibility": ("MEDIUM", 40, "Migration fails if duplicate values exist in data"),
        "performance": ("MEDIUM", 50, "Scans table rows for unique index validation"),
        "is_destructive": False
    },
    "CREATE_INDEX": {
        "data_loss": ("LOW", 0, "No data deletion risk"),
        "locking": ("MEDIUM", 50, "Acquires SHARE lock blocking concurrent WRITE operations"),
        "compatibility": ("LOW", 10, "Transparent to application code"),
        "performance": ("MEDIUM", 50, "CPU & disk I/O load during index construction"),
        "is_destructive": False
    },
    "CREATE_INDEX_CONCURRENT": {
        "data_loss": ("LOW", 0, "No data deletion risk"),
        "locking": ("LOW", 10, "Non-blocking concurrent build avoids WRITE locks"),
        "compatibility": ("LOW", 0, "Transparent to application code"),
        "performance": ("MEDIUM", 40, "Extra CPU/IO background load during build iterations"),
        "is_destructive": False
    }
}


def calculate_risk_intelligence(findings: List[Any]) -> RiskIntelligence:
    """Calculate Category Risks and Blast Radius deterministically from AST findings."""
    rule_ids = [getattr(f, "rule_id", f.get("rule_id") if isinstance(f, dict) else "") for f in findings]
    
    categories = {
        "data_loss": {"level": "LOW", "score": 0, "reasons": []},
        "locking": {"level": "LOW", "score": 0, "reasons": []},
        "compatibility": {"level": "LOW", "score": 0, "reasons": []},
        "performance": {"level": "LOW", "score": 0, "reasons": []}
    }
    
    destructive_count = 0
    
    for rule_id in rule_ids:
        mapping = RULE_CATEGORY_MAPPINGS.get(rule_id)
        if not mapping:
            continue
            
        if mapping.get("is_destructive"):
            destructive_count += 1
            
        for cat in ["data_loss", "locking", "compatibility", "performance"]:
            lvl, score, reason = mapping[cat]
            current = categories[cat]
            
            # Highest level precedence
            if SEVERITY_ORDER[lvl] > SEVERITY_ORDER[current["level"]]:
                current["level"] = lvl
                
            # Highest score precedence
            if score > current["score"]:
                current["score"] = score
                
            if reason and reason not in current["reasons"]:
                current["reasons"].append(reason)

    # Handle empty/safe default reasons
    for cat, data in categories.items():
        if not data["reasons"]:
            data["reasons"] = ["No elevated risk detected for this dimension"]

    # Calculate Blast Radius Level
    affected_ops = len(findings)
    
    if destructive_count >= 2 or categories["data_loss"]["level"] == "CRITICAL":
        blast_level = "CRITICAL"
    elif destructive_count == 1 or categories["locking"]["level"] in ("HIGH", "CRITICAL") or categories["compatibility"]["level"] in ("HIGH", "CRITICAL"):
        blast_level = "HIGH"
    elif any(categories[cat]["level"] == "MEDIUM" for cat in categories):
        blast_level = "MEDIUM"
    else:
        blast_level = "LOW"

    blast_radius = BlastRadius(
        level=blast_level,
        destructive_operations=destructive_count,
        affected_operations=affected_ops,
        application_compatibility=categories["compatibility"]["level"]
    )

    return RiskIntelligence(
        data_loss_risk=CategoryRisk(**categories["data_loss"]),
        locking_risk=CategoryRisk(**categories["locking"]),
        compatibility_risk=CategoryRisk(**categories["compatibility"]),
        performance_risk=CategoryRisk(**categories["performance"]),
        blast_radius=blast_radius
    )
