#!/usr/bin/env python3
"""
Setup Check for Replit Proxy Checker
Verifies that all files and dependencies are properly configured.
"""

import sys
import os
import importlib

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check:")
    version = sys.version_info
    print(f"   Current version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 6:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.6+ required")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Dependency Check:")
    required_packages = ['requests', 'urllib3', 'certifi']
    missing_packages = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package} - installed")
        except ImportError:
            print(f"   ❌ {package} - missing")
            missing_packages.append(package)

    if missing_packages:
        print("\n   📋 To install missing packages:")
        print("   Method 1: Use Replit Packages tab")
        print("   Method 2: Run in Shell: pip install " + " ".join(missing_packages))
        return False

    return True

def check_files():
    """Check if all required files are present"""
    print("\n📁 File Check:")
    required_files = [
        'main.py',
        'requirements.txt', 
        '.replit',
        'README.md',
        'sample_proxies.txt'
    ]

    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} - {size} bytes")
        else:
            print(f"   ❌ {file} - missing")
            missing_files.append(file)

    if missing_files:
        print("\n   📋 Missing files need to be uploaded to Replit")
        return False

    return True

def check_replit_environment():
    """Check if running in Replit"""
    print("\n🌐 Environment Check:")

    if 'REPL_ID' in os.environ:
        print("   ✅ Running in Replit environment")
        repl_id = os.environ.get('REPL_ID', 'unknown')
        print(f"   📍 Repl ID: {repl_id[:10]}...")
        return True
    else:
        print("   ⚠️  Not running in Replit (but should still work)")
        return True

def test_main_import():
    """Test if main module can be imported"""
    print("\n🔧 Module Import Test:")

    try:
        from main import ProxyChecker
        print("   ✅ ProxyChecker class imported successfully")

        # Test instantiation
        checker = ProxyChecker(timeout=5, max_workers=5)
        print("   ✅ ProxyChecker instance created")
        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Instantiation error: {e}")
        return False

def run_quick_test():
    """Run a quick functionality test"""
    print("\n🧪 Quick Functionality Test:")

    try:
        from main import ProxyChecker
        checker = ProxyChecker(timeout=2, max_workers=1)

        # Test with a dummy proxy (will fail, but should handle gracefully)
        result = checker.check_proxy("127.0.0.1:8080")

        if isinstance(result, dict) and 'proxy' in result and 'status' in result:
            print("   ✅ Proxy checking function works")
            print(f"   📊 Test result: {result['status']} - {result.get('error', 'N/A')}")
            return True
        else:
            print("   ❌ Unexpected result format")
            return False

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Run all setup checks"""
    print("🔍 REPLIT PROXY CHECKER - SETUP VERIFICATION")
    print("=" * 60)

    checks = [
        check_python_version(),
        check_dependencies(),
        check_files(),
        check_replit_environment(),
        test_main_import(),
        run_quick_test()
    ]

    passed = sum(checks)
    total = len(checks)

    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY:")
    print(f"   Checks passed: {passed}/{total}")

    if passed == total:
        print("   🎉 ALL CHECKS PASSED!")
        print("   ✅ Your proxy checker is ready to use!")
        print("\n🚀 Next steps:")
        print("   1. Run 'python main.py' to start the proxy checker")
        print("   2. Or click the Run button in Replit")
        print("   3. Follow the interactive menu")
    else:
        print("   ⚠️  Some checks failed - see details above")
        print("\n🔧 Troubleshooting:")
        print("   1. Install missing dependencies")
        print("   2. Upload missing files")
        print("   3. Check file permissions")
        print("   4. Try refreshing Replit")

    print("\n📚 For help, check README.md or run the demo.py")

if __name__ == "__main__":
    main()
