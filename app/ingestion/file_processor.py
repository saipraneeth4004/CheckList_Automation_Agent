"""
File processor for reading various file formats
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import openpyxl
from io import BytesIO


class FileProcessor:
    """Handles reading and basic processing of various file formats"""
    
    SUPPORTED_FORMATS = {
        '.xlsx': 'excel',
        '.xls': 'excel_old',
        '.csv': 'csv',
        '.txt': 'text',
        '.pdf': 'pdf'
    }
    
    def __init__(self):
        self.cache = {}
    
    def read_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Read a file and return its contents
        
        Returns:
            dict with file info and content
        """
        extension = file_path.suffix.lower()
        
        if extension not in self.SUPPORTED_FORMATS:
            return {
                "success": False,
                "error": f"Unsupported file format: {extension}"
            }
        
        try:
            if extension in ['.xlsx', '.xls']:
                return self._read_excel(file_path)
            elif extension == '.csv':
                return self._read_csv(file_path)
            elif extension == '.txt':
                return self._read_text(file_path)
            elif extension == '.pdf':
                return self._read_pdf(file_path)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": str(file_path)
            }
    
    def _read_excel(self, file_path: Path) -> Dict[str, Any]:
        """Read Excel file"""
        try:
            # Read with pandas for data
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            sheets_data = {}
            for sheet_name in sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheets_data[sheet_name] = {
                    "data": df,
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "preview": df.head(10).to_dict('records') if not df.empty else []
                }
            
            # Also load with openpyxl for metadata
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            
            return {
                "success": True,
                "file_type": "excel",
                "file_path": str(file_path),
                "sheet_names": sheet_names,
                "sheet_count": len(sheet_names),
                "sheets": sheets_data,
                "workbook": workbook
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading Excel file: {str(e)}",
                "file_path": str(file_path)
            }
    
    def _read_csv(self, file_path: Path) -> Dict[str, Any]:
        """Read CSV file"""
        try:
            df = pd.read_csv(file_path)
            
            return {
                "success": True,
                "file_type": "csv",
                "file_path": str(file_path),
                "data": df,
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "preview": df.head(10).to_dict('records') if not df.empty else []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading CSV file: {str(e)}",
                "file_path": str(file_path)
            }
    
    def _read_text(self, file_path: Path) -> Dict[str, Any]:
        """Read text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            return {
                "success": True,
                "file_type": "text",
                "file_path": str(file_path),
                "content": content,
                "lines": lines,
                "line_count": len(lines),
                "preview": '\n'.join(lines[:20])
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading text file: {str(e)}",
                "file_path": str(file_path)
            }
    
    def _read_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Read PDF file - basic implementation"""
        try:
            # Try importing pdfplumber
            try:
                import pdfplumber
                
                with pdfplumber.open(file_path) as pdf:
                    pages = []
                    for page in pdf.pages:
                        text = page.extract_text()
                        tables = page.extract_tables()
                        pages.append({
                            "text": text,
                            "tables": tables
                        })
                    
                    return {
                        "success": True,
                        "file_type": "pdf",
                        "file_path": str(file_path),
                        "page_count": len(pages),
                        "pages": pages,
                        "preview": pages[0]["text"][:500] if pages else ""
                    }
            except ImportError:
                # Fallback to PyPDF2
                import PyPDF2
                
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    pages = []
                    
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        pages.append({"text": text})
                    
                    return {
                        "success": True,
                        "file_type": "pdf",
                        "file_path": str(file_path),
                        "page_count": len(pages),
                        "pages": pages,
                        "preview": pages[0]["text"][:500] if pages else ""
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading PDF file: {str(e)}",
                "file_path": str(file_path)
            }
    
    def extract_keywords(self, file_data: Dict[str, Any], keywords: List[str]) -> Dict[str, bool]:
        """
        Check if specific keywords exist in file content
        
        Returns:
            dict mapping keyword to boolean (found/not found)
        """
        found_keywords = {}
        content_text = ""
        
        # Extract text based on file type
        if file_data.get("file_type") == "excel":
            for sheet_name, sheet_data in file_data.get("sheets", {}).items():
                df = sheet_data.get("data")
                if df is not None:
                    content_text += " " + df.to_string().lower()
        elif file_data.get("file_type") == "csv":
            df = file_data.get("data")
            if df is not None:
                content_text = df.to_string().lower()
        elif file_data.get("file_type") == "text":
            content_text = file_data.get("content", "").lower()
        elif file_data.get("file_type") == "pdf":
            for page in file_data.get("pages", []):
                content_text += " " + page.get("text", "").lower()
        
        # Check for keywords
        for keyword in keywords:
            found_keywords[keyword] = keyword.lower() in content_text
        
        return found_keywords
    
    def get_dataframe_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for a DataFrame"""
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include='number').columns) > 0 else {}
        }
