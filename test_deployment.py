#!/usr/bin/env python3
"""
Deployment Test Script for Shiritori Method Game
Tests the application configuration for deployment readiness
"""

import os
import sys
import json
import importlib.util

def test_environment():
    """Test environment configuration"""
    print("🔧 Testing Environment Configuration...")
    
    # Check for PORT environment variable
    port = os.getenv('PORT', os.getenv('FLASK_PORT', '5000'))
    print(f"  ✓ Port configuration: {port}")
    
    # Check Flask environment
    flask_env = os.getenv('FLASK_ENV', 'development')
    print(f"  ✓ Flask environment: {flask_env}")
    
    # Check for Gemini API key
    has_api_key = bool(os.getenv('GEMINI_API_KEY'))
    print(f"  ✓ Gemini API key: {'configured' if has_api_key else 'not configured (AI features will use fallback)'}")
    
    return True

def test_dependencies():
    """Test if all required dependencies are available"""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        ('flask', 'Flask'),
        ('gunicorn', 'Gunicorn'),
        ('google.generativeai', 'Google Generative AI (optional)'),
    ]
    
    all_good = True
    for module_name, display_name in required_packages:
        spec = importlib.util.find_spec(module_name.split('.')[0])
        if spec is not None:
            print(f"  ✓ {display_name}: installed")
        else:
            if 'optional' in display_name:
                print(f"  ⚠️  {display_name}: not installed")
            else:
                print(f"  ❌ {display_name}: NOT INSTALLED")
                all_good = False
    
    return all_good

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'render.yaml',
        'Procfile',
        'runtime.txt',
        'templates/index.html',
        'static/game.js',
        'static/style.css',
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}: found")
        else:
            print(f"  ❌ {file_path}: NOT FOUND")
            all_good = False
    
    return all_good

def test_app_import():
    """Test if the Flask app can be imported"""
    print("\n🚀 Testing App Import...")
    
    try:
        # Set production environment for testing
        os.environ['FLASK_ENV'] = 'production'
        
        # Try to import the app
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        # Check if app exists
        if hasattr(app_module, 'app'):
            print("  ✓ Flask app imported successfully")
            return True
        else:
            print("  ❌ Flask app not found in app.py")
            return False
            
    except Exception as e:
        print(f"  ❌ Failed to import app: {e}")
        return False

def test_scores_file():
    """Test score file handling"""
    print("\n💾 Testing Score File Handling...")
    
    scores_file = os.getenv('SCORES_FILE', 'game_scores.json')
    
    # Test reading scores
    try:
        if os.path.exists(scores_file):
            with open(scores_file, 'r') as f:
                scores = json.load(f)
            print(f"  ✓ Score file readable: {scores_file}")
        else:
            print(f"  ℹ️  Score file doesn't exist yet (will be created): {scores_file}")
        
        # Test writing (to temp file)
        temp_file = scores_file + '.test'
        test_data = {'number_game': [], 'word_game': []}
        try:
            with open(temp_file, 'w') as f:
                json.dump(test_data, f)
            os.remove(temp_file)
            print("  ✓ Score file writing works")
        except:
            print("  ⚠️  Score file writing may not work (common on read-only filesystems)")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Score file handling issue: {e}")
        return True  # Not critical for deployment

def main():
    """Run all deployment tests"""
    print("🎮 Shiritori Method Game - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_dependencies,
        test_file_structure,
        test_app_import,
        test_scores_file,
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Your app is ready for deployment.")
        print("\nNext steps:")
        print("1. Commit your changes: git add . && git commit -m 'Fix deployment issues'")
        print("2. Push to your repository: git push origin main")
        print("3. Deploy on Render:")
        print("   - Go to https://render.com")
        print("   - Connect your repository")
        print("   - The app will auto-deploy with the fixed configuration")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())