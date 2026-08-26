#!/usr/bin/env python3
"""
TileGenie App Deployment Script
Deploys the custom Databricks App from the current folder
"""

import os
import sys
import subprocess

def check_prerequisites():
    """Check if we're in the right directory"""
    if not os.path.exists('app.yaml'):
        print("❌ Error: app.yaml not found")
        print("Please run this script from the TileGenie directory")
        sys.exit(1)
    
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found")
        sys.exit(1)
    
    print("✅ Prerequisites check passed")
    return True

def deploy_app():
    """Deploy the app using Databricks CLI"""
    print("\n🚀 TileGenie Deployment")
    print("=" * 50)
    print(f"Deploying from: {os.getcwd()}")
    print()
    
    # Check prerequisites
    check_prerequisites()
    
    # Deploy command
    print("📦 Running deployment...\n")
    cmd = ["databricks", "apps", "deploy", "tilegenie", "--source-code-path", "."]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        print("\n" + "=" * 50)
        print("✅ Deployment successful!")
        print("\nNext steps:")
        print("1. Go to the 'Apps' page in your Databricks workspace")
        print("2. Find 'tilegenie' in the list")
        print("3. Click to open your app!")
        print("\n🎉 TileGenie is ready to use!")
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Deployment failed!")
        print(f"\nError: {e.stderr}")
        print("\nCommon fixes:")
        print("- Run: databricks configure --token (to authenticate)")
        print("- Make sure you're in the TileGenie folder")
        print("- Verify app.yaml has the correct Genie Space ID")
        return False
    except FileNotFoundError:
        print("❌ Error: Databricks CLI not found")
        print("Install it with: pip install databricks-cli")
        return False

if __name__ == "__main__":
    success = deploy_app()
    sys.exit(0 if success else 1)