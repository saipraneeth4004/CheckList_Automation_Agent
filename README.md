# 📊 Monthly Close Checklist Automation Agent

An AI-driven application that automates the validation of month-end accounting checklists, providing intelligent assistance and automated document generation for incomplete tasks.

## 🌟 Features

- **Automated Checklist Validation**: Upload your month-end folders and get instant validation against standard accounting checklists
- **AI-Powered Analysis**: Comprehensive document analysis using Google Gemini Flash model
- **Interactive Assistance**: Conversational AI agent guides you through completing missing items
- **Smart Document Generation**: Automatically generates missing documents based on your data
- **User-Friendly Interface**: Clean Streamlit dashboard with real-time status updates

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │
│   (Frontend)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   FastAPI       │◄────►│  Gemini Flash    │
│   (Backend)     │      │  + LangChain     │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Validation Engine + File Processor │
└─────────────────────────────────────┘
```

## 📋 Validated Checklist Items

1. ✅ Bank Reconciliation
2. ✅ Accounts Receivable Aging
3. ✅ Accounts Payable Aging
4. ✅ Accrual Entries
5. ✅ General Ledger Extract
6. ✅ Prepayments Schedule
7. ✅ Fixed Assets Register
8. ✅ Intercompany Reconciliation
9. ✅ Revenue Recognition
10. ✅ Expense Analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CheckList_Automation_Agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### Running the Application

1. **Start the FastAPI backend**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   streamlit run app/ui/streamlit_app.py
   ```

3. **Access the application**
   - Frontend: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## 📖 Usage Guide

### Step 1: Upload Month-End Folder
- Click on "Upload Folder" in the Streamlit interface
- Select and upload your month-end accounting files

### Step 2: Review Checklist Status
- The system automatically analyzes your files
- View the checklist dashboard showing Complete/Incomplete/Missing items

### Step 3: Get AI Assistance
- For incomplete items, click "Get Help"
- The AI assistant will guide you through completion steps
- Answer follow-up questions to provide necessary data

### Step 4: Generate Missing Documents
- Based on your inputs, the AI generates required documents
- Download generated files and add them to your folder

### Step 5: Re-validate
- Upload the updated folder to verify completion
- Export final checklist report

## 🗂️ Sample Data

Sample month-end folders are provided in the `sample_data/` directory:

- `complete_month_end/`: A complete month-end folder for testing
- `incomplete_month_end/`: An incomplete folder to see the assistant in action

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| AI Model | Google Gemini Flash |
| Agent Framework | LangChain |
| Data Processing | Pandas |
| Excel Handling | OpenPyXL |
| PDF Processing | pdfplumber |

## 📁 Project Structure

```
CheckList_Automation_Agent/
├── app/
│   ├── api/              # FastAPI routes and models
│   ├── core/             # Configuration and utilities
│   ├── ingestion/        # File processing modules
│   ├── validation/       # Checklist validation engine
│   ├── ai/               # AI and LangChain integration
│   └── ui/               # Streamlit interface
├── sample_data/          # Sample accounting files
├── uploads/              # User uploaded files
├── generated/            # AI-generated documents
└── tests/                # Test suite
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

## 🔐 Security

- Store API keys in `.env` file (never commit to git)
- File uploads are isolated per session
- Input validation on all endpoints
- Size limits on file uploads

## 📝 API Documentation

Once the FastAPI server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review sample data examples
3. Open an issue on GitHub

## 🗺️ Roadmap

- [ ] Multi-user authentication
- [ ] Historical analytics dashboard
- [ ] Custom checklist configuration
- [ ] Email notifications
- [ ] Integration with accounting software
- [ ] Cloud storage support

---

**Built with ❤️ using AI-powered automation**
