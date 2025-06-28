# Dungeon Builder Backend Deployment Script
# This script automates the deployment of the Azure Functions app

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$FunctionAppName,
    
    [Parameter(Mandatory=$true)]
    [string]$CosmosDbAccountName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$true)]
    [string]$JwtSecret
)

Write-Host "Starting deployment of Dungeon Builder Backend..." -ForegroundColor Green

# Check if Azure CLI is installed
try {
    az version | Out-Null
} catch {
    Write-Error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Check if user is logged in
try {
    az account show | Out-Null
} catch {
    Write-Host "Please log in to Azure..." -ForegroundColor Yellow
    az login
}

# Create resource group
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create Cosmos DB account
Write-Host "Creating Cosmos DB account..." -ForegroundColor Yellow
az cosmosdb create --name $CosmosDbAccountName --resource-group $ResourceGroupName --capabilities EnableServerless

# Get Cosmos DB connection details
Write-Host "Getting Cosmos DB connection details..." -ForegroundColor Yellow
$cosmosEndpoint = az cosmosdb show --name $CosmosDbAccountName --resource-group $ResourceGroupName --query documentEndpoint -o tsv
$cosmosKey = az cosmosdb keys list --name $CosmosDbAccountName --resource-group $ResourceGroupName --query primaryMasterKey -o tsv

# Create Function App
Write-Host "Creating Function App..." -ForegroundColor Yellow
az functionapp create --name $FunctionAppName --resource-group $ResourceGroupName --consumption-plan-location $Location --runtime python --runtime-version 3.9 --functions-version 4 --storage-account (az storage account create --name ($FunctionAppName + "storage") --resource-group $ResourceGroupName --location $Location --sku Standard_LRS --query name -o tsv)

# Configure Function App settings
Write-Host "Configuring Function App settings..." -ForegroundColor Yellow
az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings `
    COSMOS_DB_ENDPOINT=$cosmosEndpoint `
    COSMOS_DB_KEY=$cosmosKey `
    COSMOS_DB_DATABASE="DungeonBuilderDB" `
    JWT_SECRET=$JwtSecret `
    JWT_ALGORITHM="HS256" `
    JWT_EXPIRATION_MINUTES="60"

# Create Cosmos DB database and containers
Write-Host "Creating Cosmos DB database and containers..." -ForegroundColor Yellow
az cosmosdb sql database create --account-name $CosmosDbAccountName --resource-group $ResourceGroupName --name "DungeonBuilderDB"

# Create containers with appropriate partition keys
$containers = @(
    @{Name="users"; PartitionKey="/partitionKey"},
    @{Name="dungeons"; PartitionKey="/partitionKey"},
    @{Name="guilds"; PartitionKey="/partitionKey"},
    @{Name="lobbies"; PartitionKey="/partitionKey"},
    @{Name="friendships"; PartitionKey="/partitionKey"},
    @{Name="ratings"; PartitionKey="/partitionKey"},
    @{Name="leaderboard"; PartitionKey="/partitionKey"}
)

foreach ($container in $containers) {
    az cosmosdb sql container create --account-name $CosmosDbAccountName --resource-group $ResourceGroupName --database-name "DungeonBuilderDB" --name $container.Name --partition-key-path $container.PartitionKey --throughput 400
}

# Deploy the function app
Write-Host "Deploying Function App..." -ForegroundColor Yellow
func azure functionapp publish $FunctionAppName

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Function App URL: https://$FunctionAppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Cosmos DB Endpoint: $cosmosEndpoint" -ForegroundColor Cyan 