# Dungeon Builder Backend

A comprehensive serverless multiplayer dungeon builder application built with Azure Functions and Python. This backend provides all the necessary APIs for a multiplayer dungeon creation and sharing platform.

## Features

### Authentication & User Management

- User registration and login with JWT tokens
- User profiles with stats and achievements
- User search functionality

### Dungeon Management

- Create, read, update, and delete dungeons
- Share dungeons as JSON files
- Rate dungeons (1-5 stars)
- Search and filter dungeons by difficulty, tags, and popularity
- Public and private dungeon support

### Multiplayer Features

- Create and manage lobbies for multiplayer sessions
- Invite friends to lobbies
- Join public lobbies
- Password-protected lobbies
- Real-time lobby status management

### Social Features

- Friend system with requests and management
- Block/unblock users
- Guild creation and management
- Team building for adventures

### Leaderboards

- Player leaderboards based on scores and achievements
- Dungeon leaderboards based on ratings and play count
- Top creators rankings
- Most played dungeons

## Architecture

### Technology Stack

- **Azure Functions**: Serverless compute platform
- **Azure Cosmos DB**: NoSQL database for data storage
- **Python 3.9+**: Backend programming language
- **JWT**: Authentication and authorization
- **Pydantic**: Data validation and serialization
- **Serverless Framework**: Infrastructure as Code and deployment

### Project Structure

```
DungeonBuilderBackend/
├── models/                 # Data models and schemas
├── services/              # Business logic services
├── auth/                  # Authentication functions
├── dungeons/              # Dungeon management functions
├── guilds/                # Guild management functions
├── lobbies/               # Multiplayer lobby functions
├── friends/               # Friend system functions
├── leaderboard/           # Leaderboard functions
├── users/                 # User management functions
├── health/                # Health check function
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest configuration and fixtures
│   ├── test_models.py     # Data model tests
│   ├── test_services.py   # Service layer tests
│   ├── test_functions.py  # Azure Functions tests
│   └── test_integration.py # Integration tests
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies for Serverless Framework
├── serverless.yml         # Serverless Framework configuration
├── pytest.ini            # Pytest configuration
├── host.json             # Azure Functions configuration
├── local.settings.json   # Local development settings
├── deploy.sh             # Linux/macOS deployment script
├── deploy.bat            # Windows deployment script
├── setup.sh              # Linux/macOS setup script
├── setup.bat             # Windows setup script
├── test_api.py           # API testing script
└── README.md             # Project documentation
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user profile

### Users

- `GET /users?search={term}` - Search users
- `GET /users/{user_id}` - Get user profile
- `PUT /users/profile` - Update current user profile
- `GET /users/me` - Get current user profile

### Dungeons

- `POST /dungeons` - Create a new dungeon
- `GET /dungeons` - Get dungeons with filtering
- `GET /dungeons/{dungeon_id}` - Get specific dungeon
- `PUT /dungeons/{dungeon_id}` - Update dungeon
- `DELETE /dungeons/{dungeon_id}` - Delete dungeon
- `POST /dungeons/{dungeon_id}/rate` - Rate a dungeon
- `POST /dungeons/{dungeon_id}/play` - Increment play count

### Guilds

- `POST /guilds` - Create a new guild
- `GET /guilds` - Get guilds with filtering
- `GET /guilds/{guild_id}` - Get specific guild
- `GET /guilds/{guild_id}/members` - Get guild members
- `POST /guilds/{guild_id}/members` - Add member to guild
- `DELETE /guilds/{guild_id}/members/{member_id}` - Remove member
- `PUT /guilds/{guild_id}` - Update guild
- `GET /guilds/my` - Get current user's guild

### Lobbies

- `POST /lobbies` - Create a new lobby
- `GET /lobbies` - Get lobbies with filtering
- `GET /lobbies/{lobby_id}` - Get specific lobby
- `POST /lobbies/{lobby_id}/join` - Join lobby
- `POST /lobbies/{lobby_id}/leave` - Leave lobby
- `POST /lobbies/{lobby_id}/start` - Start lobby
- `POST /lobbies/{lobby_id}/complete` - Complete lobby
- `POST /lobbies/{lobby_id}/cancel` - Cancel lobby
- `POST /lobbies/{lobby_id}/invite` - Invite to lobby
- `GET /lobbies/invites` - Get lobby invites
- `POST /lobbies/invites/{invite_id}/accept` - Accept lobby invite
- `POST /lobbies/invites/{invite_id}/decline` - Decline lobby invite

### Friends

- `POST /friends/request` - Send friend request
- `POST /friends/request/{requester_id}/accept` - Accept friend request
- `POST /friends/request/{requester_id}/reject` - Reject friend request
- `GET /friends` - Get friends list
- `GET /friends/requests/pending` - Get pending requests
- `GET /friends/requests/sent` - Get sent requests
- `DELETE /friends/{friend_id}` - Remove friend
- `POST /friends/{user_id}/block` - Block user
- `POST /friends/{user_id}/unblock` - Unblock user
- `GET /friends/{user_id}/check` - Check friendship status

### Leaderboards

- `GET /leaderboard/players` - Get player leaderboard
- `GET /leaderboard/dungeons` - Get dungeon leaderboard
- `GET /leaderboard/players/rank/{user_id}` - Get player rank
- `GET /leaderboard/dungeons/rank/{dungeon_id}` - Get dungeon rank
- `GET /leaderboard/players/{user_id}` - Get player score
- `GET /leaderboard/dungeons/{dungeon_id}` - Get dungeon score
- `GET /leaderboard/players/top-creators` - Get top creators
- `GET /leaderboard/dungeons/most-played` - Get most played dungeons
- `POST /leaderboard/players/update` - Update player score
- `POST /leaderboard/dungeons/update` - Update dungeon score

## Setup and Deployment

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm (comes with Node.js)
- Azure CLI
- Azure Functions Core Tools (for local development)

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd DungeonBuilderBackend
   ```

