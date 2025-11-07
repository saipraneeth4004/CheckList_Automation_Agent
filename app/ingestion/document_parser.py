"""
Document parser for extracting and analyzing content from files
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import re


class DocumentParser:
    """Parses documents and extracts relevant accounting information"""
    
    def __init__(self):
        self.accounting_patterns = {
            "balance": r"balance|bal\b",
            "debit": r"debit|dr\b|^debit",
            "credit": r"credit|cr\b|^credit",
            "total": r"total|sum\b",
            "account": r"account|acct",
            "amount": r"amount|value",
            "date": r"date|period",
            "description": r"description|desc|narration",
            "customer": r"customer|client",
            "vendor": r"vendor|supplier",
            "aging": r"aging|age|overdue",
            "current": r"current|0-30",
            "reconciliation": r"reconcil|recon"
        }
        
        self.compiled_patterns = {
            key: re.compile(pattern, re.IGNORECASE)
            for key, pattern in self.accounting_patterns.items()
        }
    
    def parse_excel_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse an Excel sheet and extract structured information"""
        if df.empty:
            return {
                "success": False,
                "error": "Empty dataframe"
            }
        
        result = {
            "success": True,
            "rows": len(df),
            "columns": len(df.columns),
            "detected_fields": {},
            "has_headers": True,
            "numeric_columns": [],
            "date_columns": [],
            "summary": {}
        }
        
        # Detect field types from column names
        for col in df.columns:
            col_str = str(col).lower()
            for field_type, pattern in self.compiled_patterns.items():
                if pattern.search(col_str):
                    if field_type not in result["detected_fields"]:
                        result["detected_fields"][field_type] = []
                    result["detected_fields"][field_type].append(col)
        
        # Identify numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        result["numeric_columns"] = numeric_cols
        
        # Try to detect date columns
        for col in df.columns:
            try:
                pd.to_datetime(df[col], errors='raise')
                result["date_columns"].append(col)
            except:
                pass
        
        # Check for common accounting structures
        result["summary"] = {
            "has_debit_credit": ("debit" in result["detected_fields"] and 
                                 "credit" in result["detected_fields"]),
            "has_amounts": "amount" in result["detected_fields"],
            "has_balances": "balance" in result["detected_fields"],
            "has_totals": any("total" in str(col).lower() for col in df.columns),
            "numeric_column_count": len(numeric_cols)
        }
        
        return result
    
    def validate_bank_reconciliation(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate bank reconciliation file"""
        validation = {
            "valid": False,
            "checks": {},
            "issues": []
        }
        
        if file_data.get("file_type") == "excel":
            sheets = file_data.get("sheets", {})
            
            for sheet_name, sheet_data in sheets.items():
                df = sheet_data.get("data")
                if df is None or df.empty:
                    continue
                
                parsed = self.parse_excel_sheet(df)
                
                # Check for reconciliation keywords
                validation["checks"]["has_balance"] = "balance" in parsed["detected_fields"]
                validation["checks"]["has_reconciliation_keywords"] = bool(
                    parsed["detected_fields"])
                validation["checks"]["has_numeric_data"] = len(
                    parsed["numeric_columns"]) > 0
                
                # Look for reconciliation structure
                content_str = df.to_string().lower()
                validation["checks"]["mentions_reconciliation"] = "reconcil" in content_str
                validation["checks"]["mentions_outstanding"] = "outstanding" in content_str
                
                if sum(validation["checks"].values()) >= 3:
                    validation["valid"] = True
                    break
        
        if not validation["valid"]:
            validation["issues"].append("Missing reconciliation structure or keywords")
        
        return validation
    
    def validate_aging_report(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AR/AP aging report"""
        validation = {
            "valid": False,
            "checks": {},
            "issues": []
        }
        
        if file_data.get("file_type") == "excel":
            sheets = file_data.get("sheets", {})
            
            for sheet_name, sheet_data in sheets.items():
                df = sheet_data.get("data")
                if df is None or df.empty:
                    continue
                
                parsed = self.parse_excel_sheet(df)
                
                # Check for aging buckets
                content_str = " ".join([str(col) for col in df.columns]).lower()
                
                validation["checks"]["has_current"] = "current" in content_str or "0-30" in content_str
                validation["checks"]["has_30_days"] = "30" in content_str
                validation["checks"]["has_60_days"] = "60" in content_str
                validation["checks"]["has_90_days"] = "90" in content_str
                validation["checks"]["has_total"] = any("total" in str(col).lower() 
                                                         for col in df.columns)
                validation["checks"]["has_numeric_data"] = len(
                    parsed["numeric_columns"]) >= 3
                
                if sum(validation["checks"].values()) >= 4:
                    validation["valid"] = True
                    break
        
        if not validation["valid"]:
            validation["issues"].append("Missing aging buckets (Current, 30, 60, 90 days)")
        
        return validation
    
    def validate_journal_entries(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate journal entry file"""
        validation = {
            "valid": False,
            "checks": {},
            "issues": [],
            "balanced": False
        }
        
        if file_data.get("file_type") == "excel":
            sheets = file_data.get("sheets", {})
            
            for sheet_name, sheet_data in sheets.items():
                df = sheet_data.get("data")
                if df is None or df.empty:
                    continue
                
                parsed = self.parse_excel_sheet(df)
                
                validation["checks"]["has_debit_credit"] = parsed["summary"]["has_debit_credit"]
                validation["checks"]["has_account"] = "account" in parsed["detected_fields"]
                validation["checks"]["has_description"] = "description" in parsed["detected_fields"]
                
                # Try to check if debits = credits
                if parsed["summary"]["has_debit_credit"]:
                    debit_cols = parsed["detected_fields"].get("debit", [])
                    credit_cols = parsed["detected_fields"].get("credit", [])
                    
                    if debit_cols and credit_cols:
                        try:
                            total_debits = df[debit_cols[0]].sum()
                            total_credits = df[credit_cols[0]].sum()
                            
                            if abs(total_debits - total_credits) < 0.01:
                                validation["balanced"] = True
                                validation["checks"]["balanced"] = True
                        except:
                            pass
                
                if sum(validation["checks"].values()) >= 2:
                    validation["valid"] = True
                    break
        
        if not validation["valid"]:
            validation["issues"].append("Missing required fields (debit, credit, account)")
        
        if validation["valid"] and not validation["balanced"]:
            validation["issues"].append("Journal entries may not be balanced")
        
        return validation
    
    def validate_gl_extract(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate general ledger extract"""
        validation = {
            "valid": False,
            "checks": {},
            "issues": []
        }
        
        if file_data.get("file_type") == "excel":
            sheets = file_data.get("sheets", {})
            
            for sheet_name, sheet_data in sheets.items():
                df = sheet_data.get("data")
                if df is None or df.empty:
                    continue
                
                parsed = self.parse_excel_sheet(df)
                
                validation["checks"]["has_account"] = "account" in parsed["detected_fields"]
                validation["checks"]["has_debit_credit"] = parsed["summary"]["has_debit_credit"]
                validation["checks"]["has_balance"] = "balance" in parsed["detected_fields"]
                validation["checks"]["has_numeric_data"] = len(
                    parsed["numeric_columns"]) >= 2
                
                if sum(validation["checks"].values()) >= 3:
                    validation["valid"] = True
                    break
        
        if not validation["valid"]:
            validation["issues"].append("Missing GL structure (account, debit, credit, balance)")
        
        return validation
    
    def extract_amounts(self, df: pd.DataFrame) -> List[float]:
        """Extract numeric amounts from dataframe"""
        amounts = []
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            values = df[col].dropna()
            amounts.extend(values.tolist())
        
        return amounts
    
    def find_totals(self, df: pd.DataFrame) -> Dict[str, float]:
        """Find total rows/values in dataframe"""
        totals = {}
        
        # Look for rows with "total" in them
        for idx, row in df.iterrows():
            row_str = " ".join([str(val).lower() for val in row.values])
            if "total" in row_str:
                # Extract numeric values from this row
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        totals[f"total_{col}"] = row[col]
        
        return totals
