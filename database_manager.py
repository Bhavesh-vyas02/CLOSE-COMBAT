import sqlite3
import os
import sys
import logging
from datetime import datetime
import shutil

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # When running in development, use the script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class DatabaseManager:
    def __init__(self, db_name="close_combat.db"):
        """Initialize database connection and create schema if needed"""
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)
        self.connection = None
        self.setup_logging()
        self.connect()
        self.create_schema()
    
    def setup_logging(self):
        """Setup logging for database operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('game.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DatabaseManager')
    
    def connect(self):
        """Establish database connection with error handling"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self.logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {e}")
            raise
    
    def create_schema(self):
        """Create all required tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Players table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT UNIQUE NOT NULL,
                    created_date TEXT NOT NULL,
                    total_playtime INTEGER DEFAULT 0,
                    favorite_character TEXT DEFAULT NULL
                )
            ''')
            
            # Player statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_stats (
                    player_id INTEGER,
                    character_name TEXT,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    total_matches INTEGER DEFAULT 0,
                    PRIMARY KEY (player_id, character_name),
                    FOREIGN KEY (player_id) REFERENCES players (player_id)
                )
            ''')
            
            # Match history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS match_history (
                    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER,
                    match_date TEXT NOT NULL,
                    player_character TEXT NOT NULL,
                    opponent_character TEXT NOT NULL,
                    game_mode TEXT NOT NULL,
                    result TEXT NOT NULL,
                    match_duration INTEGER DEFAULT 0,
                    rounds_won INTEGER DEFAULT 0,
                    rounds_lost INTEGER DEFAULT 0,
                    FOREIGN KEY (player_id) REFERENCES players (player_id)
                )
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    setting_key TEXT,
                    setting_value TEXT,
                    player_id INTEGER DEFAULT NULL,
                    PRIMARY KEY (setting_key, player_id),
                    FOREIGN KEY (player_id) REFERENCES players (player_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_stats_player_id ON player_stats(player_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_history_player_id ON match_history(player_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_history_date ON match_history(match_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_player_id ON settings(player_id)')
            
            self.connection.commit()
            self.logger.info("Database schema created successfully")
            
        except sqlite3.Error as e:
            self.logger.error(f"Schema creation error: {e}")
            self.connection.rollback()
            raise
    
    def execute_query(self, query, params=None):
        """Execute a query with error handling and logging"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            self.logger.error(f"Query execution error: {e}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            self.connection.rollback()
            raise
    
    def fetch_one(self, query, params=None):
        """Fetch single result with error handling"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(f"Fetch one error: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """Fetch all results with error handling"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Fetch all error: {e}")
            return []
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"close_combat_backup_{timestamp}.db"
            
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Backup error: {e}")
            return None
    
    def check_database_integrity(self):
        """Check database integrity and attempt repair if needed"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result[0] == "ok":
                self.logger.info("Database integrity check passed")
                return True
            else:
                self.logger.warning(f"Database integrity issues: {result[0]}")
                return False
        except sqlite3.Error as e:
            self.logger.error(f"Integrity check error: {e}")
            return False
    
    def recover_database(self):
        """Attempt to recover from database corruption"""
        try:
            self.logger.info("Attempting database recovery...")
            
            # Create backup of corrupted database
            corrupted_backup = self.backup_database("corrupted_database_backup.db")
            
            # Close current connection
            if self.connection:
                self.connection.close()
            
            # Remove corrupted database
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            
            # Reconnect and recreate schema
            self.connect()
            self.create_schema()
            
            self.logger.info("Database recovery completed - fresh database created")
            return True
            
        except Exception as e:
            self.logger.error(f"Database recovery failed: {e}")
            return False
    
    def close_connection(self):
        """Close database connection safely"""
        try:
            if self.connection:
                self.connection.close()
                self.logger.info("Database connection closed")
        except sqlite3.Error as e:
            self.logger.error(f"Error closing database: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_connection()

# Global database instance
_db_instance = None

def get_database():
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        try:
            _db_instance = DatabaseManager()
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            # Return None if database initialization fails
            return None
    return _db_instance

def close_database():
    """Close global database instance"""
    global _db_instance
    if _db_instance:
        _db_instance.close_connection()
        _db_instance = None