2. **Install dependencies**

   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Install Node.js dependencies
   npm install
   ```

3. **Configure environment variables**
   Update `local.settings.json` with your Azure Cosmos DB credentials:

   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "UseDevelopmentStorage=true",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "COSMOS_DB_ENDPOINT": "your_cosmos_db_endpoint",
       "COSMOS_DB_KEY": "your_cosmos_db_key",
       "COSMOS_DB_DATABASE": "DungeonBuilderDB",
       "JWT_SECRET": "your_jwt_secret_key_here",
       "JWT_ALGORITHM": "HS256",
       "JWT_EXPIRATION_MINUTES": "60"
     }
   }
   ```

4. **Run locally**
   ```bash
   func start
   ```

### Serverless Framework Deployment

The project uses the Serverless Framework for infrastructure as code and automated deployment. This provides a more modern, cross-platform approach to deploying Azure Functions.

#### Prerequisites for Deployment

1. **Install Serverless Framework plugins**

   ```bash
   npm run setup:dev
   ```

2. **Login to Azure**
   ```bash
   az login
   ```

#### Automated Deployment

**Linux/macOS:**

```bash
./deploy.sh [stage] [region] [jwt_secret]
```

**Windows:**

```cmd
deploy.bat [stage] [region] [jwt_secret]
```

**Examples:**

```bash
# Deploy to dev environment
./deploy.sh dev eastus my-super-secret-jwt-key

# Deploy to production
./deploy.sh prod eastus my-production-jwt-secret

# Deploy to staging in West Europe
./deploy.sh staging westeurope my-staging-jwt-secret
```

#### Manual Deployment

1. **Install dependencies**

   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. **Deploy using Serverless Framework**

   ```bash
   # Deploy to dev environment
   npx serverless deploy --stage dev --region eastus

   # Deploy to production
   npx serverless deploy --stage prod --region eastus
   ```

