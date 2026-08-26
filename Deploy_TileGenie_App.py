# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Install Databricks SDK
# MAGIC %pip install --upgrade databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Deploy TileGenie App
from databricks.sdk import WorkspaceClient
import time

# Initialize the Databricks client (uses current workspace authentication)
w = WorkspaceClient()

print("🚀 TileGenie App Deployment")
print("=" * 70)
print()

# App configuration
app_name = "tilegenie"
source_code_path = "/Users/ashish@lucentinnovation.com/TileGenie"
genie_space_id = "01f1a166e5891c2d89a0256412e7d452"

print(f"📦 App Name: {app_name}")
print(f"📂 Source Path: {source_code_path}")
print(f"🤖 Genie Space: {genie_space_id}")
print()

try:
    print("🔍 Checking if app exists...")
    
    # Check if app already exists
    existing_apps = list(w.apps.list())
    app_exists = any(app.name == app_name for app in existing_apps)
    
    if app_exists:
        print(f"⚠️  App '{app_name}' already exists - will update it")
        print()
    else:
        print(f"✨ Creating new app '{app_name}'")
        print()
    
    # Deploy the app using the modern deploy method
    print("🚀 Deploying app from workspace folder...")
    print("   This may take 2-3 minutes...")
    print()
    
    # Use the Apps API deploy method
    # This will create or update the app based on the source code path
    from databricks.sdk.service.apps import App, AppDeployment, AppResource, AppResourceJob, AppResourceSqlWarehouse, AppResourceServingEndpoint
    
    # Create app deployment configuration
    deployment = w.apps.deploy(
        app_name=app_name,
        source_code_path=source_code_path,
        mode="SNAPSHOT"  # Deploy from current snapshot of the folder
    )
    
    print(f"✅ Deployment initiated successfully!")
    print(f"📍 App Name: {deployment.deployment_id}")
    print()
    
    # Wait for deployment to complete
    print("⏳ Waiting for deployment to complete...")
    
    # Poll deployment status
    max_wait = 300  # 5 minutes max
    start_time = time.time()
    
    while (time.time() - start_time) < max_wait:
        try:
            # Get the app details
            app = w.apps.get(name=app_name)
            
            if app.status and app.status.state:
                state = app.status.state.value if hasattr(app.status.state, 'value') else str(app.status.state)
                print(f"   Current state: {state}")
                
                if state in ["RUNNING", "SUCCEEDED"]:
                    print()
                    print("=" * 70)
                    print("🎉 Deployment Complete!")
                    print()
                    print(f"✅ App '{app_name}' is now running!")
                    
                    if app.url:
                        print(f"🌐 App URL: {app.url}")
                    
                    print()
                    print("Next steps:")
                    print("1. Click the URL above to open your app")
                    print("2. Test the 4 core CEO questions:")
                    print("   - Why was production reduced yesterday?")
                    print("   - What is the expected production of Porcelain-Glossy-24x24 for next quarter?")
                    print("   - What should our production plan be for Q4 2026?")
                    print("   - How much stock do we have in each warehouse?")
                    print()
                    print("🏆 Ready for the Databricks Community Contest!")
                    break
                    
                elif state in ["FAILED", "ERROR"]:
                    print()
                    print("❌ Deployment failed!")
                    if app.status.message:
                        print(f"Error: {app.status.message}")
                    break
            
            time.sleep(10)  # Wait 10 seconds before checking again
            
        except Exception as e:
            print(f"   Status check: {str(e)[:100]}")
            time.sleep(10)
    
    if (time.time() - start_time) >= max_wait:
        print()
        print("⏰ Deployment is taking longer than expected")
        print("Check the Apps page in your workspace for status")
        print(f"App name: {app_name}")
    
except Exception as e:
    print("=" * 70)
    print("❌ Deployment Error")
    print()
    print(f"Error: {str(e)}")
    print()
    print("💡 Alternative: Deploy via UI")
    print("1. Go to 'Apps' in the sidebar")
    print("2. Click 'Create custom app'")
    print(f"3. Source Code Path: {source_code_path}")
    print("4. App Name: tilegenie")
    print("5. Click 'Create'")

