#!/bin/bash

# GitHub Repository Setup Script for DungeonBuilderServerSide
# This script helps set up the GitHub repository and push the initial code

set -e

echo "🚀 Setting up GitHub repository for DungeonBuilderServerSide..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI is not installed. You'll need to create the repository manually."
    echo "Please install GitHub CLI: https://cli.github.com/"
    echo ""
    echo "Or create the repository manually at: https://github.com/new"
    echo "Repository name: DungeonBuilderServerSide"
    echo "Description: Multiplayer Dungeon Builder Backend - Azure Functions with comprehensive testing"
    echo "Make it Public or Private as preferred"
    echo ""
    read -p "Press Enter after creating the repository..."
else
    echo "✅ GitHub CLI found. Creating repository..."
    
    # Create the repository using GitHub CLI
    gh repo create DungeonBuilderServerSide \
        --description "Multiplayer Dungeon Builder Backend - Azure Functions with comprehensive testing" \
        --public \
        --source=. \
        --remote=origin \
        --push
    
    echo "✅ Repository created and code pushed!"
fi

# Add remote if not already added
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Adding remote origin..."
    git remote add origin https://github.com/$(gh api user --jq .login)/DungeonBuilderServerSide.git
fi

# Check if we need to push
if [ "$(git rev-list --count HEAD)" -eq 1 ]; then
    echo "📤 Pushing initial commit..."
    git push -u origin main
else
    echo "📤 Pushing all commits..."
    git push -u origin main
fi

echo ""
echo "🎉 GitHub repository setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Visit: https://github.com/$(gh api user --jq .login)/DungeonBuilderServerSide"
echo "2. Set up GitHub Actions secrets:"
echo "   - AZURE_FUNCTIONAPP_PUBLISH_PROFILE (for deployment)"
echo "3. Enable GitHub Actions in the repository settings"
echo "4. Set up branch protection rules for main branch"
echo ""
echo "🔧 To enable automatic deployment later:"
echo "1. Uncomment the push trigger in .github/workflows/deploy.yml"
echo "2. Set up Azure Functions publish profile as a secret"
echo "3. Configure environment protection rules"
echo ""
echo "✅ Repository is ready for development!" 