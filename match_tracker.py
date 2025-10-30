from database_manager import get_database
from datetime import datetime, timedelta
import logging

class MatchRecord:
    """Data model for match record information"""
    def __init__(self, match_id, date, player_char, opponent_char, 
                 game_mode, result, duration, rounds_won, rounds_lost):
        self.match_id = match_id
        self.date = date
        self.player_character = player_char
        self.opponent_character = opponent_char
        self.game_mode = game_mode
        self.result = result
        self.duration = duration
        self.rounds_won = rounds_won
        self.rounds_lost = rounds_lost

class MatchTracker:
    """Manages match recording and history retrieval"""
    
    def __init__(self):
        self.db = get_database()
        self.logger = logging.getLogger('MatchTracker')
        
        # Valid values for validation
        self.valid_characters = [
            'WARRIOR', 'WIZARD', 'HUNTRESS', 'KING', 'HERO_KNIGHT', 'MARTIAL_HERO'
        ]
        self.valid_game_modes = ['PvP', 'PvC']
        self.valid_results = ['WIN', 'LOSS', 'DRAW']
    
    def record_match(self, player_id, match_data):
        """Save match results to database"""
        try:
            # Validate match data
            if not self._validate_match_data(match_data):
                self.logger.warning("Invalid match data provided")
                return False
            
            # Prepare match record
            match_date = datetime.now().isoformat()
            
            query = '''
                INSERT INTO match_history (
                    player_id, match_date, player_character, opponent_character,
                    game_mode, result, match_duration, rounds_won, rounds_lost
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                player_id,
                match_date,
                match_data['player_character'],
                match_data['opponent_character'],
                match_data['game_mode'],
                match_data['result'],
                match_data.get('duration', 0),
                match_data.get('rounds_won', 0),
                match_data.get('rounds_lost', 0)
            )
            
            cursor = self.db.execute_query(query, params)
            match_id = cursor.lastrowid
            
            self.logger.info(f"Recorded match {match_id} for player {player_id}: {match_data['result']}")
            
            # Check if we need to cleanup old matches
            self._cleanup_old_matches_if_needed(player_id)
            
            return match_id
            
        except Exception as e:
            self.logger.error(f"Error recording match for player {player_id}: {e}")
            return False
    
    def get_match_history(self, player_id, limit=50):
        """Retrieve player's match history"""
        try:
            query = '''
                SELECT * FROM match_history
                WHERE player_id = ?
                ORDER BY match_date DESC
                LIMIT ?
            '''
            
            results = self.db.fetch_all(query, (player_id, limit))
            
            matches = []
            for row in results:
                match = MatchRecord(
                    row['match_id'],
                    row['match_date'],
                    row['player_character'],
                    row['opponent_character'],
                    row['game_mode'],
                    row['result'],
                    row['match_duration'],
                    row['rounds_won'],
                    row['rounds_lost']
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error getting match history for player {player_id}: {e}")
            return []
    
    def get_recent_matches(self, player_id, days=7):
        """Get matches from the last N days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = '''
                SELECT * FROM match_history
                WHERE player_id = ? AND match_date >= ?
                ORDER BY match_date DESC
            '''
            
            results = self.db.fetch_all(query, (player_id, cutoff_date))
            
            matches = []
            for row in results:
                match = MatchRecord(
                    row['match_id'],
                    row['match_date'],
                    row['player_character'],
                    row['opponent_character'],
                    row['game_mode'],
                    row['result'],
                    row['match_duration'],
                    row['rounds_won'],
                    row['rounds_lost']
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error getting recent matches for player {player_id}: {e}")
            return []
    
    def get_match_statistics(self, player_id):
        """Get comprehensive match statistics for a player"""
        try:
            # Overall statistics
            overall_query = '''
                SELECT 
                    COUNT(*) as total_matches,
                    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN result = 'DRAW' THEN 1 ELSE 0 END) as draws,
                    AVG(match_duration) as avg_duration,
                    SUM(rounds_won) as total_rounds_won,
                    SUM(rounds_lost) as total_rounds_lost
                FROM match_history
                WHERE player_id = ?
            '''
            
            overall_stats = self.db.fetch_one(overall_query, (player_id,))
            
            # Character-specific statistics
            char_query = '''
                SELECT 
                    player_character,
                    COUNT(*) as matches,
                    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN result = 'DRAW' THEN 1 ELSE 0 END) as draws
                FROM match_history
                WHERE player_id = ?
                GROUP BY player_character
                ORDER BY matches DESC
            '''
            
            char_stats = self.db.fetch_all(char_query, (player_id,))
            
            # Game mode statistics
            mode_query = '''
                SELECT 
                    game_mode,
                    COUNT(*) as matches,
                    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins
                FROM match_history
                WHERE player_id = ?
                GROUP BY game_mode
            '''
            
            mode_stats = self.db.fetch_all(mode_query, (player_id,))
            
            return {
                'overall': dict(overall_stats) if overall_stats else {},
                'by_character': [dict(row) for row in char_stats],
                'by_mode': [dict(row) for row in mode_stats]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting match statistics for player {player_id}: {e}")
            return {'overall': {}, 'by_character': [], 'by_mode': []}
    
    def calculate_match_duration(self, start_time, end_time):
        """Calculate match duration in seconds"""
        try:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
            
            duration = (end_time - start_time).total_seconds()
            return max(0, int(duration))  # Ensure non-negative integer
            
        except Exception as e:
            self.logger.error(f"Error calculating match duration: {e}")
            return 0
    
    def cleanup_old_matches(self, player_id=None, keep_count=1000):
        """Remove oldest matches when limit is reached"""
        try:
            if player_id:
                # Cleanup for specific player
                count_query = 'SELECT COUNT(*) as count FROM match_history WHERE player_id = ?'
                count_result = self.db.fetch_one(count_query, (player_id,))
                
                if count_result and count_result['count'] > keep_count:
                    delete_query = '''
                        DELETE FROM match_history
                        WHERE player_id = ? AND match_id NOT IN (
                            SELECT match_id FROM match_history
                            WHERE player_id = ?
                            ORDER BY match_date DESC
                            LIMIT ?
                        )
                    '''
                    self.db.execute_query(delete_query, (player_id, player_id, keep_count))
                    self.logger.info(f"Cleaned up old matches for player {player_id}")
            else:
                # Global cleanup
                count_query = 'SELECT COUNT(*) as count FROM match_history'
                count_result = self.db.fetch_one(count_query)
                
                if count_result and count_result['count'] > keep_count * 10:  # Global limit
                    delete_query = '''
                        DELETE FROM match_history
                        WHERE match_id NOT IN (
                            SELECT match_id FROM match_history
                            ORDER BY match_date DESC
                            LIMIT ?
                        )
                    '''
                    self.db.execute_query(delete_query, (keep_count * 10,))
                    self.logger.info("Performed global match history cleanup")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during match cleanup: {e}")
            return False
    
    def get_match_by_id(self, match_id):
        """Get specific match by ID"""
        try:
            query = 'SELECT * FROM match_history WHERE match_id = ?'
            result = self.db.fetch_one(query, (match_id,))
            
            if result:
                return MatchRecord(
                    result['match_id'],
                    result['match_date'],
                    result['player_character'],
                    result['opponent_character'],
                    result['game_mode'],
                    result['result'],
                    result['match_duration'],
                    result['rounds_won'],
                    result['rounds_lost']
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting match {match_id}: {e}")
            return None
    
    def _validate_match_data(self, match_data):
        """Validate match data before recording"""
        required_fields = ['player_character', 'opponent_character', 'game_mode', 'result']
        
        # Check required fields
        for field in required_fields:
            if field not in match_data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate character names
        if match_data['player_character'] not in self.valid_characters:
            self.logger.warning(f"Invalid player character: {match_data['player_character']}")
            return False
        
        if match_data['opponent_character'] not in self.valid_characters:
            self.logger.warning(f"Invalid opponent character: {match_data['opponent_character']}")
            return False
        
        # Validate game mode
        if match_data['game_mode'] not in self.valid_game_modes:
            self.logger.warning(f"Invalid game mode: {match_data['game_mode']}")
            return False
        
        # Validate result
        if match_data['result'] not in self.valid_results:
            self.logger.warning(f"Invalid result: {match_data['result']}")
            return False
        
        # Validate numeric fields if present
        numeric_fields = ['duration', 'rounds_won', 'rounds_lost']
        for field in numeric_fields:
            if field in match_data:
                try:
                    value = int(match_data[field])
                    if value < 0:
                        self.logger.warning(f"Negative value for {field}: {value}")
                        return False
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid numeric value for {field}: {match_data[field]}")
                    return False
        
        return True
    
    def _cleanup_old_matches_if_needed(self, player_id, threshold=500):
        """Automatically cleanup if player has too many matches"""
        try:
            count_query = 'SELECT COUNT(*) as count FROM match_history WHERE player_id = ?'
            count_result = self.db.fetch_one(count_query, (player_id,))
            
            if count_result and count_result['count'] > threshold:
                self.cleanup_old_matches(player_id, keep_count=400)
                
        except Exception as e:
            self.logger.error(f"Error in automatic cleanup: {e}")
    
    def get_win_streak(self, player_id):
        """Calculate current win streak for a player"""
        try:
            query = '''
                SELECT result FROM match_history
                WHERE player_id = ?
                ORDER BY match_date DESC
                LIMIT 50
            '''
            
            results = self.db.fetch_all(query, (player_id,))
            
            win_streak = 0
            for row in results:
                if row['result'] == 'WIN':
                    win_streak += 1
                else:
                    break
            
            return win_streak
            
        except Exception as e:
            self.logger.error(f"Error calculating win streak for player {player_id}: {e}")
            return 0 
    
    def get_all_matches(self, limit=50):
        """Get match history from all players"""
        try:
            query = '''
                SELECT mh.*, p.name as player_name
                FROM match_history mh
                LEFT JOIN players p ON mh.player_id = p.player_id
                ORDER BY mh.match_date DESC
                LIMIT ?
            '''
            
            results = self.db.fetch_all(query, (limit,))
            
            matches = []
            for row in results:
                # Create a match record with player name included
                match = MatchRecord(
                    row['match_id'],
                    row['match_date'],
                    row['player_character'],
                    row['opponent_character'],
                    row['game_mode'],
                    row['result'],
                    row['match_duration'],
                    row['rounds_won'],
                    row['rounds_lost']
                )
                # Add player name as an attribute
                match.player_name = row['player_name'] if row['player_name'] else f"Player {row['player_id']}"
                matches.append(match)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error getting all matches: {e}")
            return []