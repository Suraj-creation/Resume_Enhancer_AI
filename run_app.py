"""
Run script for Resume Enhancer Application
This script:
1. Checks for and installs required dependencies
2. Sets up environment variables
3. Launches the Streamlit app
"""

import os
import sys
import subprocess
import importlib

def check_dependencies():
    """
    Check if required Python modules are installed and install missing ones if needed.
    Returns True if all dependencies are satisfied, False if installation failed.
    """
    required_modules = [
        "streamlit",
        "PyPDF2",
        "typing_extensions"
    ]
    
    optional_modules = [
        "transformers",
        "torch"
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required modules
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_required.append(module)
    
    # Check optional modules
    for module in optional_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_optional.append(module)
    
    # Install missing required modules
    if missing_required:
        print(f"Installing missing required modules: {', '.join(missing_required)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_required])
            print("Required modules installed successfully.")
        except subprocess.CalledProcessError:
            print("Error installing required modules. Please run: pip install " + " ".join(missing_required))
            return False
    
    # Notify about missing optional modules but don't fail
    if missing_optional:
        print(f"Optional modules not found: {', '.join(missing_optional)}")
        print("For enhanced AI features, consider installing: pip install " + " ".join(missing_optional))
        print("The application will run with basic functionality only.")
    
    return True

def run_app():
    """Run the Resume Enhancer application"""
    print("Starting Resume Enhancer...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run streamlit app
    try:
        # Determine the script path
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        
        # Use absolute path for reliability
        cmd = [sys.executable, "-m", "streamlit", "run", script_path, "--server.port=8501"]
        
        # Run the command
        print(f"Running command: {' '.join(cmd)}")
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    # Run the Streamlit app
    run_app() 