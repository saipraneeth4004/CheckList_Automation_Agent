# Monthly Close Checklist Automation Agent - API Documentation

## Overview

This document provides comprehensive API documentation for the Monthly Close Checklist Automation Agent backend.

**Base URL**: `http://localhost:8000/api/v1`

**Interactive Documentation**: `http://localhost:8000/docs`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Endpoints

### Health Check

#### GET /health
Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Session Management

#### POST /session/create
Create a new user session.

**Response**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00",
  "files_count": 0,
  "has_validation_results": false
}
```

#### GET /session/{session_id}
Get session information.

**Parameters**:
- `session_id` (path): Session UUID

**Response**: Same as create session

---

### File Upload

#### POST /upload/{session_id}
Upload month-end files for validation.

**Parameters**:
- `session_id` (path): Session UUID
- `files` (form-data): Multiple files

**Supported File Types**: .xlsx, .xls, .csv, .pdf, .txt

**Response**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "uploaded_files": [
    {
      "filename": "bank_reconciliation.xlsx",
      "size": 15360,
      "size_mb": 0.01,
      "extension": ".xlsx"
    }
  ],
  "total_files": 1
}
```

---

### Validation

#### POST /validate/{session_id}
Validate uploaded files against checklist.

**Parameters**:
- `session_id` (path): Session UUID

**Response**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "folder_path": "/path/to/session/folder",
  "total_files": 5,
  "file_names": ["file1.xlsx", "file2.xlsx"],
  "checklist_results": [
    {
      "id": "bank_reconciliation",
      "name": "Bank Reconciliation",
      "description": "Reconciliation of bank statements with cash book entries",
      "status": "complete",
      "confidence": 0.85,
      "matched_files": ["bank_reconciliation.xlsx"],
      "issues": [],
      "recommendations": [],
      "validation_details": {
        "valid": true,
        "checks": {
          "has_balance": true,
          "has_reconciliation_keywords": true
        }
      }
    }
  ],
  "summary": {
    "total_items": 10,
    "complete": 7,
    "incomplete": 2,
    "missing": 1,
    "completion_rate": 70.0,
    "overall_status": "good",
    "high_priority_complete": 4,
    "high_priority_total": 5
  }
}
```

---

### AI Chat

#### POST /chat
Chat with AI assistant.

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "How do I complete the bank reconciliation?",
  "context": {
    "item_id": "bank_reconciliation"
  }
}
```

**Response**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "To complete the bank reconciliation, you need to...",
  "suggestions": ["Upload bank statement", "Verify outstanding checks"]
}
```

---

### Document Generation

#### POST /generate-document
Generate a missing document.

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "checklist_item_id": "bank_reconciliation",
  "user_data": {
    "period": "December 2024",
    "bank_account": "Checking Account",
    "bank_balance": 50000
  },
  "filename": "bank_recon_dec2024.xlsx"
}
```

**Response**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "bank_recon_dec2024.xlsx",
  "file_path": "/path/to/generated/file.xlsx",
  "download_url": "/download/550e8400-e29b-41d4-a716-446655440000/bank_recon_dec2024.xlsx"
}
```

---

### File Download

#### GET /download/{session_id}/{filename}
Download a generated file.

**Parameters**:
- `session_id` (path): Session UUID
- `filename` (path): Filename to download

**Response**: File download

---

### Checklist Information

#### GET /checklist/info
Get information about the standard checklist.

**Response**:
```json
{
  "total_items": 10,
  "high_priority": 5,
  "medium_priority": 4,
  "low_priority": 1,
  "items": [
    {
      "id": "bank_reconciliation",
      "name": "Bank Reconciliation",
      "description": "...",
      "priority": 1
    }
  ]
}
```

---

### AI Analysis

#### GET /checklist/analyze/{session_id}
Get AI analysis of validation results.

**Parameters**:
- `session_id` (path): Session UUID

**Response**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "analysis": "Your month-end close is 70% complete. Priority items that need attention include..."
}
```

---

### Item Guidance

#### GET /checklist/guidance/{session_id}/{item_id}
Get guidance for completing a specific item.

**Parameters**:
- `session_id` (path): Session UUID
- `item_id` (path): Checklist item ID

**Response**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "item_id": "bank_reconciliation",
  "item_name": "Bank Reconciliation",
  "status": "incomplete",
  "guidance": "Step-by-step instructions...",
  "questions": [
    "What is your bank account number?",
    "What is the ending balance per bank statement?"
  ],
  "issues": ["Missing reconciliation structure"],
  "recommendations": ["Include outstanding checks", "Add deposits in transit"]
}
```

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information"
}
```

### Common HTTP Status Codes

- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `413`: File Too Large
- `500`: Internal Server Error

---

## Rate Limiting

Currently, there is no rate limiting implemented.

## Websockets

Not currently supported. All communication is via HTTP REST.

---

## Example Workflows

### Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Create session
response = requests.post(f"{BASE_URL}/session/create")
session_id = response.json()["session_id"]

# 2. Upload files
files = [
    ("files", open("bank_recon.xlsx", "rb")),
    ("files", open("ar_aging.xlsx", "rb"))
]
response = requests.post(f"{BASE_URL}/upload/{session_id}", files=files)

# 3. Validate
response = requests.post(f"{BASE_URL}/validate/{session_id}")
results = response.json()

# 4. Get AI analysis
response = requests.get(f"{BASE_URL}/checklist/analyze/{session_id}")
analysis = response.json()["analysis"]
print(analysis)

# 5. Generate missing document
data = {
    "session_id": session_id,
    "checklist_item_id": "ap_aging",
    "user_data": {}
}
response = requests.post(f"{BASE_URL}/generate-document", json=data)
download_url = response.json()["download_url"]

# 6. Download generated file
response = requests.get(f"http://localhost:8000{download_url}")
with open("ap_aging_generated.xlsx", "wb") as f:
    f.write(response.content)
```

---

## Support

For issues or questions, please refer to the main README.md or open an issue on GitHub.