3. **Get deployment information**
   ```bash
   npx serverless info --stage dev
   ```

#### Deployment Features

The Serverless Framework deployment automatically:

- Creates Azure Resource Group
- Sets up Azure Key Vault for secure secret management
- Creates Cosmos DB account with serverless capacity
- Creates all required Cosmos DB containers
- Deploys Azure Functions with proper configuration
- Sets up environment variables and secrets
- Configures CORS and authentication settings

#### Environment Management

The deployment supports multiple environments:

- **dev**: Development environment
- **staging**: Staging environment for testing
- **prod**: Production environment

Each environment gets its own:

- Resource group
- Key Vault
- Cosmos DB account
- Function App

#### Useful Commands

```bash
# Deploy to specific stage
npm run deploy:prod

# Remove deployment
npm run remove:prod

# View logs
npm run logs

# Invoke function locally
npm run invoke:local health

# Package without deploying
npm run package

# Test API endpoints
npm run test
```

## Database Schema

### Cosmos DB Containers

- **users**: User accounts and profiles
- **dungeons**: Dungeon data and metadata
- **guilds**: Guild information and members
- **lobbies**: Multiplayer lobby sessions
- **friendships**: Friend relationships and requests
- **ratings**: Dungeon ratings and reviews
- **leaderboard**: Player and dungeon scores

### Partition Keys

- **users**: username
- **dungeons**: creator_id
- **guilds**: leader_id
- **lobbies**: creator_id
- **friendships**: requester_id
- **ratings**: dungeon_id
- **leaderboard**: partitionKey (player_scores/dungeon_scores)

## Security

### Authentication

- JWT-based authentication with configurable expiration
- Password hashing using bcrypt
- Token-based session management

### Authorization

- Role-based access control (Player/Admin)
- Resource ownership validation
- Guild leadership permissions

### Data Protection

- Input validation using Pydantic models
- SQL injection prevention through parameterized queries
- CORS configuration for web clients

## Performance Considerations

### Database Optimization

- Efficient partition key design for Cosmos DB
- Indexed queries for common operations
- Connection pooling and reuse

### Caching Strategy

- Leaderboard caching for frequently accessed data
- User session caching
- Guild member list caching

### Scalability

- Serverless architecture for automatic scaling
- Stateless function design
- Efficient data models for high-throughput operations

## Monitoring and Logging

### Application Insights

- Automatic telemetry collection
- Performance monitoring
- Error tracking and alerting

### Logging

- Structured logging with correlation IDs
- Error logging with stack traces
- Audit logging for sensitive operations

## Testing

The project includes a comprehensive test suite with unit tests, integration tests, and API tests to ensure code quality and reliability.

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **API Tests**: Test HTTP endpoints and responses
- **Model Tests**: Test data validation and serialization

### Test Categories

- **Models** (`test_models.py`): Data model validation and serialization
- **Services** (`test_services.py`): Business logic and database operations
- **Functions** (`test_functions.py`): Azure Functions HTTP endpoints
- **Integration** (`test_integration.py`): End-to-end workflows

### Running Tests

#### Prerequisites

```bash
# Install test dependencies
pip install -r requirements.txt
```

#### Test Commands

```bash
# Run all tests
npm run test:all

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration

# Run specific test categories
npm run test:models
npm run test:services
npm run test:functions

# Run tests with coverage
npm run test:coverage

# Run fast tests (excluding slow tests)
npm run test:fast

# Run authentication tests
npm run test:auth

# Run tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run specific test class
pytest tests/test_models.py::TestUserModel -v

# Run specific test method
pytest tests/test_models.py::TestUserModel::test_valid_user_creation -v
```

#### Test Coverage

The test suite aims for 80% code coverage. Coverage reports are generated in multiple formats:

- **Terminal**: Shows missing lines in terminal output
- **HTML**: Detailed coverage report in `htmlcov/index.html`
- **XML**: Coverage data for CI/CD integration

