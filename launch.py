#!/usr/bin/env python3
"""
Launch script for Resume Enhancer
Provides options to install regular or enhanced dependencies
"""

import os
import sys
import subprocess
import time

def clear_screen():
    """Clear the terminal screen based on OS"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════╗
    ║                 RESUME ENHANCER                   ║
    ║         AI-powered resume improvement tool        ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(banner)

def print_menu():
    """Print the main menu options"""
    print("\nPlease select an option:")
    print("1. Run with basic features")
    print("2. Install enhanced NLP dependencies and run")
    print("3. Exit")
    return input("\nEnter your choice (1-3): ")

def install_enhanced_dependencies():
    """Install optional dependencies for enhanced NLP features"""
    print("\nInstalling enhanced NLP dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "transformers==4.30.2", 
            "torch==2.0.1"
        ])
        print("\n✅ Enhanced dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("\n❌ Failed to install enhanced dependencies.")
        print("You can try installing them manually with:")
        print("pip install transformers torch")
        input("\nPress Enter to continue...")
        return False
    return True

def run_app():
    """Run the main application"""
    print("\nStarting Resume Enhancer...")
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_app.py")
        subprocess.check_call([sys.executable, script_path])
    except subprocess.CalledProcessError:
        print("\n❌ Failed to start the application.")
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")

def main():
    """Main function to display menu and handle user choice"""
    while True:
        clear_screen()
        print_banner()
        choice = print_menu()
        
        if choice == '1':
            run_app()
        elif choice == '2':
            if install_enhanced_dependencies():
                run_app()
        elif choice == '3':
            print("\nExiting Resume Enhancer. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(2)

if __name__ == "__main__":
    main() 