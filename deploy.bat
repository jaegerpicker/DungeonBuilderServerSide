@echo off
REM Dungeon Builder Backend - Serverless Framework Deployment Script (Windows)
REM This script automates the deployment using Serverless Framework

setlocal enabledelayedexpansion

REM Default values
set STAGE=%1
set REGION=%2
set JWT_SECRET=%3

REM Set defaults if not provided
if "%STAGE%"=="" set STAGE=dev
if "%REGION%"=="" set REGION=eastus

REM Validate inputs
if "%JWT_SECRET%"=="" (
    echo [ERROR] JWT_SECRET is required as the third parameter
    echo Usage: %0 [stage] [region] [jwt_secret]
    echo Example: %0 prod eastus my-super-secret-jwt-key
    exit /b 1
)

echo ================================
echo Dungeon Builder Backend Deployment
echo ================================
echo [INFO] Stage: %STAGE%
echo [INFO] Region: %REGION%
echo [INFO] Starting deployment...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed. Please install npm.
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed. Please install Python 3.9+
    exit /b 1
)

REM Check if Azure CLI is installed
az --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    exit /b 1
)

REM Check if user is logged in to Azure
echo [INFO] Checking Azure login status...
az account show >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Not logged in to Azure. Please log in...
    az login
)

REM Install dependencies
echo [INFO] Installing Node.js dependencies...
call npm install

echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Install Serverless Framework plugins
echo [INFO] Installing Serverless Framework plugins...
call npx serverless plugin install -n serverless-azure-functions
call npx serverless plugin install -n serverless-python-requirements

REM Store secrets in Azure Key Vault (if not exists)
echo [INFO] Setting up Azure Key Vault for secrets...
set RESOURCE_GROUP=%STAGE%-dungeon-builder-rg
set KEY_VAULT_NAME=dungeon-builder-kv-%STAGE%

REM Create resource group if it doesn't exist
az group show --name "%RESOURCE_GROUP%" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Creating resource group: %RESOURCE_GROUP%
    az group create --name "%RESOURCE_GROUP%" --location "%REGION%"
)

REM Create Key Vault if it doesn't exist
az keyvault show --name "%KEY_VAULT_NAME%" --resource-group "%RESOURCE_GROUP%" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Creating Key Vault: %KEY_VAULT_NAME%
    az keyvault create --name "%KEY_VAULT_NAME%" --resource-group "%RESOURCE_GROUP%" --location "%REGION%" --sku standard
)

REM Store JWT secret in Key Vault
echo [INFO] Storing JWT secret in Key Vault...
az keyvault secret set --vault-name "%KEY_VAULT_NAME%" --name "jwt-secret" --value "%JWT_SECRET%"

REM Create Cosmos DB account if it doesn't exist
set COSMOS_ACCOUNT_NAME=dungeon-builder-cosmos-%STAGE%
az cosmosdb show --name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Creating Cosmos DB account: %COSMOS_ACCOUNT_NAME%
    az cosmosdb create --name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --capabilities EnableServerless
)

REM Get Cosmos DB connection details
echo [INFO] Getting Cosmos DB connection details...
for /f "tokens=*" %%i in ('az cosmosdb show --name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --query documentEndpoint -o tsv') do set COSMOS_ENDPOINT=%%i
for /f "tokens=*" %%i in ('az cosmosdb keys list --name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --query primaryMasterKey -o tsv') do set COSMOS_KEY=%%i

REM Store Cosmos DB secrets in Key Vault
echo [INFO] Storing Cosmos DB secrets in Key Vault...
az keyvault secret set --vault-name "%KEY_VAULT_NAME%" --name "cosmos-endpoint" --value "%COSMOS_ENDPOINT%"
az keyvault secret set --vault-name "%KEY_VAULT_NAME%" --name "cosmos-key" --value "%COSMOS_KEY%"

REM Create Cosmos DB database and containers
echo [INFO] Setting up Cosmos DB database and containers...
az cosmosdb sql database create --account-name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --name "DungeonBuilderDB" >nul 2>&1 || echo [WARNING] Database already exists

REM Create containers
echo [INFO] Creating containers...
az cosmosdb sql container create --account-name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --database-name "DungeonBuilderDB" --name "users" --partition-key-path "/partitionKey" --throughput 400 >nul 2>&1 || echo [WARNING] Container users already exists
az cosmosdb sql container create --account-name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --database-name "DungeonBuilderDB" --name "dungeons" --partition-key-path "/partitionKey" --throughput 400 >nul 2>&1 || echo [WARNING] Container dungeons already exists
az cosmosdb sql container create --account-name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --database-name "DungeonBuilderDB" --name "guilds" --partition-key-path "/partitionKey" --throughput 400 >nul 2>&1 || echo [WARNING] Container guilds already exists
az cosmosdb sql container create --account-name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --database-name "DungeonBuilderDB" --name "lobbies" --partition-key-path "/partitionKey" --throughput 400 >nul 2>&1 || echo [WARNING] Container lobbies already exists
az cosmosdb sql container create --account-name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --database-name "DungeonBuilderDB" --name "friendships" --partition-key-path "/partitionKey" --throughput 400 >nul 2>&1 || echo [WARNING] Container friendships already exists
az cosmosdb sql container create --account-name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --database-name "DungeonBuilderDB" --name "ratings" --partition-key-path "/partitionKey" --throughput 400 >nul 2>&1 || echo [WARNING] Container ratings already exists
az cosmosdb sql container create --account-name "%COSMOS_ACCOUNT_NAME%" --resource-group "%RESOURCE_GROUP%" --database-name "DungeonBuilderDB" --name "leaderboard" --partition-key-path "/partitionKey" --throughput 400 >nul 2>&1 || echo [WARNING] Container leaderboard already exists

REM Deploy using Serverless Framework
echo [INFO] Deploying with Serverless Framework...
call npx serverless deploy --stage "%STAGE%" --region "%REGION%"

REM Get deployment info
echo [INFO] Getting deployment information...
call npx serverless info --stage "%STAGE%"

echo ================================
echo Deployment Completed Successfully!
echo ================================
echo [INFO] Stage: %STAGE%
echo [INFO] Region: %REGION%
echo [INFO] Resource Group: %RESOURCE_GROUP%
echo [INFO] Key Vault: %KEY_VAULT_NAME%
echo [INFO] Cosmos DB: %COSMOS_ACCOUNT_NAME%
echo [INFO] Function App: dungeon-builder-backend-%STAGE%

REM Display endpoints
echo [INFO] API Endpoints:
echo   Health Check: https://dungeon-builder-backend-%STAGE%.azurewebsites.net/api/health
echo   API Base URL: https://dungeon-builder-backend-%STAGE%.azurewebsites.net/api

echo [INFO] To test the deployment, run:
echo   npm run test:local https://dungeon-builder-backend-%STAGE%.azurewebsites.net

echo [INFO] To remove the deployment, run:
echo   npx serverless remove --stage %STAGE%

pause 