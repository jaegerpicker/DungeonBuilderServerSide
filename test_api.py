#!/usr/bin/env python3
"""
Test script for Dungeon Builder Backend API
This script tests the main API endpoints to ensure they work correctly.
"""

import requests
import json
import time
from typing import Dict, Any

class DungeonBuilderAPITester:
    def __init__(self, base_url: str = "http://localhost:7071"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_user = None
        self.test_dungeon = None
        self.test_guild = None
        self.test_lobby = None

    def log(self, message: str, success: bool = True):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {message}")

    def test_health_check(self) -> bool:
        """Test if the API is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                self.log("Health check passed")
                return True
            else:
                self.log(f"Health check failed: {response.status_code}", False)
                return False
        except Exception as e:
            self.log(f"Health check error: {str(e)}", False)
            return False

    def test_register_user(self) -> bool:
        """Test user registration"""
        try:
            user_data = {
                "username": f"testuser_{int(time.time())}",
                "email": f"testuser_{int(time.time())}@example.com",
                "password": "testpassword123",
                "display_name": "Test User"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=user_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.test_user = data.get("user")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log("User registration passed")
                return True
            else:
                self.log(f"User registration failed: {response.status_code} - {response.text}", False)
                return False
        except Exception as e:
            self.log(f"User registration error: {str(e)}", False)
            return False

    def test_login_user(self) -> bool:
        """Test user login"""
        try:
            login_data = {
                "username": self.test_user["username"],
                "password": "testpassword123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log("User login passed")
                return True
            else:
                self.log(f"User login failed: {response.status_code} - {response.text}", False)
                return False
        except Exception as e:
            self.log(f"User login error: {str(e)}", False)
            return False

    def test_get_user_profile(self) -> bool:
        """Test getting user profile"""
        try:
            response = self.session.get(f"{self.base_url}/api/auth/me")
            
            if response.status_code == 200:
                profile = response.json()
                if profile["id"] == self.test_user["id"]:
                    self.log("Get user profile passed")
                    return True
                else:
                    self.log("Get user profile failed: profile ID mismatch", False)
                    return False
            else:
                self.log(f"Get user profile failed: {response.status_code} - {response.text}", False)
                return False
        except Exception as e:
            self.log(f"Get user profile error: {str(e)}", False)
            return False

    def test_create_dungeon(self) -> bool:
        """Test dungeon creation"""
        try:
            dungeon_data = {
                "name": "Test Dungeon",
                "description": "A test dungeon for API testing",
                "difficulty": "medium",
                "dungeon_data": {
                    "rooms": [
                        {"id": 1, "type": "entrance", "position": {"x": 0, "y": 0}},
                        {"id": 2, "type": "treasure", "position": {"x": 1, "y": 1}}
                    ],
                    "connections": [{"from": 1, "to": 2}]
                },
                "tags": ["test", "api"],
                "is_public": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/dungeons",
                json=dungeon_data
            )
            
            if response.status_code == 201:
                self.test_dungeon = response.json()
                self.log("Dungeon creation passed")
                return True
            else:
                self.log(f"Dungeon creation failed: {response.status_code} - {response.text}", False)
                return False
        except Exception as e:
            self.log(f"Dungeon creation error: {str(e)}", False)
            return False

    def test_get_dungeons(self) -> bool:
        """Test getting dungeons"""
        try:
            response = self.session.get(f"{self.base_url}/api/dungeons")
            
            if response.status_code == 200:
                dungeons = response.json()
                if isinstance(dungeons, list):
                    self.log("Get dungeons passed")
                    return True
                else:
                    self.log("Get dungeons failed: expected list", False)
                    return False
            else:
                self.log(f"Get dungeons failed: {response.status_code} - {response.text}", False)
                return False
        except Exception as e:
            self.log(f"Get dungeons error: {str(e)}", False)
            return False

    def test_rate_dungeon(self) -> bool:
        """Test dungeon rating"""
        try:
            rating_data = {
                "rating": 5,
                "comment": "Great test dungeon!"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/dungeons/{self.test_dungeon['id']}/rate",
                json=rating_data
            )
            
            if response.status_code == 200:
                self.log("Dungeon rating passed")
                return True
            else:
                self.log(f"Dungeon rating failed: {response.status_code} - {response.text}", False)
                return False
        except Exception as e:
            self.log(f"Dungeon rating error: {str(e)}", False)
            return False

    def test_create_guild(self) -> bool:
        """Test guild creation"""
        try:
            guild_data = {
                "name": "Test Guild",
                "description": "A test guild for API testing",
                "max_members": 10,
                "is_public": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/guilds",
                json=guild_data
            )
            
            if response.status_code == 201:
                self.test_guild = response.json()
                self.log("Guild creation passed")
                return True
            else:
                self.log(f"Guild creation failed: {response.status_code} - {response.text}", False)
                return False
        except Exception as e:
            self.log(f"Guild creation error: {str(e)}", False)
            return False

    def test_create_lobby(self) -> bool:
        """Test lobby creation"""
        try:
            lobby_data = {
                "name": "Test Lobby",
                "dungeon_id": self.test_dungeon["id"],
                "max_players": 4,
                "is_public": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/lobbies",
                json=lobby_data
            )
            
            if response.status_code == 201:
                self.test_lobby = response.json()
                self.log("Lobby creation passed")
                return True
            else:
                self.log(f"Lobby creation failed: {response.status_code} - {response.text}", False)
                return False
        except Exception as e:
            self.log(f"Lobby creation error: {str(e)}", False)
            return False

    def test_get_leaderboards(self) -> bool:
        """Test leaderboard endpoints"""
        try:
            # Test player leaderboard
            response = self.session.get(f"{self.base_url}/api/leaderboard/players")
            if response.status_code != 200:
                self.log(f"Player leaderboard failed: {response.status_code}", False)
                return False
            
            # Test dungeon leaderboard
            response = self.session.get(f"{self.base_url}/api/leaderboard/dungeons")
            if response.status_code != 200:
                self.log(f"Dungeon leaderboard failed: {response.status_code}", False)
                return False
            
            self.log("Leaderboard tests passed")
            return True
        except Exception as e:
            self.log(f"Leaderboard tests error: {str(e)}", False)
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all API tests"""
        print("🚀 Starting Dungeon Builder Backend API Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_register_user),
            ("User Login", self.test_login_user),
            ("Get User Profile", self.test_get_user_profile),
            ("Create Dungeon", self.test_create_dungeon),
            ("Get Dungeons", self.test_get_dungeons),
            ("Rate Dungeon", self.test_rate_dungeon),
            ("Create Guild", self.test_create_guild),
            ("Create Lobby", self.test_create_lobby),
            ("Leaderboards", self.test_get_leaderboards),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                self.log(f"{test_name} error: {str(e)}", False)
                results[test_name] = False
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print("=" * 50)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The API is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the API implementation.")
        
        return results

def main():
    """Main function to run the API tests"""
    import sys
    
    # Get base URL from command line argument or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7071"
    
    tester = DungeonBuilderAPITester(base_url)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 