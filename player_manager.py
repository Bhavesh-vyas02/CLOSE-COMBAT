from database_manager import get_database
from datetime import datetime
import logging

class PlayerProfile:
    """Data model for player profile information"""
    def __init__(self, player_id, name, created_date, total_playtime, favorite_character):
        self.player_id = player_id
        self.name = name
        self.created_date = created_date
        self.total_playtime = total_playtime
        self.favorite_character = favorite_character
        self.stats = {}  # Character-specific statistics
        self.overall_stats = {}  # Overall win/loss/draw counts

class PlayerManager:
    """Manages player profiles, statistics, and leaderboards"""
    
    def __init__(self):
        self.db = get_database()
        self.logger = logging.getLogger('PlayerManager')
        
        if self.db is None:
            self.logger.error("Database connection is None in PlayerManager")
            raise Exception("Database not available")
        
        # Valid character names
        self.valid_characters = [
            'WARRIOR', 'WIZARD', 'HUNTRESS', 'KING', 'HERO_KNIGHT', 'MARTIAL_HERO'
        ]
    
    def create_player(self, name):
        """Create a new player profile"""
        try:
            # Validate player name
            if not self.validate_player_name(name):
                return None
            
            # Check if name already exists
            if self.get_player_by_name(name):
                self.logger.warning(f"Player name '{name}' already exists")
                return None
            
            # Create player record
            created_date = datetime.now().isoformat()
            query = '''
                INSERT INTO players (player_name, created_date, total_playtime, favorite_character)
                VALUES (?, ?, 0, NULL)
            '''
            cursor = self.db.execute_query(query, (name, created_date))
            player_id = cursor.lastrowid
            
            # Initialize default settings for the player (non-critical)
            try:
                self._initialize_player_settings(player_id)
            except Exception as settings_error:
                self.logger.warning(f"Failed to initialize settings for player {player_id}: {settings_error}")
            
            self.logger.info(f"Created new player: {name} (ID: {player_id})")
            return player_id
            
        except Exception as e:
            self.logger.error(f"Error creating player '{name}': {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def validate_player_name(self, name):
        """Validate player name according to requirements"""
        if not name or len(name.strip()) == 0:
            return False
        
        name = name.strip()
        if len(name) > 20:
            return False
        
        # Check for valid characters (letters, numbers, spaces, basic punctuation)
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .-_')
        if not all(c in allowed_chars for c in name):
            return False
        return True
    
    def get_player_by_name(self, name):
        """Find player by name"""
        try:
            query = 'SELECT * FROM players WHERE player_name = ?'
            result = self.db.fetch_one(query, (name,))
            
            if result:
                return PlayerProfile(
                    result['player_id'],
                    result['player_name'],
                    result['created_date'],
                    result['total_playtime'],
                    result['favorite_character']
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding player '{name}': {e}")
            return None
    
    def get_player_by_id(self, player_id):
        """Get player by ID"""
        try:
            query = 'SELECT * FROM players WHERE player_id = ?'
            result = self.db.fetch_one(query, (player_id,))
            
            if result:
                return PlayerProfile(
                    result['player_id'],
                    result['player_name'],
                    result['created_date'],
                    result['total_playtime'],
                    result['favorite_character']
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding player ID {player_id}: {e}")
            return None
    
    def get_player_stats(self, player_id):
        """Retrieve comprehensive player statistics"""
        try:
            player = self.get_player_by_id(player_id)
            if not player:
                return None
            
            # Get character-specific stats
            query = '''
                SELECT character_name, wins, losses, draws, total_matches
                FROM player_stats
                WHERE player_id = ?
            '''
            char_stats = self.db.fetch_all(query, (player_id,))
            
            # Calculate overall statistics
            total_wins = sum(row['wins'] for row in char_stats)
            total_losses = sum(row['losses'] for row in char_stats)
            total_draws = sum(row['draws'] for row in char_stats)
            total_matches = sum(row['total_matches'] for row in char_stats)
            
            win_percentage = (total_wins / total_matches * 100) if total_matches > 0 else 0
            
            # Build character stats dictionary
            player.stats = {
                row['character_name']: {
                    'wins': row['wins'],
                    'losses': row['losses'],
                    'draws': row['draws'],
                    'total_matches': row['total_matches'],
                    'win_percentage': (row['wins'] / row['total_matches'] * 100) if row['total_matches'] > 0 else 0
                }
                for row in char_stats
            }
            
            # Overall stats
            player.overall_stats = {
                'total_wins': total_wins,
                'total_losses': total_losses,
                'total_draws': total_draws,
                'total_matches': total_matches,
                'win_percentage': win_percentage
            }
            
            # Update favorite character
            if char_stats:
                favorite = max(char_stats, key=lambda x: x['total_matches'])
                player.favorite_character = favorite['character_name']
                self._update_favorite_character(player_id, favorite['character_name'])
            
            return player
            
        except Exception as e:
            self.logger.error(f"Error getting stats for player {player_id}: {e}")
            return None
    
    def update_character_stats(self, player_id, character, result):
        """Update win/loss records for a character"""
        try:
            if character not in self.valid_characters:
                self.logger.warning(f"Invalid character: {character}")
                return False
            
            if result not in ['WIN', 'LOSS', 'DRAW']:
                self.logger.warning(f"Invalid result: {result}")
                return False
            
            # Check if record exists
            query = '''
                SELECT wins, losses, draws, total_matches
                FROM player_stats
                WHERE player_id = ? AND character_name = ?
            '''
            existing = self.db.fetch_one(query, (player_id, character))
            
            if existing:
                # Update existing record
                wins = existing['wins']
                losses = existing['losses']
                draws = existing['draws']
                total = existing['total_matches']
                
                if result == 'WIN':
                    wins += 1
                elif result == 'LOSS':
                    losses += 1
                else:  # DRAW
                    draws += 1
                
                total += 1
                
                update_query = '''
                    UPDATE player_stats
                    SET wins = ?, losses = ?, draws = ?, total_matches = ?
                    WHERE player_id = ? AND character_name = ?
                '''
                self.db.execute_query(update_query, (wins, losses, draws, total, player_id, character))
                
            else:
                # Create new record
                wins = 1 if result == 'WIN' else 0
                losses = 1 if result == 'LOSS' else 0
                draws = 1 if result == 'DRAW' else 0
                
                insert_query = '''
                    INSERT INTO player_stats (player_id, character_name, wins, losses, draws, total_matches)
                    VALUES (?, ?, ?, ?, ?, 1)
                '''
                self.db.execute_query(insert_query, (player_id, character, wins, losses, draws))
            
            self.logger.info(f"Updated stats for player {player_id}, character {character}: {result}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating character stats: {e}")
            return False
    
    def get_leaderboard(self, limit=10):
        """Generate leaderboard rankings"""
        try:
            query = '''
                SELECT 
                    p.player_id,
                    p.player_name,
                    SUM(ps.wins) as total_wins,
                    SUM(ps.losses) as total_losses,
                    SUM(ps.draws) as total_draws,
                    SUM(ps.total_matches) as total_matches,
                    CASE 
                        WHEN SUM(ps.total_matches) > 0 
                        THEN ROUND((SUM(ps.wins) * 100.0 / SUM(ps.total_matches)), 2)
                        ELSE 0 
                    END as win_percentage
                FROM players p
                LEFT JOIN player_stats ps ON p.player_id = ps.player_id
                GROUP BY p.player_id, p.player_name
                HAVING SUM(ps.total_matches) >= 10
                ORDER BY win_percentage DESC, total_wins DESC
                LIMIT ?
            '''
            
            results = self.db.fetch_all(query, (limit,))
            
            leaderboard = []
            for i, row in enumerate(results, 1):
                leaderboard.append({
                    'rank': i,
                    'player_id': row['player_id'],
                    'player_name': row['player_name'],
                    'total_wins': row['total_wins'],
                    'total_losses': row['total_losses'],
                    'total_draws': row['total_draws'],
                    'total_matches': row['total_matches'],
                    'win_percentage': row['win_percentage']
                })
            
            return leaderboard
            
        except Exception as e:
            self.logger.error(f"Error generating leaderboard: {e}")
            return []
    
    def update_playtime(self, player_id, seconds):
        """Update total playtime for a player"""
        try:
            query = '''
                UPDATE players
                SET total_playtime = total_playtime + ?
                WHERE player_id = ?
            '''
            self.db.execute_query(query, (seconds, player_id))
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating playtime for player {player_id}: {e}")
            return False
    
    def update_player_name(self, player_id, new_name):
        """Update player name"""
        try:
            if not self.validate_player_name(new_name):
                return False
            
            # Check if name already exists (excluding current player)
            existing = self.get_player_by_name(new_name)
            if existing and existing.player_id != player_id:
                return False
            
            query = 'UPDATE players SET player_name = ? WHERE player_id = ?'
            self.db.execute_query(query, (new_name, player_id))
            
            self.logger.info(f"Updated player {player_id} name to: {new_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating player name: {e}")
            return False
    
    def _update_favorite_character(self, player_id, character):
        """Internal method to update favorite character"""
        try:
            query = 'UPDATE players SET favorite_character = ? WHERE player_id = ?'
            self.db.execute_query(query, (character, player_id))
        except Exception as e:
            self.logger.error(f"Error updating favorite character: {e}")
    
    def _initialize_player_settings(self, player_id):
        """Initialize default settings for new player"""
        try:
            default_settings = [
                ('background_sound', 'True'),
                ('player_sound', 'True'),
                ('preferred_character', 'WARRIOR')
            ]
            
            for key, value in default_settings:
                query = '''
                    INSERT INTO settings (setting_key, setting_value, player_id)
                    VALUES (?, ?, ?)
                '''
                self.db.execute_query(query, (key, value, player_id))
                
        except Exception as e:
            self.logger.error(f"Error initializing player settings: {e}")
    
    def get_all_players(self):
        """Get all players for admin purposes"""
        try:
            query = 'SELECT * FROM players ORDER BY created_date DESC'
            results = self.db.fetch_all(query)
            
            players = []
            for row in results:
                players.append(PlayerProfile(
                    row['player_id'],
                    row['player_name'],
                    row['created_date'],
                    row['total_playtime'],
                    row['favorite_character']
                ))
            
            return players
            
        except Exception as e:
            self.logger.error(f"Error getting all players: {e}")
            return []