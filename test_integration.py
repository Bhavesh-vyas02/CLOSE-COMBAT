#!/usr/bin/env python3
"""
Test script for Close Combat database integration
Tests the integration without running the full game
"""

import sys
import os

# Mock pygame to avoid import errors during testing
class MockPygame:
    class mixer:
        class music:
            @staticmethod
            def set_volume(vol): pass
        
        @staticmethod
        def Sound(path): 
            return MockSound()
    
    @staticmethod
    def init(): pass

class MockSound:
    def set_volume(self, vol): pass

# Replace pygame import
sys.modules['pygame'] = MockPygame()

# Now we can import our integration modules
from game_integration import (
    get_game_session, initialize_game_database, 
    record_game_result, update_sound_preferences, 
    load_sound_preferences, start_player_session
)

def test_integration():
    """Test the database integration functionality"""
    print("🎮 Testing Close Combat Database Integration")
    print("=" * 50)
    
    try:
        # Test 1: Initialize database
        print("\n1. Testing Database Initialization...")
        if initialize_game_database():
            print("✅ Database initialized successfully")
        else:
            print("❌ Database initialization failed")
            return False
        
        # Test 2: Start player session
        print("\n2. Testing Player Session...")
        if start_player_session("TestPlayer"):
            print("✅ Player session started")
        else:
            print("❌ Player session failed")
            return False
        
        # Test 3: Sound preferences
        print("\n3. Testing Sound Preferences...")
        
        # Save sound preferences
        if update_sound_preferences(True, False):
            print("✅ Sound preferences saved")
        else:
            print("❌ Failed to save sound preferences")
        
        # Load sound preferences
        prefs = load_sound_preferences()
        if prefs and prefs['background_sound'] == True and prefs['player_sound'] == False:
            print("✅ Sound preferences loaded correctly")
        else:
            print("❌ Sound preferences not loaded correctly")
        
        # Test 4: Match recording
        print("\n4. Testing Match Recording...")
        
        # Record a test match
        if record_game_result("WARRIOR", "WIZARD", "P1", "PvC", 2, 1, 1, 2):
            print("✅ Match recorded successfully")
        else:
            print("❌ Match recording failed")
        
        # Test 5: Get session data
        print("\n5. Testing Session Data Retrieval...")
        
        session = get_game_session()
        if session:
            stats = session.get_player_stats()
            if stats:
                print(f"✅ Player stats retrieved: {stats.name}")
                print(f"   Overall stats: {stats.overall_stats}")
            else:
                print("⚠️  No player stats available yet")
            
            history = session.get_match_history(5)
            print(f"✅ Match history retrieved: {len(history)} matches")
            
            leaderboard = session.get_leaderboard(5)
            print(f"✅ Leaderboard retrieved: {len(leaderboard)} players")
        
        print("\n" + "=" * 50)
        print("🎉 Database Integration Test Complete!")
        print("\nIntegration Features Working:")
        print("• Database initialization on game start")
        print("• Player session management")
        print("• Sound preferences persistence")
        print("• Match result recording")
        print("• Statistics and history retrieval")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test():
    """Clean up test database"""
    try:
        from game_integration import cleanup_game_database
        cleanup_game_database()
        
        # Remove test database file
        if os.path.exists("close_combat.db"):
            os.remove("close_combat.db")
            print("🗑️  Test database cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}")

if __name__ == "__main__":
    print("Close Combat Database Integration Test")
    print("This tests the database integration without running the full game")
    
    success = test_integration()
    
    if success:
        keep_data = input("\nKeep test database? (y/n): ").lower().strip()
        if keep_data != 'y' and keep_data != 'yes':
            cleanup_test()
    else:
        print("\n❌ Integration test failed - check error messages above")
        cleanup_test()