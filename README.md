# DungeonBuilderServerSide

A multiplayer dungeon builder backend built with Azure Functions and Python, featuring comprehensive testing and CI/CD pipeline.

## 🏗️ Architecture

- **Backend**: Azure Functions with Python 3.10
- **Database**: Azure Cosmos DB
- **Authentication**: JWT-based with bcrypt password hashing
- **Testing**: pytest with 91.94% code coverage
- **CI/CD**: GitHub Actions with automated testing and deployment

## 🚀 Features

### Core Services

- **User Management**: Registration, authentication, profile management
- **Dungeon Builder**: Create, edit, and share custom dungeons
- **Multiplayer Lobbies**: Real-time lobby management for dungeon runs
- **Guild System**: Team-based features and guild management
- **Friendship System**: Social features with friend requests and blocking
- **Leaderboards**: Global and dungeon-specific rankings

### Technical Features

- **Comprehensive Testing**: 267 tests with 91.94% coverage
- **Data Validation**: Pydantic models for type safety
- **Error Handling**: Robust error handling and logging
- **Scalable Architecture**: Serverless design for automatic scaling

## 📊 Test Coverage

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
auth/__init__.py                     60     17    72%   39-47, 55, 64, 87-89, 97, 105, 113, 124-126, 134
dungeons/__init__.py                131     25    81%   30, 44, 59, 63, 76, 78, 97, 117-119, 127, 157-159, 167, 195-197, 205, 238-246, 254
friends/__init__.py                 168     49    71%   30, 37-38, 49-51, 59, 63, 80, 91-93, 101, 118, 129-131, 139, 159-161, 169, 189-191, 199, 219-221, 229, 246, 257-259, 267, 288-296, 304, 321, 332-334, 342, 367-369
guilds/__init__.py                  145     33    77%   30, 44, 59, 63, 73, 75, 94, 114-116, 124, 137-139, 147, 175, 186-188, 196, 215, 226-228, 236, 255, 266-268, 276, 303-305
health/__init__.py                   14      4    71%   30-36, 44
leaderboard/__init__.py             157     37    76%   34-36, 44, 48, 71, 91-93, 101, 121-123, 131, 151-153, 161, 181-183, 191, 204-206, 214, 227-229, 237, 274-276, 284, 322-324
lobbies/__init__.py                 208     60    71%   30, 37-38, 49-51, 59, 63, 72, 91, 111-113, 121, 141, 152-154, 162, 179, 190-192, 200, 217, 228-230, 238, 245, 255, 266-268, 276, 283, 293, 304-306, 314, 345-353, 361, 381-383, 391, 408, 419-421, 429, 446, 457-459
models/__init__.py                    7      0   100%
services/__init__.py                  9      0   100%
services/auth.py                     53      2    96%   67, 77
services/database.py                 51      9    82%   37-38, 44, 55-56, 61, 66-68
services/dungeon_service.py          78      0   100%
services/friendship_service.py       89     32    64%   65, 80-87, 91-96, 106, 118-134, 138-142, 146-150, 154-155, 183
services/guild_service.py            82      0   100%
services/leaderboard_service.py      73      1    99%   157
services/lobby_service.py           112     29    74%   53-57, 66, 91, 112-126, 134-148, 156-167, 173, 176, 179, 182, 198-212, 224, 230, 253
services/user_service.py             62      0   100%
users/__init__.py                    78     13    83%   42-44, 52, 84, 88, 126-128, 136, 163-165
---------------------------------------------------------------
TOTAL                              4183    337    92%
```

## 🛠️ Development Setup

### Prerequisites

- Python 3.10 or 3.11
- Azure Functions Core Tools
- Azure CLI (for deployment)

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/DungeonBuilderServerSide.git
   cd DungeonBuilderServerSide
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests**

   ```bash
   python -m pytest --cov=. --cov-report=html
   ```

5. **Start local development server**
   ```bash
   func start
   ```

## 🚀 Deployment

### GitHub Actions CI/CD

The project includes automated CI/CD pipelines:

#### Continuous Integration (`ci.yml`)

- Runs on every push and pull request
- Tests against Python 3.10 and 3.11
- Generates coverage reports
- Uploads coverage to Codecov

#### Deployment (`deploy.yml`)

- **Manual deployment only** (disabled automatic deployment for safety)
- Deploy to staging or production environments
- Requires Azure Functions publish profile

### Manual Deployment

1. **Setup Azure Functions**

   ```bash
   az login
   az group create --name DungeonBuilderBackend --location eastus
   az storage account create --name dungeonbuilderstorage --resource-group DungeonBuilderBackend --location eastus --sku Standard_LRS
   az functionapp create --resource-group DungeonBuilderBackend --consumption-plan-location eastus --runtime python --runtime-version 3.10 --functions-version 4 --name dungeon-builder-backend --storage-account dungeonbuilderstorage --os-type linux
   ```

2. **Deploy using Serverless Framework**

   ```bash
   npm install -g serverless
   serverless deploy
   ```

3. **Deploy using Azure Functions Core Tools**
   ```bash
   func azure functionapp publish dungeon-builder-backend
   ```

## 🔧 Configuration

### Environment Variables

Create a `local.settings.json` file for local development:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_DB_CONNECTION_STRING": "your-cosmos-db-connection-string",
    "JWT_SECRET": "your-jwt-secret-key",
    "JWT_ALGORITHM": "HS256",
    "JWT_EXPIRATION_HOURS": "24"
  }
}
```

