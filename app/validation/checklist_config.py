"""
Checklist configuration defining all month-end close tasks and validation rules
"""

from typing import List, Dict, Any
from enum import Enum


class ChecklistStatus(str, Enum):
    """Status of checklist items"""
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    MISSING = "missing"
    PARTIAL = "partial"


class ChecklistItem:
    """Represents a single checklist item with validation rules"""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        required_files: List[str],
        optional_files: List[str] = None,
        required_content: List[str] = None,
        priority: int = 1
    ):
        self.id = id
        self.name = name
        self.description = description
        self.required_files = required_files
        self.optional_files = optional_files or []
        self.required_content = required_content or []
        self.priority = priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required_files": self.required_files,
            "optional_files": self.optional_files,
            "required_content": self.required_content,
            "priority": self.priority
        }


# Define the standard month-end checklist
MONTH_END_CHECKLIST = [
    ChecklistItem(
        id="bank_reconciliation",
        name="Bank Reconciliation",
        description="Reconciliation of bank statements with cash book entries",
        required_files=["bank_reconciliation", "bank_recon", "reconciliation"],
        optional_files=["bank_statement", "cash_book"],
        required_content=["balance", "reconciliation", "outstanding", "deposits"],
        priority=1
    ),
    ChecklistItem(
        id="ar_aging",
        name="Accounts Receivable Aging",
        description="Aging report for accounts receivable",
        required_files=["ar_aging", "receivable_aging", "ar_report", "receivables"],
        optional_files=["customer_aging"],
        required_content=["current", "30", "60", "90", "total", "customer"],
        priority=1
    ),
    ChecklistItem(
        id="ap_aging",
        name="Accounts Payable Aging",
        description="Aging report for accounts payable",
        required_files=["ap_aging", "payable_aging", "ap_report", "payables"],
        optional_files=["vendor_aging", "supplier_aging"],
        required_content=["current", "30", "60", "90", "total", "vendor", "supplier"],
        priority=1
    ),
    ChecklistItem(
        id="accruals",
        name="Accrual Entries",
        description="Journal entries for accrued expenses and revenues",
        required_files=["accrual", "accruals", "journal_entries", "je"],
        optional_files=["adjusting_entries"],
        required_content=["debit", "credit", "account", "description", "amount"],
        priority=2
    ),
    ChecklistItem(
        id="gl_extract",
        name="General Ledger Extract",
        description="General ledger extract or trial balance",
        required_files=["gl_extract", "general_ledger", "trial_balance", "tb"],
        optional_files=["ledger"],
        required_content=["account", "debit", "credit", "balance"],
        priority=1
    ),
    ChecklistItem(
        id="prepayments",
        name="Prepayments Schedule",
        description="Schedule of prepaid expenses and amortization",
        required_files=["prepayment", "prepaid", "deferred"],
        optional_files=["amortization"],
        required_content=["asset", "amount", "period", "amortization"],
        priority=2
    ),
    ChecklistItem(
        id="fixed_assets",
        name="Fixed Assets Register",
        description="Fixed assets register with depreciation schedule",
        required_files=["fixed_asset", "asset_register", "depreciation"],
        optional_files=["capex", "ppe"],
        required_content=["asset", "cost", "depreciation", "nbv", "net book value"],
        priority=2
    ),
    ChecklistItem(
        id="intercompany_recon",
        name="Intercompany Reconciliation",
        description="Reconciliation of intercompany balances",
        required_files=["intercompany", "ic_recon", "interco"],
        optional_files=["related_party"],
        required_content=["entity", "balance", "reconciliation"],
        priority=2
    ),
    ChecklistItem(
        id="revenue_recognition",
        name="Revenue Recognition",
        description="Revenue recognition schedule and analysis",
        required_files=["revenue", "sales", "income"],
        optional_files=["revenue_schedule"],
        required_content=["revenue", "period", "recognition", "amount"],
        priority=2
    ),
    ChecklistItem(
        id="expense_analysis",
        name="Expense Analysis",
        description="Detailed expense analysis and variance report",
        required_files=["expense", "cost"],
        optional_files=["variance", "budget"],
        required_content=["expense", "category", "amount", "analysis"],
        priority=3
    )
]


def get_checklist() -> List[ChecklistItem]:
    """Get the complete month-end checklist"""
    return MONTH_END_CHECKLIST


def get_checklist_by_id(checklist_id: str) -> ChecklistItem:
    """Get a specific checklist item by ID"""
    for item in MONTH_END_CHECKLIST:
        if item.id == checklist_id:
            return item
    return None


def get_checklist_dict() -> Dict[str, ChecklistItem]:
    """Get checklist as a dictionary keyed by ID"""
    return {item.id: item for item in MONTH_END_CHECKLIST}


def get_high_priority_items() -> List[ChecklistItem]:
    """Get high priority checklist items"""
    return [item for item in MONTH_END_CHECKLIST if item.priority == 1]


def get_checklist_summary() -> Dict[str, Any]:
    """Get summary information about the checklist"""
    return {
        "total_items": len(MONTH_END_CHECKLIST),
        "high_priority": len([i for i in MONTH_END_CHECKLIST if i.priority == 1]),
        "medium_priority": len([i for i in MONTH_END_CHECKLIST if i.priority == 2]),
        "low_priority": len([i for i in MONTH_END_CHECKLIST if i.priority == 3]),
        "items": [item.to_dict() for item in MONTH_END_CHECKLIST]
    }