# COMMAND ----------

# DBTITLE 1,🎯 Quick Git Setup for Deployment
# MAGIC %md
# MAGIC # 🚀 TileGenie Git Deployment Guide
# MAGIC
# MAGIC The Databricks Apps UI requires a **Git repository URL**. Here's the 5-minute setup:
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 📋 Steps to Deploy
# MAGIC
# MAGIC ### Step 1: Create GitHub Repository (2 minutes)
# MAGIC
# MAGIC 1. Go to https://github.com/new
# MAGIC 2. Repository name: `tilegenie`
# MAGIC 3. Description: `Genie-powered tile manufacturing intelligence for Databricks Community Contest`
# MAGIC 4. ✅ Make it **Public** (required for contest submission)
# MAGIC 5. ❌ Don't initialize with README (we already have files)
# MAGIC 6. Click **"Create repository"**
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Step 2: Push Your Code (Run the cell below)
# MAGIC
# MAGIC The next cell will:
# MAGIC - Initialize Git in your TileGenie folder
# MAGIC - Add all your files
# MAGIC - Push to GitHub
# MAGIC
# MAGIC **Before running:** Update the `GITHUB_USERNAME` variable in the cell below!
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Step 3: Deploy in Databricks UI (1 minute)
# MAGIC
# MAGIC 1. Go to **"Apps"** in the sidebar
# MAGIC 2. Click **"Create custom app"**
# MAGIC 3. Enter your Git URL: `https://github.com/YOUR_USERNAME/tilegenie.git`
# MAGIC 4. Click **"Create"**
# MAGIC 5. Wait 2-3 minutes for deployment
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## ✅ Your Files (Already Perfect!)
# MAGIC
# MAGIC ```
# MAGIC TileGenie/
# MAGIC ├── app.py              ✅ Main Streamlit app
# MAGIC ├── app.yaml            ✅ App config (Genie Space ID: 01f1a166e5891c2d89a0256412e7d452)
# MAGIC ├── requirements.txt    ✅ Dependencies
# MAGIC ├── README.md           ✅ Documentation
# MAGIC └── scripts/
# MAGIC     └── generate_tile_production_data.py ✅ Data generator
# MAGIC ```
# MAGIC
# MAGIC All files are ready! Just push to Git and deploy. 🎉

# COMMAND ----------

# DBTITLE 1,📦 Push TileGenie to GitHub
# ========================================
# UPDATE THIS WITH YOUR GITHUB USERNAME!
# ========================================
GITHUB_USERNAME = "YOUR_GITHUB_USERNAME"  # <-- CHANGE THIS!

# ========================================
# Then run this cell
# ========================================

import subprocess
import os

print("🚀 TileGenie Git Setup")
print("=" * 70)
print()

# Validate username
if GITHUB_USERNAME == "YOUR_GITHUB_USERNAME":
    print("❌ ERROR: Please update GITHUB_USERNAME in the cell above!")
    print("   Change 'YOUR_GITHUB_USERNAME' to your actual GitHub username")
    print()
    print("📌 Example: GITHUB_USERNAME = 'ashish123'")
    raise ValueError("GitHub username not set")

# Navigate to TileGenie folder
os.chdir("/Workspace/Users/ashish@lucentinnovation.com/TileGenie")
print(f"📂 Working directory: {os.getcwd()}")
print()

# Initialize Git
print("🎯 Step 1: Initializing Git...")
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "config", "user.name", "TileGenie Contest"], check=True)
subprocess.run(["git", "config", "user.email", "tilegenie@contest.com"], check=True)
print("✅ Git initialized")
print()

# Add all files
print("📦 Step 2: Adding files...")
subprocess.run(["git", "add", "."], check=True)
print("✅ Files staged")
print()

# Commit
print("📝 Step 3: Creating commit...")
subprocess.run([
    "git", "commit", "-m", 
    "Initial TileGenie app for Databricks Community Contest"
], check=True)
print("✅ Commit created")
print()

