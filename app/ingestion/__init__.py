"""
Ingestion module initialization
"""

from app.ingestion.file_classifier import FileClassifier
from app.ingestion.file_processor import FileProcessor
from app.ingestion.document_parser import DocumentParser

__all__ = [
    "FileClassifier",
    "FileProcessor",
    "DocumentParser"
]
