from database_manager import get_database
import logging
import json
from datetime import datetime

class SettingsManager:
    """Manages game settings and preferences persistence"""
    
    def __init__(self):
        self.db = get_database()
        self.logger = logging.getLogger('SettingsManager')
        
        # Default settings
        self.default_settings = {
            # Global settings (player_id = None)
            'background_music_volume': '0.5',
            'sound_effects_volume': '0.75',
            'master_volume': '1.0',
            'fullscreen': 'False',
            'resolution': '1000x600',
            
            # Player-specific settings (require player_id)
            'background_sound': 'True',
            'player_sound': 'True',
            'preferred_character': 'WARRIOR',
            'control_scheme': 'default',
            'difficulty_preference': 'normal'
        }
        
        # Settings that require player_id
        self.player_specific_settings = {
            'background_sound', 'player_sound', 'preferred_character',
            'control_scheme', 'difficulty_preference'
        }
    
    def save_setting(self, key, value, player_id=None):
        """Store setting value in database"""
        try:
            # Validate setting
            if not self._validate_setting(key, value, player_id):
                return False
            
            # Convert value to string for storage
            value_str = str(value)
            
            # Check if setting already exists
            query = '''
                SELECT setting_value FROM settings
                WHERE setting_key = ? AND 
                      (player_id = ? OR (player_id IS NULL AND ? IS NULL))
            '''
            existing = self.db.fetch_one(query, (key, player_id, player_id))
            
            if existing:
                # Update existing setting
                update_query = '''
                    UPDATE settings
                    SET setting_value = ?
                    WHERE setting_key = ? AND 
                          (player_id = ? OR (player_id IS NULL AND ? IS NULL))
                '''
                self.db.execute_query(update_query, (value_str, key, player_id, player_id))
            else:
                # Insert new setting
                insert_query = '''
                    INSERT INTO settings (setting_key, setting_value, player_id)
                    VALUES (?, ?, ?)
                '''
                self.db.execute_query(insert_query, (key, value_str, player_id))
            
            self.logger.info(f"Saved setting {key}={value} for player {player_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving setting {key}: {e}")
            return False
    
    def get_setting(self, key, default=None, player_id=None):
        """Retrieve setting value from database"""
        try:
            query = '''
                SELECT setting_value FROM settings
                WHERE setting_key = ? AND 
                      (player_id = ? OR (player_id IS NULL AND ? IS NULL))
            '''
            result = self.db.fetch_one(query, (key, player_id, player_id))
            
            if result:
                return self._convert_setting_value(key, result['setting_value'])
            
            # Return default value if not found
            if default is not None:
                return default
            
            # Return system default if available
            if key in self.default_settings:
                return self._convert_setting_value(key, self.default_settings[key])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting setting {key}: {e}")
            return default
    
    def get_all_settings(self, player_id=None):
        """Get all settings for a player or global settings"""
        try:
            if player_id is None:
                # Get global settings only
                query = 'SELECT setting_key, setting_value FROM settings WHERE player_id IS NULL'
                results = self.db.fetch_all(query)
            else:
                # Get player-specific settings
                query = 'SELECT setting_key, setting_value FROM settings WHERE player_id = ?'
                results = self.db.fetch_all(query, (player_id,))
            
            settings = {}
            for row in results:
                key = row['setting_key']
                value = self._convert_setting_value(key, row['setting_value'])
                settings[key] = value
            
            # Add defaults for missing settings
            if player_id is None:
                # Add global defaults
                for key, default_value in self.default_settings.items():
                    if key not in self.player_specific_settings and key not in settings:
                        settings[key] = self._convert_setting_value(key, default_value)
            else:
                # Add player-specific defaults
                for key in self.player_specific_settings:
                    if key not in settings and key in self.default_settings:
                        settings[key] = self._convert_setting_value(key, self.default_settings[key])
            
            return settings
            
        except Exception as e:
            self.logger.error(f"Error getting all settings for player {player_id}: {e}")
            return {}
    
    def reset_settings(self, player_id=None):
        """Reset settings to defaults"""
        try:
            if player_id is None:
                # Reset global settings
                delete_query = 'DELETE FROM settings WHERE player_id IS NULL'
                self.db.execute_query(delete_query)
                
                # Insert default global settings
                for key, value in self.default_settings.items():
                    if key not in self.player_specific_settings:
                        self.save_setting(key, value, None)
            else:
                # Reset player-specific settings
                delete_query = 'DELETE FROM settings WHERE player_id = ?'
                self.db.execute_query(delete_query, (player_id,))
                
                # Insert default player settings
                for key in self.player_specific_settings:
                    if key in self.default_settings:
                        self.save_setting(key, self.default_settings[key], player_id)
            
            self.logger.info(f"Reset settings for player {player_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting settings for player {player_id}: {e}")
            return False
    
    def delete_setting(self, key, player_id=None):
        """Delete a specific setting"""
        try:
            query = '''
                DELETE FROM settings
                WHERE setting_key = ? AND 
                      (player_id = ? OR (player_id IS NULL AND ? IS NULL))
            '''
            self.db.execute_query(query, (key, player_id, player_id))
            
            self.logger.info(f"Deleted setting {key} for player {player_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting setting {key}: {e}")
            return False
    
    def backup_settings(self, player_id=None):
        """Create a backup of settings as JSON"""
        try:
            settings = self.get_all_settings(player_id)
            
            backup_data = {
                'player_id': player_id,
                'backup_date': datetime.now().isoformat(),
                'settings': settings
            }
            
            return json.dumps(backup_data, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error backing up settings: {e}")
            return None
    
    def restore_settings(self, backup_json, player_id=None):
        """Restore settings from JSON backup"""
        try:
            backup_data = json.loads(backup_json)
            
            if 'settings' not in backup_data:
                self.logger.error("Invalid backup format")
                return False
            
            # Clear existing settings
            self.reset_settings(player_id)
            
            # Restore settings
            for key, value in backup_data['settings'].items():
                self.save_setting(key, value, player_id)
            
            self.logger.info(f"Restored settings for player {player_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring settings: {e}")
            return False
    
    def get_sound_settings(self, player_id=None):
        """Get all sound-related settings"""
        try:
            sound_settings = {}
            
            # Global sound settings
            sound_settings['background_music_volume'] = self.get_setting('background_music_volume', 0.5)
            sound_settings['sound_effects_volume'] = self.get_setting('sound_effects_volume', 0.75)
            sound_settings['master_volume'] = self.get_setting('master_volume', 1.0)
            
            # Player-specific sound settings
            if player_id is not None:
                sound_settings['background_sound'] = self.get_setting('background_sound', True, player_id)
                sound_settings['player_sound'] = self.get_setting('player_sound', True, player_id)
            
            return sound_settings
            
        except Exception as e:
            self.logger.error(f"Error getting sound settings: {e}")
            return {}
    
    def apply_sound_settings(self, pygame_mixer, player_id=None):
        """Apply sound settings to pygame mixer"""
        try:
            sound_settings = self.get_sound_settings(player_id)
            
            # Apply master volume
            master_vol = sound_settings.get('master_volume', 1.0)
            
            # Apply background music volume
            bg_vol = sound_settings.get('background_music_volume', 0.5)
            bg_enabled = sound_settings.get('background_sound', True)
            
            if bg_enabled:
                pygame_mixer.music.set_volume(bg_vol * master_vol)
            else:
                pygame_mixer.music.set_volume(0.0)
            
            # Return sound effects settings for manual application
            sfx_vol = sound_settings.get('sound_effects_volume', 0.75)
            sfx_enabled = sound_settings.get('player_sound', True)
            
            return {
                'effects_volume': sfx_vol * master_vol if sfx_enabled else 0.0,
                'effects_enabled': sfx_enabled
            }
            
        except Exception as e:
            self.logger.error(f"Error applying sound settings: {e}")
            return {'effects_volume': 0.5, 'effects_enabled': True}
    
    def _validate_setting(self, key, value, player_id):
        """Validate setting key and value"""
        # Check if player-specific setting has player_id
        if key in self.player_specific_settings and player_id is None:
            self.logger.warning(f"Player-specific setting {key} requires player_id")
            return False
        
        # Validate specific setting types
        if key in ['background_sound', 'player_sound', 'fullscreen']:
            if not isinstance(value, (bool, str)):
                return False
            if isinstance(value, str) and value.lower() not in ['true', 'false']:
                return False
        
        elif key in ['background_music_volume', 'sound_effects_volume', 'master_volume']:
            try:
                vol = float(value)
                if not (0.0 <= vol <= 1.0):
                    return False
            except (ValueError, TypeError):
                return False
        
        elif key == 'preferred_character':
            valid_chars = ['WARRIOR', 'WIZARD', 'HUNTRESS', 'KING', 'HERO_KNIGHT', 'MARTIAL_HERO']
            if value not in valid_chars:
                return False
        
        elif key == 'resolution':
            if not isinstance(value, str) or 'x' not in value:
                return False
            try:
                width, height = value.split('x')
                int(width)
                int(height)
            except (ValueError, AttributeError):
                return False
        
        return True
    
    def _convert_setting_value(self, key, value_str):
        """Convert string value to appropriate type"""
        if key in ['background_sound', 'player_sound', 'fullscreen']:
            return value_str.lower() == 'true'
        
        elif key in ['background_music_volume', 'sound_effects_volume', 'master_volume']:
            try:
                return float(value_str)
            except (ValueError, TypeError):
                return 0.5
        
        else:
            return value_str
    
    def initialize_default_settings(self):
        """Initialize default global settings if they don't exist"""
        try:
            for key, value in self.default_settings.items():
                if key not in self.player_specific_settings:
                    # Check if setting exists
                    existing = self.get_setting(key)
                    if existing is None:
                        self.save_setting(key, value, None)
            
            self.logger.info("Initialized default settings")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing default settings: {e}")
            return False