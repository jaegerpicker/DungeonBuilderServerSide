#!/bin/bash

# Dungeon Builder Backend - Development Setup Script
# This script sets up the development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_header "Dungeon Builder Backend Setup"
print_status "Setting up development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+ from https://python.org/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_warning "Azure CLI is not installed. You'll need it for deployment."
    print_status "Install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
fi

# Check if Azure Functions Core Tools is installed
if ! command -v func &> /dev/null; then
    print_warning "Azure Functions Core Tools is not installed. You'll need it for local development."
    print_status "Install it with: npm install -g azure-functions-core-tools@4 --unsafe-perm true"
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

# Install Serverless Framework plugins
print_status "Installing Serverless Framework plugins..."
npx serverless plugin install -n serverless-azure-functions
npx serverless plugin install -n serverless-python-requirements

# Create local.settings.json if it doesn't exist
if [ ! -f "local.settings.json" ]; then
    print_status "Creating local.settings.json template..."
    cat > local.settings.json << EOF
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_DB_ENDPOINT": "your_cosmos_db_endpoint_here",
    "COSMOS_DB_KEY": "your_cosmos_db_key_here",
    "COSMOS_DB_DATABASE": "DungeonBuilderDB",
    "JWT_SECRET": "your_jwt_secret_key_here",
    "JWT_ALGORITHM": "HS256",
    "JWT_EXPIRATION_MINUTES": "60"
  }
}
EOF
    print_warning "Please update local.settings.json with your Azure Cosmos DB credentials"
fi

# Make deployment scripts executable
chmod +x deploy.sh
chmod +x setup.sh

print_header "Setup Completed Successfully!"
print_status "Development environment is ready!"

print_status "Next steps:"
echo "  1. Update local.settings.json with your Azure Cosmos DB credentials"
echo "  2. Run 'func start' to start local development server"
echo "  3. Run './deploy.sh dev eastus your-jwt-secret' to deploy to Azure"
echo "  4. Run 'python test_api.py' to test the API endpoints"

print_status "Useful commands:"
echo "  npm run deploy:prod    - Deploy to production"
echo "  npm run test           - Test API endpoints"
echo "  npm run logs           - View function logs"
echo "  func start             - Start local development server" 