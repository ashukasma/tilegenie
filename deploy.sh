#!/bin/bash
# TileGenie Deployment Script
# Deploy custom Databricks App from existing folder

echo "🚀 TileGenie Deployment"
echo "========================"
echo ""

# Check if we're in the right directory
if [ ! -f "app.yaml" ]; then
    echo "❌ Error: app.yaml not found. Run this from /TileGenie directory"
    exit 1
fi

echo "📦 Deploying TileGenie from current folder..."
echo "Folder: $(pwd)"
echo ""

# Deploy using databricks apps deploy
# This command will create the app if it doesn't exist, or update it if it does
databricks apps deploy tilegenie --source-code-path .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "Next steps:"
    echo "1. Go to the 'Apps' page in your Databricks workspace"
    echo "2. Find 'tilegenie' in the list"
    echo "3. Click to open and start using it!"
    echo ""
    echo "🎉 Your TileGenie app is ready!"
else
    echo ""
    echo "❌ Deployment failed. Check the error above."
    echo ""
    echo "Common fixes:"
    echo "- Run: databricks configure --token (to set up authentication)"
    echo "- Make sure you're in the TileGenie folder"
    echo "- Check that app.yaml has the correct Genie Space ID"
    exit 1
fi