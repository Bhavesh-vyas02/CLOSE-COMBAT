# Design Document

## Overview

The SQLite database system will be implemented as a centralized data management layer for the Close Combat game. The system uses a single SQLite database file that will be created in the game directory and will handle all persistent data operations including player statistics, match history, settings, and leaderboards. The design follows a modular approach with a dedicated database manager class that provides clean interfaces for all game components.

## Architecture

### Database Schema Design

The system uses four main tables to organize data efficiently:

**players table:**
- `player_id` (INTEGER PRIMARY KEY): Unique identifier for each player
- `player_name` (TEXT UNIQUE): Custom player name (max 20 characters)
- `created_date` (TEXT): ISO format timestamp of profile creation
- `total_playtime` (INTEGER): Total seconds played
- `favorite_character` (TEXT): Most used character name

**player_stats table:**
- `player_id` (INTEGER): Foreign key to players table
- `character_name` (TEXT): Character used (WARRIOR, WIZARD, etc.)
- `wins` (INTEGER): Number of wins with this character
- `losses` (INTEGER): Number of losses with this character
- `draws` (INTEGER): Number of draws with this character
- `total_matches` (INTEGER): Computed total matches for this character
- PRIMARY KEY: (player_id, character_name)

**match_history table:**
- `match_id` (INTEGER PRIMARY KEY): Unique match identifier
- `player_id` (INTEGER): Foreign key to players table
- `match_date` (TEXT): ISO format timestamp
- `player_character` (TEXT): Character used by player
- `opponent_character` (TEXT): Opponent's character
- `game_mode` (TEXT): 'PvP' or 'PvC'
- `result` (TEXT): 'WIN', 'LOSS', or 'DRAW'
- `match_duration` (INTEGER): Match length in seconds
- `rounds_won` (INTEGER): Rounds won by player
- `rounds_lost` (INTEGER): Rounds lost by player

**settings table:**
- `setting_key` (TEXT PRIMARY KEY): Setting identifier
- `setting_value` (TEXT): Setting value as string
- `player_id` (INTEGER): Foreign key to players table (for player-specific settings)

### Component Architecture

```
Game Components
├── DatabaseManager (Core)
│   ├── Connection Management
│   ├── Schema Creation/Migration
│   └── Error Handling
├── PlayerManager
│   ├── Profile Creation/Updates
│   ├── Statistics Calculation
│   └── Leaderboard Generation
├── MatchTracker
│   ├── Match Recording
│   ├── History Retrieval
│   └── Performance Analytics
└── SettingsManager
    ├── Preference Storage
    ├── Setting Retrieval
    └── Default Value Management
```

## Components and Interfaces

### DatabaseManager Class

**Purpose:** Core database operations and connection management

**Key Methods:**
- `__init__(db_path)`: Initialize database connection and create schema
- `execute_query(query, params)`: Execute SQL with error handling
- `fetch_one(query, params)`: Fetch single result
- `fetch_all(query, params)`: Fetch multiple results
- `close_connection()`: Clean database shutdown
- `backup_database()`: Create database backup

**Error Handling:** All database operations wrapped in try-catch blocks with logging

### PlayerManager Class

**Purpose:** Player profile and statistics management

**Key Methods:**
- `create_player(name)`: Create new player profile
- `get_player_stats(player_id)`: Retrieve comprehensive player statistics
- `update_character_stats(player_id, character, result)`: Update win/loss records
- `get_leaderboard(limit=10)`: Generate leaderboard rankings
- `get_player_by_name(name)`: Find player by name
- `update_playtime(player_id, seconds)`: Track total playtime

**Statistics Calculations:**
- Win percentage: (wins / total_matches) * 100
- Favorite character: Character with most matches played
- Overall ranking: Based on win percentage with total wins tiebreaker

### MatchTracker Class

**Purpose:** Match recording and history management

