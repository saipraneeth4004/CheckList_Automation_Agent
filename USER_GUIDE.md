# Monthly Close Checklist Automation Agent - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the Application](#using-the-application)
4. [Features in Detail](#features-in-detail)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

---

## Introduction

### What is the Monthly Close Checklist Automation Agent?

The Monthly Close Checklist Automation Agent is an AI-powered tool that helps accounting teams streamline their month-end close process by:

- **Automatically validating** uploaded files against a standard checklist
- **Identifying missing or incomplete** items
- **Providing AI-guided assistance** to complete missing tasks
- **Generating required documents** based on your data

### Who should use this tool?

- Accounting managers and staff
- Finance teams handling month-end close
- Controllers and CFOs
- Anyone responsible for monthly financial reporting

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Basic knowledge of month-end accounting processes

### Installation

#### Option 1: Quick Start (Windows)

1. Download the project
2. Copy `.env.example` to `.env`
3. Add your Google API key to `.env`
4. Double-click `start.bat`

#### Option 2: Quick Start (Linux/Mac)

```bash
# Make start script executable
chmod +x start.sh

# Run the application
./start.sh
```

#### Option 3: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API key

# Generate sample data
python generate_sample_data.py

# Start FastAPI backend
python -m uvicorn app.main:app --reload --port 8000

# In another terminal, start Streamlit frontend
streamlit run app/ui/streamlit_app.py
```

#### Option 4: Docker

```bash
# Copy and configure .env
cp .env.example .env
# Edit .env with your API key

# Start with Docker Compose
docker-compose up
```

### Accessing the Application

Once running:
- **Frontend**: http://localhost:8501
- **API Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Using the Application

### Step-by-Step Walkthrough

#### 1. Start a New Session

1. Open the Streamlit UI at http://localhost:8501
2. Click **"Start New Session"** button
3. A unique session ID will be created for your work

#### 2. Upload Your Month-End Files

1. Navigate to **"📁 Upload & Validate"** page
2. Click **"Browse files"** or drag and drop your files
3. Supported formats: Excel (.xlsx, .xls), CSV, PDF, Text
4. Click **"⬆️ Upload Files"**

**Tip**: You can upload multiple files at once!

#### 3. Validate Your Checklist

1. After uploading, click **"🔍 Validate Checklist"**
2. Wait for the validation to complete (usually 5-10 seconds)
3. View your results:
   - **Completion Rate**: Overall percentage complete
   - **Item Status**: Each checklist item's status

#### 4. Review Checklist Status

1. Navigate to **"📋 Checklist Status"** page
2. Filter items by status (Complete/Incomplete/Missing)
3. Expand any item to see:
   - Detailed issues
   - Recommendations
   - Matched files

#### 5. Get AI Assistance

1. Navigate to **"💬 AI Assistant"** page
2. Ask questions about your month-end close:
   - "What items are missing?"
   - "How do I complete the bank reconciliation?"
   - "Analyze my results"
3. Get step-by-step guidance and recommendations

#### 6. Generate Missing Documents

1. Navigate to **"📄 Generate Documents"** page
2. Select the document you want to generate
3. Provide required data (or generate a template)
4. Click **"Generate Document"**
5. Download the generated Excel file
6. Fill in any remaining details
7. Upload back to your session for re-validation

---

## Features in Detail

### Checklist Items Validated

The system validates these 10 standard month-end items:

1. **Bank Reconciliation**
   - Checks for: reconciliation structure, balances, outstanding items
   - Required content: balance, deposits, checks, reconciliation

2. **Accounts Receivable Aging**
   - Checks for: aging buckets (Current, 30, 60, 90+ days)
   - Required content: customer names, amounts, aging categories

3. **Accounts Payable Aging**
   - Checks for: vendor aging buckets
   - Required content: vendor names, amounts, aging categories

4. **Accrual Entries**
   - Checks for: balanced debits and credits
   - Required content: account codes, descriptions, amounts

5. **General Ledger Extract**
   - Checks for: account structure, trial balance
   - Required content: accounts, debits, credits, balances

6. **Prepayments Schedule**
   - Checks for: amortization tracking
   - Required content: assets, amounts, amortization

7. **Fixed Assets Register**
   - Checks for: depreciation calculations
   - Required content: assets, cost, depreciation, NBV

8. **Intercompany Reconciliation**
   - Checks for: balanced intercompany accounts
   - Required content: entities, balances, reconciliation

9. **Revenue Recognition**
   - Checks for: revenue tracking
   - Required content: revenue, periods, amounts

10. **Expense Analysis**
    - Checks for: expense categorization
    - Required content: categories, amounts, analysis

### File Classification

The system automatically classifies files based on:
- **Filename patterns**: Keywords like "bank_reconciliation", "ar_aging"
- **Content analysis**: Actual data columns and structure
- **Confidence scoring**: How confident the system is about the match

### AI Capabilities

The AI assistant can:
- **Analyze** your validation results
- **Explain** what's missing or incomplete
- **Guide** you through completing items
- **Ask questions** to gather necessary data
- **Generate** documents based on your responses
- **Provide recommendations** for best practices

### Document Generation

Generated documents include:
- **Excel templates** with proper formatting
- **Pre-filled formulas** for calculations
- **Professional styling** (headers, borders, colors)
- **Sample data** to guide you
- **Empty rows** for you to fill in

---

## Troubleshooting

### Common Issues

#### Application Won't Start

**Problem**: Import errors or missing dependencies

**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### API Key Error

**Problem**: "Invalid API key" or authentication errors

**Solution**:
1. Check your `.env` file has the correct API key
2. Ensure no extra spaces or quotes around the key
3. Verify your API key is active at Google AI Studio

#### Files Not Being Validated

**Problem**: Validation shows all items as "missing"

**Solution**:
1. Check file names contain relevant keywords
2. Ensure files are in supported formats (.xlsx, .csv, etc.)
3. Verify files contain actual data (not empty)
4. Try uploading files with more explicit names

#### Connection Error

**Problem**: "Cannot connect to API"

**Solution**:
1. Ensure FastAPI backend is running on port 8000
2. Check no firewall is blocking the connection
3. Verify `API_BASE_URL` in Streamlit app

#### Slow Performance

**Problem**: Validation or AI responses take too long

**Solution**:
1. Check your internet connection (AI requires API calls)
2. Reduce number of files uploaded at once
3. Use smaller file sizes if possible
4. Check Google API quota limits

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Session not found" | Invalid or expired session | Start a new session |
| "File type not allowed" | Unsupported file format | Use .xlsx, .csv, .pdf, or .txt |
| "File too large" | File exceeds size limit | Reduce file size or split data |
| "No files uploaded" | Trying to validate without files | Upload files first |
| "Error generating analysis" | AI service issue | Check API key and internet |

---

## Best Practices

### File Naming Conventions

Use descriptive names that include keywords:
- ✅ `bank_reconciliation_dec2024.xlsx`
- ✅ `ar_aging_report_december.xlsx`
- ✅ `accrual_journal_entries_2024.xlsx`
- ❌ `file1.xlsx`
- ❌ `data.xlsx`

### File Organization

- Keep one checklist item per file
- Use consistent naming across months
- Include period/date in filenames
- Maintain original file formats from source systems

### Using the AI Assistant

**Good Questions**:
- "What's the best way to prepare a bank reconciliation?"
- "My AR aging is incomplete. What am I missing?"
- "Can you explain the validation results?"

**Less Helpful Questions**:
- "Hi" or "Hello" (be specific)
- Vague requests without context
- Questions unrelated to accounting

### Document Generation

1. **Gather data first**: Have your raw data ready before generating
2. **Use templates**: Generate a template, fill it in Excel, then re-upload
3. **Verify formulas**: Check that calculated totals make sense
4. **Save copies**: Keep generated documents as templates for future months

### Session Management

- **One session per month-end period**: Don't mix different months
- **Complete workflow**: Upload → Validate → Review → Generate → Re-validate
- **Start fresh if needed**: Create new session if you start over

---

## Advanced Tips

### Using Sample Data

The project includes sample data in `sample_data/`:
- `complete_month_end/`: Fully complete example
- `incomplete_month_end/`: Partially complete example

Use these to:
1. Test the application
2. See what complete files look like
3. Understand the validation logic
4. Train your team

### API Integration

For power users, you can integrate with the API directly:

```python
import requests

# Create session and upload files programmatically
session_id = create_session()
upload_files(session_id, file_list)
results = validate_files(session_id)

# Process results in your own application
for item in results['checklist_results']:
    if item['status'] != 'complete':
        print(f"Missing: {item['name']}")
```

See `API_DOCUMENTATION.md` for full API details.

### Customization

The checklist is defined in `app/validation/checklist_config.py`. You can:
- Modify existing items
- Add new checklist items
- Change validation rules
- Adjust priority levels

---

## Getting Help

### Resources

- **README.md**: Project overview and setup
- **API_DOCUMENTATION.md**: API reference
- **PROJECT_PLAN.md**: Technical architecture

### Support

For issues:
1. Check this user guide
2. Review error messages
3. Check sample data for examples
4. Open an issue on GitHub

### Contributing

We welcome contributions! Areas for improvement:
- Additional checklist items
- Enhanced validation rules
- New document templates
- UI improvements
- Bug fixes

---

## Appendix

### Keyboard Shortcuts (Streamlit)

- `R`: Rerun the app
- `C`: Clear cache
- `M`: Toggle menu

### File Size Limits

- Default max upload: 100MB per file
- Can be configured in `.env` file
- Recommended: Keep files under 10MB for best performance

### Session Timeout

- Default: 60 minutes of inactivity
- Sessions are automatically cleaned up
- Start a new session if yours expires

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**License**: MIT