# Add remote
print("🌐 Step 4: Adding GitHub remote...")
remote_url = f"https://github.com/{GITHUB_USERNAME}/tilegenie.git"
subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
subprocess.run(["git", "branch", "-M", "main"], check=True)
print(f"✅ Remote added: {remote_url}")
print()

# Push (requires authentication)
print("🚀 Step 5: Pushing to GitHub...")
print("   ⚠️  You may be prompted for GitHub credentials")
print("   Use a Personal Access Token (not password)")
print("   Create one at: https://github.com/settings/tokens")
print()

try:
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    print()
    print("=" * 70)
    print("🎉 SUCCESS! Your code is on GitHub!")
    print()
    print(f"🔗 Repository URL: {remote_url}")
    print()
    print("👉 Next Steps:")
    print("1. Go to 'Apps' in Databricks sidebar")
    print("2. Click 'Create custom app'")
    print(f"3. Enter Git URL: {remote_url}")
    print("4. Click 'Create' and wait 2-3 minutes")
    print()
    print("🏆 You're ready to deploy!")
    
except subprocess.CalledProcessError as e:
    print()
    print("❌ Push failed! This usually means authentication is needed.")
    print()
    print("🔑 Setup GitHub Authentication:")
    print("1. Create a Personal Access Token at:")
    print("   https://github.com/settings/tokens/new")
    print("   (Give it 'repo' permissions)")
    print()
    print("2. Use this token as your password when prompted")
    print()
    print("💡 Or use the GitHub CLI: gh auth login")

# COMMAND ----------

# DBTITLE 1,🚨 Alternative: Manual GitHub Upload
# MAGIC %md
# MAGIC # 🚨 If Git Push Fails: Manual Upload Method
# MAGIC
# MAGIC If the automated Git push doesn't work (authentication issues), here's the **manual method** (5 minutes):
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 📎 Step-by-Step Manual Upload
# MAGIC
# MAGIC ### 1. Download Your Files
# MAGIC
# MAGIC In Databricks:
# MAGIC 1. Go to **Workspace** → **Users** → `ashish@lucentinnovation.com` → **TileGenie**
# MAGIC 2. Download these files to your computer:
# MAGIC    - `app.py`
# MAGIC    - `app.yaml`
# MAGIC    - `requirements.txt`
# MAGIC    - `README.md`
# MAGIC    - `scripts/generate_tile_production_data.py`
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 2. Create GitHub Repository
# MAGIC
# MAGIC 1. Go to https://github.com/new
# MAGIC 2. Name: `tilegenie`
# MAGIC 3. **Public** repository
# MAGIC 4. Click **"Create repository"**
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 3. Upload Files to GitHub
# MAGIC
# MAGIC 1. On the new repository page, click **"uploading an existing file"**
# MAGIC 2. Drag and drop all 5 files
# MAGIC 3. Commit message: `"Initial TileGenie app for Databricks Contest"`
# MAGIC 4. Click **"Commit changes"**
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 4. Deploy in Databricks
# MAGIC
# MAGIC 1. Copy your repository URL: `https://github.com/YOUR_USERNAME/tilegenie`
# MAGIC 2. In Databricks, go to **"Apps"** → **"Create custom app"**
# MAGIC 3. Paste the Git URL
# MAGIC 4. Click **"Create"**
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## ✅ Verification Checklist
# MAGIC
# MAGIC Before deploying, make sure:
# MAGIC - ☑️ All 5 files are in GitHub
# MAGIC - ☑️ `app.yaml` has Genie Space ID: `01f1a166e5891c2d89a0256412e7d452`
# MAGIC - ☑️ Repository is **Public**
# MAGIC - ☑️ README.md is visible (good for contest judges!)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 🏆 Contest Submission Bonus
# MAGIC
# MAGIC Your GitHub repo will be part of your contest submission! Make sure:
# MAGIC - ✅ Repository name is clear: `tilegenie`
# MAGIC - ✅ README has a good description
# MAGIC - ✅ Code is well-commented
# MAGIC
# MAGIC Judges can review your code on GitHub! 👀