**Key Methods:**
- `record_match(player_id, match_data)`: Save match results
- `get_match_history(player_id, limit=50)`: Retrieve player's match history
- `get_recent_matches(days=7)`: Get matches from last N days
- `calculate_match_duration(start_time, end_time)`: Compute match length
- `cleanup_old_matches(keep_count=1000)`: Remove oldest matches when limit reached

**Match Data Structure:**
```python
match_data = {
    'player_character': str,
    'opponent_character': str,
    'game_mode': 'PvP' | 'PvC',
    'result': 'WIN' | 'LOSS' | 'DRAW',
    'rounds_won': int,
    'rounds_lost': int,
    'duration': int  # seconds
}
```

### SettingsManager Class

**Purpose:** Game settings persistence

**Key Methods:**
- `save_setting(key, value, player_id=None)`: Store setting value
- `get_setting(key, default=None, player_id=None)`: Retrieve setting
- `get_all_settings(player_id=None)`: Get all settings for player
- `reset_settings(player_id=None)`: Reset to defaults

**Setting Categories:**
- Global settings: Background music volume, sound effects volume
- Player settings: Preferred character, control preferences
- Game settings: Difficulty level, round duration

## Data Models

### Player Profile Model
```python
class PlayerProfile:
    def __init__(self, player_id, name, created_date, total_playtime, favorite_character):
        self.player_id = player_id
        self.name = name
        self.created_date = created_date
        self.total_playtime = total_playtime
        self.favorite_character = favorite_character
        self.stats = {}  # Character-specific statistics
        self.overall_stats = {}  # Overall win/loss/draw counts
```

### Match Record Model
```python
class MatchRecord:
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
```

## Error Handling

### Database Connection Errors
- **Missing Database:** Automatically create new database with schema
- **Corrupted Database:** Backup existing, create fresh database
- **Permission Errors:** Log error, attempt alternative location
- **Disk Space:** Cleanup old records, notify user

### Data Validation
- **Player Names:** Check length (1-20 chars), uniqueness, valid characters
- **Match Data:** Validate character names, results, numeric ranges
- **Settings:** Type checking, range validation for numeric settings

### Recovery Mechanisms
- **Transaction Rollback:** All multi-step operations use transactions
- **Backup System:** Daily automatic backups of database
- **Default Values:** Fallback to defaults when settings missing
- **Graceful Degradation:** Game continues if database unavailable

## Testing Strategy

### Unit Tests
- Database schema creation and migration
- CRUD operations for all tables
- Statistics calculation accuracy
- Setting persistence and retrieval
- Error handling for various failure scenarios

### Integration Tests
- Game integration with database operations
- Performance testing with large datasets
- Concurrent access handling
- Database file portability across systems

### Performance Tests
- Query execution time benchmarks
- Memory usage monitoring
- Database file size growth patterns
- Cleanup operation efficiency

### User Acceptance Tests
- Player profile creation workflow
- Match recording during actual gameplay
- Settings persistence across game sessions
- Leaderboard accuracy and updates
- Database recovery from corruption

## Security Considerations

### Data Protection
- **SQL Injection Prevention:** All queries use parameterized statements
- **Input Validation:** Sanitize all user inputs before database operations
- **File Permissions:** Database file created with appropriate access controls

### Privacy
- **Local Storage:** All data stored locally, no network transmission
- **Data Minimization:** Only collect necessary game-related data
- **User Control:** Players can reset/delete their data

## Performance Optimization

### Database Optimization
- **Indexes:** Create indexes on frequently queried columns (player_id, match_date)
- **Query Optimization:** Use efficient SQL patterns, avoid N+1 queries
- **Connection Pooling:** Reuse database connections where possible
- **Batch Operations:** Group multiple inserts/updates when possible

### Memory Management
- **Result Set Limits:** Limit query results to prevent memory issues
- **Connection Cleanup:** Properly close database connections
- **Cache Strategy:** Cache frequently accessed data (player profiles, settings)

### File Management
- **Database Size Limits:** Implement automatic cleanup of old data
- **Compression:** Use SQLite's built-in compression features
- **Backup Rotation:** Keep limited number of backup files