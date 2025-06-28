#!/bin/bash

# Dungeon Builder Backend - Serverless Framework Deployment Script
# This script automates the deployment using Serverless Framework

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

# Default values
STAGE=${1:-dev}
REGION=${2:-eastus}
JWT_SECRET=${3:-}

# Validate inputs
if [ -z "$JWT_SECRET" ]; then
    print_error "JWT_SECRET is required as the third parameter"
    echo "Usage: $0 [stage] [region] [jwt_secret]"
    echo "Example: $0 prod eastus my-super-secret-jwt-key"
    exit 1
fi

print_header "Dungeon Builder Backend Deployment"
print_status "Stage: $STAGE"
print_status "Region: $REGION"
print_status "Starting deployment..."

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

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in to Azure
print_status "Checking Azure login status..."
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure. Please log in..."
    az login
fi

# Install dependencies
print_status "Installing Node.js dependencies..."
npm install

print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install Serverless Framework plugins
print_status "Installing Serverless Framework plugins..."
npx serverless plugin install -n serverless-azure-functions
npx serverless plugin install -n serverless-python-requirements

# Store secrets in Azure Key Vault (if not exists)
print_status "Setting up Azure Key Vault for secrets..."
RESOURCE_GROUP="${STAGE}-dungeon-builder-rg"
KEY_VAULT_NAME="dungeon-builder-kv-${STAGE}"

# Create resource group if it doesn't exist
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    print_status "Creating resource group: $RESOURCE_GROUP"
    az group create --name "$RESOURCE_GROUP" --location "$REGION"
fi

# Create Key Vault if it doesn't exist
if ! az keyvault show --name "$KEY_VAULT_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_status "Creating Key Vault: $KEY_VAULT_NAME"
    az keyvault create --name "$KEY_VAULT_NAME" --resource-group "$RESOURCE_GROUP" --location "$REGION" --sku standard
fi

# Store JWT secret in Key Vault
print_status "Storing JWT secret in Key Vault..."
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "jwt-secret" --value "$JWT_SECRET"

# Create Cosmos DB account if it doesn't exist
COSMOS_ACCOUNT_NAME="dungeon-builder-cosmos-${STAGE}"
if ! az cosmosdb show --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_status "Creating Cosmos DB account: $COSMOS_ACCOUNT_NAME"
    az cosmosdb create --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --capabilities EnableServerless
fi

# Get Cosmos DB connection details
print_status "Getting Cosmos DB connection details..."
COSMOS_ENDPOINT=$(az cosmosdb show --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --query documentEndpoint -o tsv)
COSMOS_KEY=$(az cosmosdb keys list --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --query primaryMasterKey -o tsv)

# Store Cosmos DB secrets in Key Vault
print_status "Storing Cosmos DB secrets in Key Vault..."
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "cosmos-endpoint" --value "$COSMOS_ENDPOINT"
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "cosmos-key" --value "$COSMOS_KEY"

# Create Cosmos DB database and containers
print_status "Setting up Cosmos DB database and containers..."
az cosmosdb sql database create --account-name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --name "DungeonBuilderDB" 2>/dev/null || print_warning "Database already exists"

# Create containers
CONTAINERS=("users" "dungeons" "guilds" "lobbies" "friendships" "ratings" "leaderboard")
for container in "${CONTAINERS[@]}"; do
    print_status "Creating container: $container"
    az cosmosdb sql container create \
        --account-name "$COSMOS_ACCOUNT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --database-name "DungeonBuilderDB" \
        --name "$container" \
        --partition-key-path "/partitionKey" \
        --throughput 400 2>/dev/null || print_warning "Container $container already exists"
done

# Deploy using Serverless Framework
print_status "Deploying with Serverless Framework..."
npx serverless deploy --stage "$STAGE" --region "$REGION"

# Get deployment info
print_status "Getting deployment information..."
npx serverless info --stage "$STAGE"

print_header "Deployment Completed Successfully!"
print_status "Stage: $STAGE"
print_status "Region: $REGION"
print_status "Resource Group: $RESOURCE_GROUP"
print_status "Key Vault: $KEY_VAULT_NAME"
print_status "Cosmos DB: $COSMOS_ACCOUNT_NAME"
print_status "Function App: dungeon-builder-backend-$STAGE"

# Display endpoints
print_status "API Endpoints:"
echo "  Health Check: https://dungeon-builder-backend-$STAGE.azurewebsites.net/api/health"
echo "  API Base URL: https://dungeon-builder-backend-$STAGE.azurewebsites.net/api"

print_status "To test the deployment, run:"
echo "  npm run test:local https://dungeon-builder-backend-$STAGE.azurewebsites.net"

print_status "To remove the deployment, run:"
echo "  npx serverless remove --stage $STAGE" 