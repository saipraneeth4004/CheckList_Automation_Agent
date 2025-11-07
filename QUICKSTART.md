# 🚀 Quick Setup Guide

## 5-Minute Setup

### Step 1: Get Your Google API Key
1. Visit https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the generated key

### Step 2: Configure Environment
```bash
# Copy the example environment file
copy .env.example .env

# Open .env in your text editor
notepad .env

# Replace "your_gemini_api_key_here" with your actual API key
GOOGLE_API_KEY=AIzaSy...your_actual_key_here
```

### Step 3: Run the Application

**Windows Users:**
```bash
# Simply double-click start.bat
# Or from command prompt:
start.bat
```

**Linux/Mac Users:**
```bash
chmod +x start.sh
./start.sh
```

**Using Docker:**
```bash
docker-compose up
```

### Step 4: Access the Application
- 🌐 **Open your browser**: http://localhost:8501
- 📚 **API Documentation**: http://localhost:8000/docs

---

## What Happens During Setup?

The startup script automatically:
1. ✅ Creates a Python virtual environment
2. ✅ Installs all required dependencies
3. ✅ Generates sample accounting data
4. ✅ Starts the FastAPI backend (port 8000)
5. ✅ Starts the Streamlit frontend (port 8501)

---

## First Time Usage

### Try the Sample Data

1. Click **"Start New Session"**
2. Navigate to the `sample_data/incomplete_month_end/` folder
3. Upload the sample files
4. Click **"Validate Checklist"**
5. See which items are complete and which are missing!

### Generate Your First Document

1. After validation, go to **"📄 Generate Documents"**
2. Select a missing item (e.g., "Accrual Entries")
3. Click **"Generate Document"**
4. Download and review the Excel template
5. Fill it in with your data
6. Upload and re-validate!

---

## Troubleshooting

### "Import errors" when starting
```bash
# Upgrade pip and reinstall
pip install --upgrade pip
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Kill processes on ports 8000 and 8501
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
```

### "No module named 'app'"
```bash
# Make sure you're in the project root directory
cd CheckList_Automation_Agent
# And running from there
```

---

## Next Steps

✅ **Read the User Guide**: See `USER_GUIDE.md` for detailed instructions

✅ **Explore the API**: Check `API_DOCUMENTATION.md` for API integration

✅ **Review the Architecture**: See `PROJECT_PLAN.md` for technical details

---

## Need Help?

- 📖 Check USER_GUIDE.md for detailed walkthroughs
- 🐛 Found a bug? Open an issue
- 💡 Have a suggestion? We'd love to hear it!

---

**Happy Month-End Closing! 📊✨**