### Azure Configuration

Required Azure resources:

- **Azure Functions App**: Hosts the serverless functions
- **Azure Cosmos DB**: NoSQL database for user data and game state
- **Azure Storage Account**: For function app storage

## 📁 Project Structure

```
DungeonBuilderServerSide/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Continuous Integration
│   │   └── deploy.yml          # Deployment pipeline
│   └── project.yml             # GitHub Project configuration
├── auth/                       # Authentication endpoints
├── dungeons/                   # Dungeon management endpoints
├── friends/                    # Friendship system endpoints
├── guilds/                     # Guild management endpoints
├── health/                     # Health check endpoints
├── leaderboard/                # Leaderboard endpoints
├── lobbies/                    # Multiplayer lobby endpoints
├── models/                     # Pydantic data models
├── services/                   # Business logic services
├── tests/                      # Comprehensive test suite
├── users/                      # User management endpoints
├── host.json                   # Azure Functions host configuration
├── serverless.yml              # Serverless Framework configuration
└── requirements.txt            # Python dependencies
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test categories
python -m pytest tests/test_models.py
python -m pytest tests/test_services.py
python -m pytest tests/test_functions.py
```

### Test Categories

- **Model Tests**: Data validation and serialization
- **Service Tests**: Business logic with mocked dependencies
- **Function Tests**: Azure Functions endpoint testing
- **Integration Tests**: End-to-end API testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Maintain 90%+ test coverage
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes

## 📝 API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### User Endpoints

- `GET /api/users/{username}` - Get user profile
- `PUT /api/users/{username}` - Update user profile
- `GET /api/users/search` - Search users

### Dungeon Endpoints

- `POST /api/dungeons` - Create dungeon
- `GET /api/dungeons/{id}` - Get dungeon
- `PUT /api/dungeons/{id}` - Update dungeon
- `DELETE /api/dungeons/{id}` - Delete dungeon
- `GET /api/dungeons/search` - Search dungeons

### Lobby Endpoints

- `POST /api/lobbies` - Create lobby
- `GET /api/lobbies/{id}` - Get lobby
- `POST /api/lobbies/{id}/join` - Join lobby
- `POST /api/lobbies/{id}/leave` - Leave lobby
- `POST /api/lobbies/{id}/start` - Start game

### Guild Endpoints

- `POST /api/guilds` - Create guild
- `GET /api/guilds/{id}` - Get guild
- `POST /api/guilds/{id}/members` - Add member
- `DELETE /api/guilds/{id}/members/{member_id}` - Remove member

### Friendship Endpoints

- `POST /api/friends/request` - Send friend request
- `POST /api/friends/accept` - Accept friend request
- `POST /api/friends/reject` - Reject friend request
- `DELETE /api/friends/{friend_id}` - Remove friend

### Leaderboard Endpoints

- `GET /api/leaderboard/players` - Get player leaderboard
- `GET /api/leaderboard/dungeons` - Get dungeon leaderboard
- `GET /api/leaderboard/players/{player_id}/rank` - Get player rank

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Check the [Wiki](https://github.com/yourusername/DungeonBuilderServerSide/wiki)
- Review the [API Documentation](docs/api.md)

---

**Built with ❤️ using Azure Functions and Python**
