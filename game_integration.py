"""
Game Integration Module for Close Combat Database System
Handles all database operations and integrates with existing game code
"""

import pygame
import logging
from datetime import datetime
from database_manager import get_database, close_database
from player_manager import PlayerManager
from match_tracker import MatchTracker
from settings_manager import SettingsManager

class GameSession:
    """Manages a single game session with database integration"""
    
    def __init__(self):
        self.player_manager = PlayerManager()
        self.match_tracker = MatchTracker()
        self.settings_manager = SettingsManager()
        self.logger = logging.getLogger('GameSession')
        
        # Session tracking
        self.current_player_id = None
        self.session_start_time = None
        self.match_start_time = None
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database and default settings"""
        try:
            db = get_database()
            if db:
                self.logger.info("Database initialized successfully")
                # Initialize default global settings
                self.settings_manager.initialize_default_settings()
            else:
                self.logger.error("Failed to initialize database")
        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")
    
    def start_session(self, player_name=None):
        """Start a new game session"""
        try:
            self.session_start_time = datetime.now()
            
            if player_name:
                # Get or create player
                player = self.player_manager.get_player_by_name(player_name)
                if not player:
                    self.current_player_id = self.player_manager.create_player(player_name)
                    if self.current_player_id:
                        self.logger.info(f"Created new player: {player_name}")
                    else:
                        self.logger.error(f"Failed to create player: {player_name}")
                        return False
                else:
                    self.current_player_id = player.player_id
                    self.logger.info(f"Loaded existing player: {player_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            return False
    
    def end_session(self):
        """End the current game session"""
        try:
            if self.current_player_id and self.session_start_time:
                # Calculate session duration
                session_duration = (datetime.now() - self.session_start_time).total_seconds()
                
                # Update playtime
                self.player_manager.update_playtime(self.current_player_id, int(session_duration))
                
                self.logger.info(f"Session ended. Duration: {session_duration:.1f} seconds")
            
            # Close database connection
            close_database()
            
        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
    
    def start_match(self):
        """Mark the start of a match"""
        self.match_start_time = datetime.now()
    
    def record_match_result(self, player_character, opponent_character, game_mode, 
                          result, rounds_won=0, rounds_lost=0):
        """Record match result in database"""
        try:
            if not self.current_player_id:
                self.logger.warning("No active player - cannot record match")
                return False
            
            # Calculate match duration
            duration = 0
            if self.match_start_time:
                duration = (datetime.now() - self.match_start_time).total_seconds()
            
            # Prepare match data
            match_data = {
                'player_character': player_character,
                'opponent_character': opponent_character,
                'game_mode': game_mode,
                'result': result,
                'duration': int(duration),
                'rounds_won': rounds_won,
                'rounds_lost': rounds_lost
            }
            
            # Record match
            match_id = self.match_tracker.record_match(self.current_player_id, match_data)
            
            if match_id:
                # Update character statistics
                self.player_manager.update_character_stats(
                    self.current_player_id, player_character, result
                )
                
                self.logger.info(f"Match recorded: {result} with {player_character} vs {opponent_character}")
                return True
            else:
                self.logger.error("Failed to record match")
                return False
                
        except Exception as e:
            self.logger.error(f"Error recording match: {e}")
            return False
    
    def get_player_stats(self):
        """Get current player statistics"""
        try:
            if not self.current_player_id:
                return None
            
            return self.player_manager.get_player_stats(self.current_player_id)
            
        except Exception as e:
            self.logger.error(f"Error getting player stats: {e}")
            return None
    
    def get_sound_settings(self):
        """Get current sound settings"""
        try:
            return self.settings_manager.get_sound_settings(self.current_player_id)
        except Exception as e:
            self.logger.error(f"Error getting sound settings: {e}")
            return {
                'background_music_volume': 0.5,
                'sound_effects_volume': 0.75,
                'background_sound': True,
                'player_sound': True
            }
    
    def save_sound_settings(self, background_sound=None, player_sound=None, 
                          bg_volume=None, sfx_volume=None):
        """Save sound settings to database"""
        try:
            if background_sound is not None:
                self.settings_manager.save_setting('background_sound', background_sound, self.current_player_id)
            
            if player_sound is not None:
                self.settings_manager.save_setting('player_sound', player_sound, self.current_player_id)
            
            if bg_volume is not None:
                self.settings_manager.save_setting('background_music_volume', bg_volume)
            
            if sfx_volume is not None:
                self.settings_manager.save_setting('sound_effects_volume', sfx_volume)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving sound settings: {e}")
            return False
    
    def apply_sound_settings(self, pygame_mixer):
        """Apply saved sound settings to pygame"""
        try:
            return self.settings_manager.apply_sound_settings(pygame_mixer, self.current_player_id)
        except Exception as e:
            self.logger.error(f"Error applying sound settings: {e}")
            return {'effects_volume': 0.5, 'effects_enabled': True}
    
    def get_leaderboard(self, limit=10):
        """Get current leaderboard"""
        try:
            return self.player_manager.get_leaderboard(limit)
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return []
    
    def get_match_history(self, limit=20):
        """Get match history for current player"""
        try:
            if not self.current_player_id:
                return []
            
            return self.match_tracker.get_match_history(self.current_player_id, limit)
            
        except Exception as e:
            self.logger.error(f"Error getting match history: {e}")
            return []

# Global game session instance
_game_session = None

def get_game_session():
    """Get the global game session instance"""
    global _game_session
    if _game_session is None:
        _game_session = GameSession()
    return _game_session

def initialize_game_database():
    """Initialize the game database system"""
    try:
        session = get_game_session()
        return session is not None
    except Exception as e:
        logging.error(f"Failed to initialize game database: {e}")
        return False

def cleanup_game_database():
    """Cleanup database resources"""
    global _game_session
    if _game_session:
        _game_session.end_session()
        _game_session = None

# Helper functions for easy integration with existing game code

def record_game_result(p1_character, p2_character, winner, game_mode, 
                      p1_rounds_won=0, p1_rounds_lost=0, p2_rounds_won=0, p2_rounds_lost=0):
    """
    Record game result for both players
    winner: 'P1', 'P2', or 'DRAW'
    """
    try:
        session = get_game_session()
        if not session.current_player_id:
            return False
        
        # Determine result for player 1
        if winner == 'P1':
            result = 'WIN'
        elif winner == 'P2':
            result = 'LOSS'
        else:
            result = 'DRAW'
        
        # Record match for player 1 (assuming player 1 is the human player)
        return session.record_match_result(
            p1_character, p2_character, game_mode, result,
            p1_rounds_won, p1_rounds_lost
        )
        
    except Exception as e:
        logging.error(f"Error recording game result: {e}")
        return False

def update_sound_preferences(background_on, effects_on):
    """Update sound preferences in database"""
    try:
        session = get_game_session()
        return session.save_sound_settings(
            background_sound=background_on,
            player_sound=effects_on
        )
    except Exception as e:
        logging.error(f"Error updating sound preferences: {e}")
        return False

def load_sound_preferences():
    """Load sound preferences from database"""
    try:
        session = get_game_session()
        settings = session.get_sound_settings()
        return {
            'background_sound': settings.get('background_sound', True),
            'player_sound': settings.get('player_sound', True),
            'background_volume': settings.get('background_music_volume', 0.5),
            'effects_volume': settings.get('sound_effects_volume', 0.75)
        }
    except Exception as e:
        logging.error(f"Error loading sound preferences: {e}")
        return {
            'background_sound': True,
            'player_sound': True,
            'background_volume': 0.5,
            'effects_volume': 0.75
        }

def get_player_statistics():
    """Get current player statistics"""
    try:
        session = get_game_session()
        return session.get_player_stats()
    except Exception as e:
        logging.error(f"Error getting player statistics: {e}")
        return None

def start_player_session(player_name):
    """Start a session for a specific player"""
    try:
        session = get_game_session()
        return session.start_session(player_name)
    except Exception as e:
        logging.error(f"Error starting player session: {e}")
        return False