"""
Installation and Environment Verification Script
Checks all prerequisites and dependencies before running the application
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_python_version():
    """Check Python version"""
    print("\n📌 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.10+ is required")
        return False


def check_pip():
    """Check if pip is available"""
    print("\n📌 Checking pip...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        print(f"   {result.stdout.strip()}")
        print("   ✅ pip is available")
        return True
    except Exception as e:
        print(f"   ❌ pip not found: {e}")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("\n📌 Checking .env file...")
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("   ✅ .env file exists")
        
        # Check if API key is set
        with open(env_file, 'r') as f:
            content = f.read()
            if "your_gemini_api_key_here" in content:
                print("   ⚠️  WARNING: Please update .env with your actual API key")
                return False
            elif "GOOGLE_API_KEY=" in content:
                print("   ✅ API key appears to be configured")
                return True
    else:
        print("   ❌ .env file not found")
        if env_example.exists():
            print("   💡 Run: copy .env.example .env")
        return False


def check_directories():
    """Check required directories"""
    print("\n📌 Checking required directories...")
    
    dirs = {
        "app": "Main application directory",
        "uploads": "File upload directory",
        "generated": "Generated files directory",
    }
    
    all_exist = True
    for dir_name, description in dirs.items():
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"   ✅ {dir_name}/ - {description}")
        else:
            print(f"   ❌ {dir_name}/ not found - {description}")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Check if required packages are installed"""
    print("\n📌 Checking installed packages...")
    
    required_packages = [
        "fastapi",
        "streamlit",
        "pandas",
        "openpyxl",
        "google-generativeai",
        "langchain",
        "uvicorn"
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Extract version
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        print(f"   ✅ {package} ({version})")
                        break
            else:
                print(f"   ❌ {package} - NOT INSTALLED")
                missing.append(package)
        except Exception as e:
            print(f"   ❌ {package} - Error checking: {e}")
            missing.append(package)
    
    if missing:
        print(f"\n   💡 To install missing packages, run:")
        print(f"      pip install -r requirements.txt")
        return False
    
    return True


def check_ports():
    """Check if required ports are available"""
    print("\n📌 Checking port availability...")
    
    import socket
    
    ports = {
        8000: "FastAPI Backend",
        8501: "Streamlit Frontend"
    }
    
    all_available = True
    
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"   ⚠️  Port {port} ({service}) is already in use")
            all_available = False
        else:
            print(f"   ✅ Port {port} ({service}) is available")
    
    return all_available


def check_sample_data():
    """Check if sample data exists"""
    print("\n📌 Checking sample data...")
    
    sample_dir = Path("sample_data/complete_month_end")
    
    if sample_dir.exists():
        files = list(sample_dir.glob("*.xlsx"))
        print(f"   ✅ Sample data exists ({len(files)} files)")
        return True
    else:
        print("   ⚠️  Sample data not found")
        print("   💡 Run: python generate_sample_data.py")
        return False


def main():
    """Run all checks"""
    print_header("Monthly Close Checklist Automation - System Check")
    
    checks = {
        "Python Version": check_python_version(),
        "pip": check_pip(),
        "Environment File": check_env_file(),
        "Directories": check_directories(),
        "Dependencies": check_dependencies(),
        "Ports": check_ports(),
        "Sample Data": check_sample_data()
    }
    
    print_header("Summary")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    print("\nDetailed Results:")
    for check, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {check}")
    
    if all(checks.values()):
        print_header("🎉 All Checks Passed! You're Ready to Run!")
        print("\nNext steps:")
        print("   1. Run: start.bat (Windows) or ./start.sh (Linux/Mac)")
        print("   2. Open: http://localhost:8501")
        print("   3. Enjoy your automated month-end close!")
    else:
        print_header("⚠️  Some Checks Failed")
        print("\nPlease fix the issues above before running the application.")
        print("See QUICKSTART.md or README.md for help.")
    
    print("\n")
    return all(checks.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
