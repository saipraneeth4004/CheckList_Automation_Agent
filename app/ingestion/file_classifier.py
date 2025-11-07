"""
File classifier to automatically detect and categorize uploaded files
"""

from pathlib import Path
from typing import Dict, Optional
import re


class FileClassifier:
    """Classifies files based on name patterns and content"""
    
    # Keyword patterns for each checklist category
    CLASSIFICATION_PATTERNS = {
        "bank_reconciliation": [
            r"bank.*recon",
            r"reconciliation",
            r"bank.*statement",
            r"cash.*book",
            r"recon"
        ],
        "ar_aging": [
            r"ar.*aging",
            r"receivable.*aging",
            r"ar.*report",
            r"receivables",
            r"customer.*aging",
            r"debtors"
        ],
        "ap_aging": [
            r"ap.*aging",
            r"payable.*aging",
            r"ap.*report",
            r"payables",
            r"vendor.*aging",
            r"supplier.*aging",
            r"creditors"
        ],
        "accruals": [
            r"accrual",
            r"journal.*entr",
            r"je\b",
            r"adjusting.*entr",
            r"provision"
        ],
        "gl_extract": [
            r"gl.*extract",
            r"general.*ledger",
            r"trial.*balance",
            r"\btb\b",
            r"ledger"
        ],
        "prepayments": [
            r"prepayment",
            r"prepaid",
            r"deferred",
            r"amortization"
        ],
        "fixed_assets": [
            r"fixed.*asset",
            r"asset.*register",
            r"depreciation",
            r"capex",
            r"\bppe\b",
            r"plant.*equipment"
        ],
        "intercompany_recon": [
            r"intercompany",
            r"ic.*recon",
            r"interco",
            r"related.*party"
        ],
        "revenue_recognition": [
            r"revenue",
            r"sales",
            r"income",
            r"revenue.*schedule"
        ],
        "expense_analysis": [
            r"expense",
            r"cost.*analys",
            r"opex",
            r"variance",
            r"budget.*actual"
        ]
    }
    
    def __init__(self):
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.CLASSIFICATION_PATTERNS.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def classify_file(self, filename: str) -> Dict[str, any]:
        """
        Classify a file based on its name
        
        Returns:
            dict with classification results including category and confidence
        """
        filename_lower = filename.lower()
        stem = Path(filename).stem.lower()  # filename without extension
        
        scores = {}
        
        # Check each category
        for category, patterns in self.compiled_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                if pattern.search(stem):
                    score += 1
                    matched_patterns.append(pattern.pattern)
            
            if score > 0:
                scores[category] = {
                    "score": score,
                    "matched_patterns": matched_patterns
                }
        
        # Determine best match
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1]["score"])
            confidence = min(best_category[1]["score"] * 0.3, 1.0)  # Cap at 1.0
            
            return {
                "category": best_category[0],
                "confidence": confidence,
                "matched_patterns": best_category[1]["matched_patterns"],
                "all_scores": scores
            }
        
        return {
            "category": "unknown",
            "confidence": 0.0,
            "matched_patterns": [],
            "all_scores": {}
        }
    
    def classify_multiple_files(self, filenames: list) -> Dict[str, list]:
        """
        Classify multiple files and group by category
        
        Returns:
            dict mapping category to list of files
        """
        categorized = {}
        
        for filename in filenames:
            result = self.classify_file(filename)
            category = result["category"]
            
            if category not in categorized:
                categorized[category] = []
            
            categorized[category].append({
                "filename": filename,
                "confidence": result["confidence"],
                "matched_patterns": result["matched_patterns"]
            })
        
        return categorized
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        return Path(filename).suffix.lower()
    
    def is_supported_extension(self, filename: str, allowed_extensions: list) -> bool:
        """Check if file extension is supported"""
        ext = self.get_file_extension(filename)
        return ext in allowed_extensions
    
    def suggest_category(self, filename: str, threshold: float = 0.3) -> Optional[str]:
        """
        Suggest a category if confidence is above threshold
        
        Returns:
            category name or None
        """
        result = self.classify_file(filename)
        if result["confidence"] >= threshold and result["category"] != "unknown":
            return result["category"]
        return None
