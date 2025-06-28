@echo off
REM Dungeon Builder Backend - Development Setup Script (Windows)
REM This script sets up the development environment

setlocal enabledelayedexpansion

echo ================================
echo Dungeon Builder Backend Setup
echo ================================
echo [INFO] Setting up development environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed. Please install Python 3.9+ from https://python.org/
    exit /b 1
)

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

REM Check if Azure CLI is installed
az --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Azure CLI is not installed. You'll need it for deployment.
    echo [INFO] Install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
)

REM Check if Azure Functions Core Tools is installed
func --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Azure Functions Core Tools is not installed. You'll need it for local development.
    echo [INFO] Install it with: npm install -g azure-functions-core-tools@4 --unsafe-perm true
)

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
call npm install

REM Install Serverless Framework plugins
echo [INFO] Installing Serverless Framework plugins...
call npx serverless plugin install -n serverless-azure-functions
call npx serverless plugin install -n serverless-python-requirements

REM Create local.settings.json if it doesn't exist
if not exist "local.settings.json" (
    echo [INFO] Creating local.settings.json template...
    (
        echo {
        echo   "IsEncrypted": false,
        echo   "Values": {
        echo     "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        echo     "FUNCTIONS_WORKER_RUNTIME": "python",
        echo     "COSMOS_DB_ENDPOINT": "your_cosmos_db_endpoint_here",
        echo     "COSMOS_DB_KEY": "your_cosmos_db_key_here",
        echo     "COSMOS_DB_DATABASE": "DungeonBuilderDB",
        echo     "JWT_SECRET": "your_jwt_secret_key_here",
        echo     "JWT_ALGORITHM": "HS256",
        echo     "JWT_EXPIRATION_MINUTES": "60"
        echo   }
        echo }
    ) > local.settings.json
    echo [WARNING] Please update local.settings.json with your Azure Cosmos DB credentials
)

echo ================================
echo Setup Completed Successfully!
echo ================================
echo [INFO] Development environment is ready!

echo [INFO] Next steps:
echo   1. Update local.settings.json with your Azure Cosmos DB credentials
echo   2. Run 'func start' to start local development server
echo   3. Run 'deploy.bat dev eastus your-jwt-secret' to deploy to Azure
echo   4. Run 'python test_api.py' to test the API endpoints

echo [INFO] Useful commands:
echo   npm run deploy:prod    - Deploy to production
echo   npm run test           - Test API endpoints
echo   npm run logs           - View function logs
echo   func start             - Start local development server

pause 