#!/usr/bin/env python3
"""
Setup script for SEO Content Generator

This script helps set up the environment and install dependencies
for the SEO Content Generator application.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_virtual_environment():
    """Create a virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def activate_virtual_environment():
    """Activate the virtual environment"""
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "source venv/bin/activate"
    
    print(f"📝 To activate the virtual environment, run: {activate_script}")
    return True

def install_dependencies():
    """Install required dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def download_spacy_model():
    """Download the required spaCy model"""
    return run_command("python -m spacy download en_core_web_sm", "Downloading spaCy model")

def create_env_file():
    """Create environment configuration file"""
    if os.path.exists(".env"):
        print("✅ Environment file already exists")
        return True
    
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Security
SECRET_KEY=your_secret_key_here_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./seo_writer.db

# App Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Environment file created (.env)")
        print("⚠️  Please edit .env and add your OpenAI API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 SEO Content Generator Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Download spaCy model
    if not download_spacy_model():
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        sys.exit(1)
    
    # Instructions
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run the application:")
    print("   python main.py")
    print("\n🌐 The application will be available at: http://localhost:8000")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()