```bash
# Generate coverage report
npm run test:coverage

# View HTML coverage report
open htmlcov/index.html
```

#### Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.auth`: Authentication tests
- `@pytest.mark.models`: Data model tests
- `@pytest.mark.services`: Service layer tests
- `@pytest.mark.functions`: Azure Functions tests

#### Test Fixtures

The test suite includes comprehensive fixtures for:

- **Mock Services**: Database and authentication services
- **Sample Data**: Users, dungeons, guilds, lobbies, etc.
- **JWT Tokens**: Valid and expired tokens for testing
- **HTTP Requests**: Mock request objects
- **Azure Context**: Mock Azure Functions context

#### Continuous Integration

Tests are configured to run in CI/CD pipelines with:

- Coverage reporting
- Test result aggregation
- Failure thresholds
- Parallel test execution

### Writing Tests

#### Unit Test Example

```python
def test_user_registration_success(database_service, auth_service):
    """Test successful user registration."""
    user_service = UserService(database_service, auth_service)

    with patch.object(database_service, 'query_items') as mock_query:
        mock_query.return_value = []  # No existing user

        with patch.object(database_service, 'create_item') as mock_create:
            mock_create.return_value = {"id": "new-user-123"}

            result = user_service.register_user("newuser", "new@example.com", "password123")

            assert result is not None
            assert "user_id" in result
            assert "token" in result
```

#### Integration Test Example

```python
def test_complete_user_workflow(database_service, auth_service):
    """Test complete user registration and login workflow."""
    user_service = UserService(database_service, auth_service)

    # Register user
    with patch.object(database_service, 'query_items') as mock_query:
        mock_query.return_value = []

        with patch.object(database_service, 'create_item') as mock_create:
            mock_create.return_value = {"id": "new-user-123"}

            result = user_service.register_user("newuser", "new@example.com", "password123")

            # Verify registration
            assert result is not None
            token = result["token"]

            # Verify token
            payload = auth_service.verify_token(token)
            assert payload is not None
            assert payload["user_id"] == "new-user-123"
```

#### API Test Example

```python
def test_register_endpoint_success(mock_request, mock_context, database_service, auth_service):
    """Test successful user registration via API endpoint."""
    mock_request.method = "POST"
    mock_request.get_body.return_value = json.dumps({
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    }).encode('utf-8')

    with patch('auth.DatabaseService') as mock_db_class:
        mock_db_class.return_value = database_service

        with patch('auth.AuthService') as mock_auth_class:
            mock_auth_class.return_value = auth_service

            with patch.object(database_service, 'query_items') as mock_query:
                mock_query.return_value = []

                with patch.object(database_service, 'create_item') as mock_create:
                    mock_create.return_value = {"id": "new-user-123"}

                    result = auth.main(mock_request, mock_context)

                    assert result.status_code == 201
                    data = json.loads(result.get_body())
                    assert "user_id" in data
                    assert "token" in data
```

### Test Best Practices

1. **Use Descriptive Names**: Test names should clearly describe what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
3. **Mock External Dependencies**: Use mocks for database, external APIs, and services
4. **Test Edge Cases**: Include tests for error conditions and boundary values
5. **Keep Tests Fast**: Avoid slow operations and use appropriate markers
6. **Maintain Test Data**: Use fixtures for consistent test data
7. **Test One Thing**: Each test should verify a single behavior
8. **Use Meaningful Assertions**: Assertions should be specific and descriptive

### Debugging Tests

```bash
# Run tests with debug output
pytest tests/ -v -s

# Run specific test with debug
pytest tests/test_models.py::TestUserModel::test_valid_user_creation -v -s

# Run tests with maximum verbosity
pytest tests/ -vvv

# Run tests and stop on first failure
pytest tests/ -x

# Run tests and show local variables on failure
pytest tests/ --tb=long
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository or contact the development team.
