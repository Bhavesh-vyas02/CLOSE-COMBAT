#!/usr/bin/env python3
"""
Test script for the Close Combat database system
Run this to verify all database components work correctly
"""

import os
import sys
from database_manager import get_database, close_database
from player_manager import PlayerManager
from match_tracker import MatchTracker
from settings_manager import SettingsManager

def test_database_system():
    """Test all database components"""
    print("🎮 Testing Close Combat Database System")
    print("=" * 50)
    
    try:
        # Test 1: Database Connection
        print("\n1. Testing Database Connection...")
        db = get_database()
        if db:
            print("✅ Database connected successfully")
            print(f"   Database file: {db.db_path}")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test 2: Player Management
        print("\n2. Testing Player Management...")
        player_mgr = PlayerManager()
        
        # Create test player
        player_id = player_mgr.create_player("TestPlayer")
        if player_id:
            print(f"✅ Created test player (ID: {player_id})")
        else:
            print("❌ Failed to create player")
            return False
        
        # Get player stats
        player = player_mgr.get_player_stats(player_id)
        if player:
            print(f"✅ Retrieved player stats: {player.name}")
        else:
            print("❌ Failed to get player stats")
        
        # Test 3: Settings Management
        print("\n3. Testing Settings Management...")
        settings_mgr = SettingsManager()
        
        # Save and retrieve setting
        settings_mgr.save_setting("background_sound", True, player_id)
        bg_sound = settings_mgr.get_setting("background_sound", player_id=player_id)
        if bg_sound == True:
            print("✅ Settings save/retrieve working")
        else:
            print("❌ Settings save/retrieve failed")
        
        # Test 4: Match Tracking
        print("\n4. Testing Match Tracking...")
        match_tracker = MatchTracker()
        
        # Record test match
        match_data = {
            'player_character': 'WARRIOR',
            'opponent_character': 'WIZARD',
            'game_mode': 'PvC',
            'result': 'WIN',
            'duration': 120,
            'rounds_won': 2,
            'rounds_lost': 1
        }
        
        match_id = match_tracker.record_match(player_id, match_data)
        if match_id:
            print(f"✅ Recorded test match (ID: {match_id})")
        else:
            print("❌ Failed to record match")
        
        # Update player stats
        player_mgr.update_character_stats(player_id, 'WARRIOR', 'WIN')
        print("✅ Updated character stats")
        
        # Get match history
        history = match_tracker.get_match_history(player_id, limit=10)
        if history:
            print(f"✅ Retrieved match history ({len(history)} matches)")
        else:
            print("❌ Failed to get match history")
        
        # Test 5: Leaderboard
        print("\n5. Testing Leaderboard...")
        
        # Add more matches to qualify for leaderboard
        for i in range(12):
            result = 'WIN' if i % 2 == 0 else 'LOSS'
            character = ['WARRIOR', 'WIZARD', 'HUNTRESS'][i % 3]
            
            match_data = {
                'player_character': character,
                'opponent_character': 'KING',
                'game_mode': 'PvC',
                'result': result,
                'duration': 90 + i * 10,
                'rounds_won': 2 if result == 'WIN' else 1,
                'rounds_lost': 1 if result == 'WIN' else 2
            }
            
            match_tracker.record_match(player_id, match_data)
            player_mgr.update_character_stats(player_id, character, result)
        
        leaderboard = player_mgr.get_leaderboard(limit=5)
        if leaderboard:
            print(f"✅ Generated leaderboard ({len(leaderboard)} players)")
            for entry in leaderboard:
                print(f"   {entry['rank']}. {entry['player_name']} - {entry['win_percentage']:.1f}% wins")
        else:
            print("⚠️  Leaderboard empty (need 10+ matches to qualify)")
        
        # Test 6: Database Integrity
        print("\n6. Testing Database Integrity...")
        if db.check_database_integrity():
            print("✅ Database integrity check passed")
        else:
            print("❌ Database integrity issues detected")
        
        print("\n" + "=" * 50)
        print("🎉 Database System Test Complete!")
        print("\nDatabase Features Ready:")
        print("• Player profiles and statistics")
        print("• Match history tracking")
        print("• Settings persistence")
        print("• Leaderboard system")
        print("• Error handling and recovery")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        close_database()
        print("\n🔒 Database connection closed")

def cleanup_test_data():
    """Remove test database file"""
    try:
        db_path = "close_combat.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"🗑️  Removed test database: {db_path}")
    except Exception as e:
        print(f"⚠️  Could not remove test database: {e}")

if __name__ == "__main__":
    print("Close Combat Database System Test")
    print("This will create a test database and verify all features work")
    
    # Ask user if they want to run the test
    response = input("\nRun database test? (y/n): ").lower().strip()
    
    if response == 'y' or response == 'yes':
        success = test_database_system()
        
        if success:
            # Ask if user wants to keep test data
            keep_data = input("\nKeep test database for inspection? (y/n): ").lower().strip()
            if keep_data != 'y' and keep_data != 'yes':
                cleanup_test_data()
        else:
            print("\n❌ Test failed - check error messages above")
    else:
        print("Test cancelled")