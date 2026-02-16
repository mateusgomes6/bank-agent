#!/usr/bin/env python3
"""
Setup script for Banco Ágil.
Run this script to verify the environment is properly configured.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8+."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"❌ Python 3.8+ required (found {version.major}.{version.minor})")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\n🔍 Checking dependencies...")
    required_packages = [
        'langchain',
        'langchain_community',
        'langchain_google_genai',
        'streamlit',
        'pandas',
        'requests',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed")
    return True


def check_env_file():
    """Check if .env file exists and is configured."""
    print("\n🔍 Checking environment configuration...")
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("Run: cp .env.example .env")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        if "your_google_api_key_here" in content:
            print("⚠️  .env file exists but GOOGLE_API_KEY is not configured")
            print("Please edit .env and add your Google Gemini API key")
            return False
    
    print("✅ .env file configured")
    return True


def check_data_files():
    """Check if data files exist."""
    print("\n🔍 Checking data files...")
    data_dir = Path("src/data")
    required_files = [
        "clientes.csv",
        "score_limite.csv",
        "solicitacoes_aumento_limite.csv"
    ]
    
    missing = []
    for file in required_files:
        file_path = data_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️  Missing files: {', '.join(missing)}")
        return False
    
    return True


def check_file_structure():
    """Check if project structure is correct."""
    print("\n🔍 Checking project structure...")
    required_dirs = [
        "src",
        "src/agents",
        "src/tools",
        "src/utils",
        "src/data",
        "ui",
        "tests"
    ]
    
    missing = []
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/")
            missing.append(dir_name)
    
    if missing:
        return False
    
    return True


def test_imports():
    """Test if main modules can be imported."""
    print("\n🔍 Testing module imports...")
    try:
        from src.agents.triage_agent import TriageAgent
        print("✅ TriageAgent imports")
        
        from src.agents.credit_agent import CreditAgent
        print("✅ CreditAgent imports")
        
        from src.tools.auth_tools import validate_cpf_format
        print("✅ auth_tools imports")
        
        from src.tools.csv_tools import get_cliente_by_cpf
        print("✅ csv_tools imports")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("🏦 Banco Ágil - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_file_structure),
        ("Data Files", check_data_files),
        ("Dependencies", check_dependencies),
        ("Environment Configuration", check_env_file),
        ("Module Imports", test_imports),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print(f"\n{'✅' if passed == total else '⚠️'} {passed}/{total} checks passed")
    
    # Next steps
    if passed == total:
        print("\n🚀 Everything is ready!")
        print("\nTo start the application, run:")
        print("  streamlit run ui/streamlit_app.py")
        return 0
    else:
        print("\n📝 Please fix the issues above before running the application.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
