import pygame
import sys
import os
from game_integration import get_game_session

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# High Contrast Colors for Maximum Readability
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
YELLOW = (255, 255, 150)
GREEN = (150, 255, 150)
BLUE = (150, 200, 255)
PURPLE = (255, 150, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (240, 240, 240)
BRIGHT_WHITE = (255, 255, 255)
# Much darker background for better text contrast
CARD_BG = (15, 15, 25)
CARD_BORDER = (100, 100, 120)
# New colors for better visibility
WIN_GREEN = (0, 255, 0)
LOSS_RED = (255, 50, 50)
DRAW_YELLOW = (255, 255, 0)
HIGHLIGHT_BLUE = (100, 200, 255)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, surface):
        color = YELLOW if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=12)
        
        button_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 24)
        text_surface = button_font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class PlayerStatsScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_session = get_game_session()
        
        # Much Larger Fonts for Maximum Readability
        self.title_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 60)
        self.header_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 42)
        self.text_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 32)
        self.small_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 28)
        self.big_text_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 38)
        
        # Back button positioned to not overlap content
        self.back_button = Button(50, 50, 120, 50, "BACK", RED)
        
        # Load background
        try:
            self.bg_image = pygame.image.load(resource_path("assets/images/background/main_menu_bg.jpg")).convert_alpha()
        except:
            self.bg_image = None

    def draw(self, surface):
        # Draw solid dark background for maximum contrast
        surface.fill(BLACK)
        
        # Draw title with better positioning
        title_text = "PLAYER STATISTICS"
        title_surface = self.title_font.render(title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_surface, title_rect)
        
        # Draw back button first (top-left)
        self.back_button.draw(surface)
        
        if not self.game_session:
            error_text = self.text_font.render("Database not available", True, RED)
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(error_text, error_rect)
            return
        
        # Get all players from the database
        try:
            from player_manager import PlayerManager
            player_mgr = PlayerManager()
            all_players = player_mgr.get_all_players()
            
            if not all_players:
                no_data_text = self.text_font.render("No players found - play some matches first!", True, WHITE)
                no_data_rect = no_data_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                surface.blit(no_data_text, no_data_rect)
                return
        except Exception as e:
            error_text = self.text_font.render(f"Error loading player data: {str(e)}", True, RED)
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(error_text, error_rect)
            return
        
        # Display all players' statistics
        y_pos = 140
        
        # Header
        stats_header = self.header_font.render("ALL PLAYERS STATISTICS", True, HIGHLIGHT_BLUE)
        header_rect = stats_header.get_rect(center=(self.screen_width // 2, y_pos))
        surface.blit(stats_header, header_rect)
        y_pos += 60
        
        # Display each player's information
        for player in all_players:
            try:
                # Get player stats
                player_stats = player_mgr.get_player_stats(player.player_id)
                
                # Player name header
                player_header = self.text_font.render(f"PLAYER: {player.name}", True, YELLOW)
                surface.blit(player_header, (100, y_pos))
                y_pos += 40
                
                if player_stats and player_stats.overall_stats:
                    overall = player_stats.overall_stats
                    
                    # Player's overall stats
                    total_matches = overall.get('total_matches', 0)
                    wins = overall.get('total_wins', 0)
                    losses = overall.get('total_losses', 0)
                    draws = overall.get('total_draws', 0)
                    win_rate = overall.get('win_percentage', 0)
                    
                    # Display stats in columns
                    stats_text = f"Matches: {total_matches}  |  Wins: {wins}  |  Losses: {losses}  |  Draws: {draws}  |  Win Rate: {win_rate:.1f}%"
                    color = WIN_GREEN if win_rate >= 50 else DRAW_YELLOW if win_rate >= 30 else LOSS_RED
                    stats_surface = self.small_font.render(stats_text, True, color)
                    surface.blit(stats_surface, (120, y_pos))
                    y_pos += 35
                    
                    # Character performance for this player
                    if player_stats.stats:
                        char_text = "Characters: "
                        for char_name, char_stats in player_stats.stats.items():
                            display_name = self._get_display_name(char_name)
                            char_wins = char_stats.get('wins', 0)
                            char_losses = char_stats.get('losses', 0)
                            char_text += f"{display_name}({char_wins}W-{char_losses}L) "
                        
                        char_surface = self.small_font.render(char_text, True, WHITE)
                        surface.blit(char_surface, (120, y_pos))
                        y_pos += 35
                else:
                    no_stats_text = self.small_font.render("No matches played yet", True, GRAY)
                    surface.blit(no_stats_text, (120, y_pos))
                    y_pos += 35
                
                y_pos += 20  # Space between players
                
            except Exception as e:
                error_text = self.small_font.render(f"Error loading stats for {player.name}", True, RED)
                surface.blit(error_text, (120, y_pos))
                y_pos += 40
    
    def _format_playtime(self, seconds):
        """Format playtime in seconds to readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _get_display_name(self, char_name):
        """Convert database character name to display name"""
        display_names = {
            "WARRIOR": "WARRIOR",
            "WIZARD": "WIZARD",
            "HUNTRESS": "HUNTER",
            "KING": "KING",
            "HERO_KNIGHT": "KNIGHT",
            "MARTIAL_HERO": "MARTIAL"
        }
        return display_names.get(char_name, char_name)
    
    def handle_event(self, event):
        if self.back_button.handle_event(event):
            return "BACK"
        return None

class MatchHistoryScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_session = get_game_session()
        
        # Much Larger Fonts for Better Readability
        self.title_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 60)
        self.header_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 32)
        self.text_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 26)
        
        # Back button positioned to not overlap
        self.back_button = Button(50, 50, 120, 50, "BACK", RED)
        
        # Scrolling
        self.scroll_offset = 0
        self.max_visible_matches = 5  # Reduced for better spacing with player names
        
        # Load background
        try:
            self.bg_image = pygame.image.load(resource_path("assets/images/background/main_menu_bg.jpg")).convert_alpha()
        except:
            self.bg_image = None

    def draw(self, surface):
        # Draw solid dark background for maximum contrast
        surface.fill(BLACK)
        
        # Draw title
        title_text = "MATCH HISTORY"
        title_surface = self.title_font.render(title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_surface, title_rect)
        
        # Draw back button first
        self.back_button.draw(surface)
        
        if not self.game_session:
            error_text = self.text_font.render("Database not available", True, RED)
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(error_text, error_rect)
            return
        
        # Get match history from all players
        try:
            from match_tracker import MatchTracker
            match_tracker = MatchTracker()
            matches = match_tracker.get_all_matches(limit=50)
            
            if not matches:
                no_data_text = self.text_font.render("No match history available - play some matches first!", True, WHITE)
                no_data_rect = no_data_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                surface.blit(no_data_text, no_data_rect)
                return
        except Exception as e:
            error_text = self.text_font.render(f"Error loading match history: {str(e)}", True, RED)
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(error_text, error_rect)
            return
        
        # Display matches in a much clearer format
        y_pos = 140
        
        # Header
        header_text = self.header_font.render("Recent Matches (Use UP/DOWN arrows to scroll)", True, HIGHLIGHT_BLUE)
        header_rect = header_text.get_rect(center=(self.screen_width // 2, y_pos))
        surface.blit(header_text, header_rect)
        y_pos += 60
        
        # Display matches with much clearer information
        visible_matches = matches[self.scroll_offset:self.scroll_offset + self.max_visible_matches]
        
        for i, match in enumerate(visible_matches):
            match_y = y_pos + i * 90
            
            # Match date and player info
            date_str = match.date[:10] if match.date else "Unknown Date"
            player_name = getattr(match, 'player_name', 'Unknown Player')
            
            header_text = f"Date: {date_str} | Player: {player_name}"
            header_surface = self.text_font.render(header_text, True, WHITE)
            surface.blit(header_surface, (100, match_y))
            
            # Match details showing both players clearly
            player1_char = self._get_display_name(match.player_character)
            player2_char = self._get_display_name(match.opponent_character)
            
            # Display match with clear player identification
            match_text = f"{player_name} ({player1_char}) vs OPPONENT ({player2_char})"
            match_surface = self.text_font.render(match_text, True, HIGHLIGHT_BLUE)
            surface.blit(match_surface, (100, match_y + 30))
            
            # Result showing who won with player names
            result_text = ""
            result_color = WHITE
            if match.result == 'WIN':
                result_text = f"🏆 {player_name} WON! Final Score: {match.rounds_won}-{match.rounds_lost}"
                result_color = WIN_GREEN
            elif match.result == 'LOSS':
                result_text = f"🏆 OPPONENT WON! Final Score: {match.rounds_lost}-{match.rounds_won}"
                result_color = LOSS_RED
            else:
                result_text = f"🤝 DRAW! Final Score: {match.rounds_won}-{match.rounds_lost}"
                result_color = DRAW_YELLOW
            
            result_surface = self.text_font.render(result_text, True, result_color)
            surface.blit(result_surface, (100, match_y + 55))
            
            # Duration and game mode
            duration = f"Duration: {match.duration}s" if match.duration else "Duration: Unknown"
            game_mode = f"Mode: {match.game_mode}"
            info_text = f"{duration} | {game_mode}"
            info_surface = self.small_font.render(info_text, True, GRAY)
            surface.blit(info_surface, (600, match_y + 30))
        
        # Draw scroll indicators if needed
        if len(matches) > self.max_visible_matches:
            if self.scroll_offset > 0:
                up_text = self.text_font.render("▲ Press UP arrow to scroll up", True, YELLOW)
                surface.blit(up_text, (300, self.screen_height - 100))
            
            if self.scroll_offset + self.max_visible_matches < len(matches):
                down_text = self.text_font.render("▼ Press DOWN arrow to scroll down", True, YELLOW)
                surface.blit(down_text, (300, self.screen_height - 70))
    
    def _get_display_name(self, char_name):
        """Convert database character name to display name"""
        display_names = {
            "WARRIOR": "WARRIOR",
            "WIZARD": "WIZARD", 
            "HUNTRESS": "HUNTER",
            "KING": "KING",
            "HERO_KNIGHT": "KNIGHT",
            "MARTIAL_HERO": "MARTIAL"
        }
        return display_names.get(char_name, char_name)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            matches = self.game_session.get_match_history(limit=50) if self.game_session else []
            if event.key == pygame.K_UP and self.scroll_offset > 0:
                self.scroll_offset -= 1
            elif event.key == pygame.K_DOWN and self.scroll_offset + self.max_visible_matches < len(matches):
                self.scroll_offset += 1
        
        if self.back_button.handle_event(event):
            return "BACK"
        return None

class LeaderboardScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_session = get_game_session()
        
        # Enhanced Fonts for Better Readability
        self.title_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 52)
        self.header_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 30)
        self.text_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 24)
        self.rank_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 36)
        
        # Back button positioned to not overlap
        self.back_button = Button(50, 50, 120, 50, "BACK", RED)
        
        # Load background
        try:
            self.bg_image = pygame.image.load(resource_path("assets/images/background/main_menu_bg.jpg")).convert_alpha()
        except:
            self.bg_image = None

    def draw(self, surface):
        # Draw solid dark background for maximum contrast
        surface.fill(BLACK)
        
        # Draw title
        title_text = "LEADERBOARD"
        title_surface = self.title_font.render(title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_surface, title_rect)
        
        # Draw back button first
        self.back_button.draw(surface)
        
        if not self.game_session:
            error_text = self.text_font.render("Database not available", True, RED)
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(error_text, error_rect)
            return
        
        # Get leaderboard data
        leaderboard = self.game_session.get_leaderboard(limit=10)
        if not leaderboard:
            no_data_text = self.text_font.render("No leaderboard data available", True, WHITE)
            no_data_rect = no_data_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
            surface.blit(no_data_text, no_data_rect)
            
            requirement_text = self.text_font.render("(Players need 10+ matches to qualify)", True, GRAY)
            requirement_rect = requirement_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
            surface.blit(requirement_text, requirement_rect)
            
            self.back_button.draw(surface)
            return
        
        # Create leaderboard container with better layout
        table_y = 130
        table_height = 420
        table_rect = pygame.Rect(50, table_y, self.screen_width - 100, table_height)
        pygame.draw.rect(surface, CARD_BG, table_rect, border_radius=15)
        pygame.draw.rect(surface, CARD_BORDER, table_rect, 3, border_radius=15)
        
        # Draw table headers with better spacing
        header_y = table_y + 20
        headers = ["RANK", "PLAYER NAME", "WIN RATE", "WINS", "LOSSES", "MATCHES"]
        header_positions = [90, 200, 400, 520, 620, 750]
        
        for header, x_pos in zip(headers, header_positions):
            header_surface = self.header_font.render(header, True, YELLOW)
            surface.blit(header_surface, (x_pos, header_y))
        
        # Draw separator line
        pygame.draw.line(surface, CARD_BORDER, (70, header_y + 40), (self.screen_width - 70, header_y + 40), 3)
        
        # Draw leaderboard entries with improved styling
        entry_start_y = header_y + 60
        for i, entry in enumerate(leaderboard):
            row_y = entry_start_y + i * 50
            
            # Enhanced row backgrounds with podium highlighting
            row_rect = pygame.Rect(60, row_y - 10, self.screen_width - 120, 45)
            
            if entry['rank'] <= 3:
                # Special highlighting for top 3
                if entry['rank'] == 1:
                    pygame.draw.rect(surface, (40, 30, 0), row_rect, border_radius=8)  # Gold background
                    pygame.draw.rect(surface, (255, 215, 0), row_rect, 2, border_radius=8)  # Gold border
                elif entry['rank'] == 2:
                    pygame.draw.rect(surface, (30, 30, 40), row_rect, border_radius=8)  # Silver background
                    pygame.draw.rect(surface, (192, 192, 192), row_rect, 2, border_radius=8)  # Silver border
                elif entry['rank'] == 3:
                    pygame.draw.rect(surface, (40, 25, 15), row_rect, border_radius=8)  # Bronze background
                    pygame.draw.rect(surface, (205, 127, 50), row_rect, 2, border_radius=8)  # Bronze border
            else:
                # Regular alternating colors
                if i % 2 == 0:
                    pygame.draw.rect(surface, (35, 35, 45), row_rect, border_radius=8)
            
            # Enhanced colors for top 3
            rank_color = BRIGHT_WHITE
            player_color = BRIGHT_WHITE
            if entry['rank'] == 1:
                rank_color = (255, 215, 0)  # Gold
                player_color = (255, 235, 100)  # Light gold
            elif entry['rank'] == 2:
                rank_color = (192, 192, 192)  # Silver
                player_color = (220, 220, 220)  # Light silver
            elif entry['rank'] == 3:
                rank_color = (205, 127, 50)  # Bronze
                player_color = (225, 160, 100)  # Light bronze
            
            # Entry data with better formatting
            rank = f"#{entry['rank']}"
            player_name = entry['player_name']
            win_rate = f"{entry['win_percentage']:.1f}%"
            wins = str(entry['total_wins'])
            losses = str(entry['total_losses'])
            total_matches = str(entry['total_matches'])
            
            # Color coding for win rate
            win_rate_color = GREEN if entry['win_percentage'] >= 60 else YELLOW if entry['win_percentage'] >= 40 else RED
            
            entry_data = [rank, player_name, win_rate, wins, losses, total_matches]
            colors = [rank_color, player_color, win_rate_color, GREEN, RED, LIGHT_GRAY]
            fonts = [self.rank_font, self.text_font, self.text_font, self.text_font, self.text_font, self.text_font]
            
            for data, x_pos, color, font in zip(entry_data, header_positions, colors, fonts):
                text_surface = font.render(str(data), True, color)
                surface.blit(text_surface, (x_pos, row_y))
        
        # Draw back button
        self.back_button.draw(surface)
    
    def handle_event(self, event):
        if self.back_button.handle_event(event):
            return "BACK"
        return None

class DatabaseMenuScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fonts
        self.title_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 60)
        self.text_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 28)
        
        # Create buttons
        button_width = 350
        button_height = 60
        button_spacing = 20
        start_y = screen_height // 2 - 120
        
        self.stats_button = Button(screen_width // 2 - button_width // 2, start_y, 
                                 button_width, button_height, "ALL PLAYERS STATISTICS", RED)
        self.history_button = Button(screen_width // 2 - button_width // 2, start_y + button_height + button_spacing,
                                   button_width, button_height, "COMPLETE MATCH HISTORY", RED)
        self.leaderboard_button = Button(screen_width // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing),
                                       button_width, button_height, "LEADERBOARD", RED)
        self.back_button = Button(screen_width // 2 - button_width // 2, start_y + 3 * (button_height + button_spacing),
                                button_width, button_height, "BACK TO MENU", RED)
        
        # Load background
        try:
            self.bg_image = pygame.image.load(resource_path("assets/images/background/main_menu_bg.jpg")).convert_alpha()
        except:
            self.bg_image = None

    def draw(self, surface):
        # Draw solid dark background
        surface.fill(BLACK)
        
        # Draw title
        title_text = "GAME DATA & STATISTICS"
        title_surface = self.title_font.render(title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_surface, title_rect)
        
        # Add explanation text
        explanation_text = "View statistics and match history for all players"
        explanation_surface = self.text_font.render(explanation_text, True, WHITE)
        explanation_rect = explanation_surface.get_rect(center=(self.screen_width // 2, 120))
        surface.blit(explanation_surface, explanation_rect)
        
        # Draw buttons
        self.stats_button.draw(surface)
        self.history_button.draw(surface)
        self.leaderboard_button.draw(surface)
        self.back_button.draw(surface)

    def handle_event(self, event):
        # Process mouse motion for all buttons first
        if event.type == pygame.MOUSEMOTION:
            self.stats_button.handle_event(event)
            self.history_button.handle_event(event)
            self.leaderboard_button.handle_event(event)
            self.back_button.handle_event(event)
        
        if self.stats_button.handle_event(event):
            return "STATS"
        elif self.history_button.handle_event(event):
            return "HISTORY"
        elif self.leaderboard_button.handle_event(event):
            return "LEADERBOARD"
        elif self.back_button.handle_event(event):
            return "BACK"
        return None