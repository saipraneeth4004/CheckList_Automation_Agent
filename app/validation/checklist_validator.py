"""
Checklist validator - main validation engine
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from app.validation.checklist_config import (
    get_checklist, ChecklistItem, ChecklistStatus, get_checklist_by_id
)
from app.ingestion.file_classifier import FileClassifier
from app.ingestion.file_processor import FileProcessor
from app.ingestion.document_parser import DocumentParser


class ChecklistValidator:
    """Main validator for month-end checklist"""
    
    def __init__(self):
        self.checklist = get_checklist()
        self.classifier = FileClassifier()
        self.processor = FileProcessor()
        self.parser = DocumentParser()
    
    def validate_folder(self, folder_path: Path) -> Dict[str, Any]:
        """
        Validate all files in a folder against the checklist
        
        Returns:
            Complete validation report
        """
        if not folder_path.exists() or not folder_path.is_dir():
            return {
                "success": False,
                "error": f"Invalid folder path: {folder_path}"
            }
        
        # Get all files
        all_files = [f for f in folder_path.rglob('*') if f.is_file()]
        file_names = [f.name for f in all_files]
        
        # Classify files
        classified_files = self.classifier.classify_multiple_files(file_names)
        
        # Validate each checklist item
        checklist_results = []
        
        for item in self.checklist:
            result = self._validate_checklist_item(
                item, all_files, classified_files
            )
            checklist_results.append(result)
        
        # Calculate summary statistics
        summary = self._calculate_summary(checklist_results)
        
        return {
            "success": True,
            "folder_path": str(folder_path),
            "total_files": len(all_files),
            "file_names": file_names,
            "classified_files": classified_files,
            "checklist_results": checklist_results,
            "summary": summary
        }
    
    def _validate_checklist_item(
        self, 
        item: ChecklistItem, 
        all_files: List[Path],
        classified_files: Dict[str, List]
    ) -> Dict[str, Any]:
        """Validate a single checklist item"""
        
        result = {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "status": ChecklistStatus.MISSING,
            "matched_files": [],
            "confidence": 0.0,
            "validation_details": {},
            "issues": [],
            "recommendations": []
        }
        
        # Find files that match this category
        category_files = classified_files.get(item.id, [])
        
        if not category_files:
            result["status"] = ChecklistStatus.MISSING
            result["issues"].append(f"No files found for {item.name}")
            result["recommendations"].append(
                f"Upload file with name containing: {', '.join(item.required_files[:3])}"
            )
            return result
        
        # Get the best matching file
        best_match = max(category_files, key=lambda x: x["confidence"])
        result["matched_files"] = [f["filename"] for f in category_files]
        result["confidence"] = best_match["confidence"]
        
        # Find the actual file path
        matched_file_path = None
        for file_path in all_files:
            if file_path.name == best_match["filename"]:
                matched_file_path = file_path
                break
        
        if not matched_file_path:
            result["status"] = ChecklistStatus.INCOMPLETE
            result["issues"].append("File found but could not be accessed")
            return result
        
        # Read and validate file content
        file_data = self.processor.read_file(matched_file_path)
        
        if not file_data.get("success"):
            result["status"] = ChecklistStatus.INCOMPLETE
            result["issues"].append(f"Could not read file: {file_data.get('error')}")
            return result
        
        # Perform content validation based on checklist item type
        content_validation = self._validate_content(item, file_data)
        result["validation_details"] = content_validation
        
        # Determine final status
        if content_validation.get("valid"):
            result["status"] = ChecklistStatus.COMPLETE
        else:
            result["status"] = ChecklistStatus.INCOMPLETE
            result["issues"].extend(content_validation.get("issues", []))
        
        # Add recommendations if needed
        if result["status"] != ChecklistStatus.COMPLETE:
            result["recommendations"].extend(
                self._generate_recommendations(item, content_validation)
            )
        
        return result
    
    def _validate_content(
        self, 
        item: ChecklistItem, 
        file_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate file content based on checklist item type"""
        
        # Use specific validators for different types
        if item.id == "bank_reconciliation":
            return self.parser.validate_bank_reconciliation(file_data)
        elif item.id in ["ar_aging", "ap_aging"]:
            return self.parser.validate_aging_report(file_data)
        elif item.id == "accruals":
            return self.parser.validate_journal_entries(file_data)
        elif item.id == "gl_extract":
            return self.parser.validate_gl_extract(file_data)
        else:
            # Generic validation - check for required keywords
            return self._generic_content_validation(item, file_data)
    
    def _generic_content_validation(
        self, 
        item: ChecklistItem, 
        file_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generic content validation using keywords"""
        
        found_keywords = self.processor.extract_keywords(
            file_data, item.required_content
        )
        
        found_count = sum(found_keywords.values())
        required_count = len(item.required_content)
        
        validation = {
            "valid": found_count >= (required_count * 0.5),  # At least 50% of keywords
            "checks": found_keywords,
            "issues": []
        }
        
        if not validation["valid"]:
            missing_keywords = [k for k, v in found_keywords.items() if not v]
            validation["issues"].append(
                f"Missing expected content. Missing keywords: {', '.join(missing_keywords[:5])}"
            )
        
        return validation
    
    def _generate_recommendations(
        self, 
        item: ChecklistItem, 
        validation: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for fixing issues"""
        
        recommendations = []
        
        if item.id == "bank_reconciliation":
            recommendations.append("Ensure the file contains reconciliation details")
            recommendations.append("Include: opening balance, deposits, withdrawals, closing balance")
            recommendations.append("Mark outstanding items clearly")
        
        elif item.id in ["ar_aging", "ap_aging"]:
            recommendations.append("Include aging buckets: Current, 30, 60, 90+ days")
            recommendations.append("Add customer/vendor names")
            recommendations.append("Include total amounts for each bucket")
        
        elif item.id == "accruals":
            recommendations.append("Ensure debits equal credits")
            recommendations.append("Include account codes and descriptions")
            recommendations.append("Add journal entry reference numbers")
        
        elif item.id == "gl_extract":
            recommendations.append("Include: account code, account name, debit, credit, balance")
            recommendations.append("Ensure trial balance sums correctly")
        
        else:
            recommendations.append(f"Ensure file contains: {', '.join(item.required_content[:3])}")
        
        return recommendations
    
    def _calculate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        
        total = len(results)
        complete = sum(1 for r in results if r["status"] == ChecklistStatus.COMPLETE)
        incomplete = sum(1 for r in results if r["status"] == ChecklistStatus.INCOMPLETE)
        missing = sum(1 for r in results if r["status"] == ChecklistStatus.MISSING)
        
        completion_rate = (complete / total * 100) if total > 0 else 0
        
        return {
            "total_items": total,
            "complete": complete,
            "incomplete": incomplete,
            "missing": missing,
            "completion_rate": round(completion_rate, 2),
            "overall_status": self._get_overall_status(completion_rate),
            "high_priority_complete": self._count_high_priority_complete(results),
            "high_priority_total": len([r for r in results if self._get_item_priority(r["id"]) == 1])
        }
    
    def _get_overall_status(self, completion_rate: float) -> str:
        """Get overall status based on completion rate"""
        if completion_rate >= 90:
            return "excellent"
        elif completion_rate >= 70:
            return "good"
        elif completion_rate >= 50:
            return "fair"
        else:
            return "needs_attention"
    
    def _count_high_priority_complete(self, results: List[Dict[str, Any]]) -> int:
        """Count completed high priority items"""
        count = 0
        for result in results:
            item = get_checklist_by_id(result["id"])
            if item and item.priority == 1 and result["status"] == ChecklistStatus.COMPLETE:
                count += 1
        return count
    
    def _get_item_priority(self, item_id: str) -> int:
        """Get priority of a checklist item"""
        item = get_checklist_by_id(item_id)
        return item.priority if item else 3
    
    def get_incomplete_items(self, validation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of incomplete or missing items"""
        if not validation_result.get("success"):
            return []
        
        checklist_results = validation_result.get("checklist_results", [])
        return [
            r for r in checklist_results 
            if r["status"] in [ChecklistStatus.INCOMPLETE, ChecklistStatus.MISSING]
        ]
    
    def get_completion_report(self, validation_result: Dict[str, Any]) -> str:
        """Generate a human-readable completion report"""
        if not validation_result.get("success"):
            return "Validation failed"
        
        summary = validation_result.get("summary", {})
        
        report = f"""
Month-End Checklist Validation Report
=====================================

Total Items: {summary.get('total_items', 0)}
✅ Complete: {summary.get('complete', 0)}
⚠️  Incomplete: {summary.get('incomplete', 0)}
❌ Missing: {summary.get('missing', 0)}

Completion Rate: {summary.get('completion_rate', 0)}%
Overall Status: {summary.get('overall_status', 'unknown').upper()}

High Priority Items: {summary.get('high_priority_complete', 0)}/{summary.get('high_priority_total', 0)} complete

"""
        
        # Add details for incomplete/missing items
        incomplete = self.get_incomplete_items(validation_result)
        if incomplete:
            report += "\nItems Needing Attention:\n" + "-" * 40 + "\n"
            for item in incomplete:
                report += f"\n{item['name']} [{item['status'].upper()}]\n"
                for issue in item.get('issues', []):
                    report += f"  ❌ {issue}\n"
                if item.get('recommendations'):
                    report += "  💡 Recommendations:\n"
                    for rec in item['recommendations'][:2]:
                        report += f"     - {rec}\n"
        
        return report
