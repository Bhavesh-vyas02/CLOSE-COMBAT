import pygame
from pygame import mixer
from fighter import Fighter
import main_menu
import sys
import os
from game_integration import get_game_session, record_game_result

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # When running in development, use the script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def start_game(p1_character, p2_character, background_map, pvc_mode=False):
    global game_paused, pause_menu_selection, background_sound_on, player_sound_on, match_over, match_winner
    
    print("Starting game with:", p1_character, p2_character, background_map.name, "PvC:", pvc_mode)  # Debug print
    
    # Start match tracking
    session = get_game_session()
    session.start_match()
    
    mixer.init()
    pygame.init()

    #create game window
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("close")

    #set framerate
    clock = pygame.time.Clock()
    FPS = 60

    #define colours
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)

    #define game variables
    intro_count = 5
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]#player scores. [P1, P2]
    round_over = False
    ROUND_OVER_COOLDOWN = 2000
    
    # Timer and pause variables
    ROUND_TIME = 60  # 60 seconds per round
    round_start_time = 0
    current_round_time = ROUND_TIME
    game_paused = False
    pause_menu_selection = 0  # 0 = Background Sound, 1 = Player Sound, 2 = Resume, 3 = Quit
    
    # Sound control variables - load from database
    from game_integration import load_sound_preferences
    sound_prefs = load_sound_preferences()
    background_sound_on = sound_prefs['background_sound']
    player_sound_on = sound_prefs['player_sound']
    time_up = False
    
    # Round tracking variables
    current_round = 1
    total_rounds = 3
    rounds_to_win = 2
    
    # Victory menu variables
    match_over = False
    match_winner = ""
    victory_menu_selection = 0
    match_recorded = False  # Track if match result has been recorded
    
    # Round announcement variables
    show_round_announcement = True
    round_announcement_start_time = 0
    round_announcement_duration = 2000  # 2 seconds total
    round_announcement_fade_duration = 500  # 0.5 seconds fade out
    
    # Navigation control variable
    next_screen = None

    #define fighter variables
    WARRIOR_SIZE = 162
    WARRIOR_SCALE = 4
    WARRIOR_OFFSET = [72, 62]
    WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
    WIZARD_SIZE = 250
    WIZARD_SCALE = 3
    WIZARD_OFFSET = [112, 113]
    WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]
    HUNTRESS_SIZE = 150
    HUNTRESS_SCALE = 3.5
    HUNTRESS_OFFSET = [50, 45]
    HUNTRESS_DATA = [HUNTRESS_SIZE, HUNTRESS_SCALE, HUNTRESS_OFFSET]
    KING_SIZE = 160
    KING_SCALE = 3
    KING_OFFSET = [60, 70]
    KING_DATA = [KING_SIZE, KING_SCALE, KING_OFFSET]
    HERO_KNIGHT_SIZE = 180
    HERO_KNIGHT_SCALE = 3
    HERO_KNIGHT_OFFSET = [70, 55]
    HERO_KNIGHT_DATA = [HERO_KNIGHT_SIZE, HERO_KNIGHT_SCALE, HERO_KNIGHT_OFFSET]
    MARTIAL_HERO_SIZE = 200
    MARTIAL_HERO_SCALE = 3
    MARTIAL_HERO_OFFSET = [80, 62]
    MARTIAL_HERO_DATA = [MARTIAL_HERO_SIZE, MARTIAL_HERO_SCALE, MARTIAL_HERO_OFFSET]

    #load music and sounds
    pygame.mixer.music.load(resource_path("assets/audio/music.mp3"))
    
    # Apply loaded sound settings
    bg_volume = sound_prefs['background_volume'] if background_sound_on else 0.0
    pygame.mixer.music.set_volume(bg_volume)
    pygame.mixer.music.play(-1, 0.0, 5000)
    
    sword_fx = pygame.mixer.Sound(resource_path("assets/audio/sword.wav"))
    magic_fx = pygame.mixer.Sound(resource_path("assets/audio/magic.wav"))
    
    # Apply sound effects volume
    sfx_volume = sound_prefs['effects_volume'] if player_sound_on else 0.0
    sword_fx.set_volume(sfx_volume)
    magic_fx.set_volume(sfx_volume)

    #load spritesheets
    warrior_sheet = pygame.image.load(resource_path("assets/images/warrior/Sprites/warrior.png")).convert_alpha()
    wizard_sheet = pygame.image.load(resource_path("assets/images/wizard/Sprites/wizard.png")).convert_alpha()
    huntress_sheet = pygame.image.load(resource_path("assets/images/Huntress/Sprites/huntress.png")).convert_alpha()
    king_sheet = pygame.image.load(resource_path("assets/images/Medieval King Pack 2/Sprites/king.png")).convert_alpha()
    hero_knight_sheet = pygame.image.load(resource_path("assets/images/Hero Knight/Sprites/hero_knight.png")).convert_alpha()
    martial_hero_sheet = pygame.image.load(resource_path("assets/images/Martial Hero/Sprites/martial_hero.png")).convert_alpha()

    #load victory image
    victory_img = pygame.image.load(resource_path("assets/images/icons/victory.png")).convert_alpha()

    #define number of steps in each animation
    WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
    WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]
    HUNTRESS_ANIMATION_STEPS = [8, 8, 2, 5, 5, 3, 8]
    KING_ANIMATION_STEPS = [8, 8, 2, 4, 4, 4, 6]
    HERO_KNIGHT_ANIMATION_STEPS = [11, 8, 3, 7, 7, 4, 11]
    MARTIAL_HERO_ANIMATION_STEPS = [8, 8, 2, 6, 6, 4, 6]

    #define font
    count_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 80)
    score_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 30)
    control_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 20)

    #function for drawing text
    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    #function for drawing control keys
    def draw_controls():
        # Player 1 Controls
        draw_text("PLAYER CONTROLS:", control_font, WHITE, 50, 200)
        draw_text("Move: A / D", control_font, YELLOW, 50, 230)
        draw_text("Jump: W", control_font, YELLOW, 50, 260)
        draw_text("Attack 1: R", control_font, YELLOW, 50, 290)
        draw_text("Attack 2: T", control_font, YELLOW, 50, 320)
        
        if pvc_mode:
            # AI opponent info
            draw_text("COMPUTER OPPONENT:", control_font, WHITE, SCREEN_WIDTH - 250, 200)
            draw_text("AI Controlled", control_font, YELLOW, SCREEN_WIDTH - 250, 230)
            draw_text(f"Character: {p2_character}", control_font, YELLOW, SCREEN_WIDTH - 250, 260)
            draw_text("Difficulty: Normal", control_font, YELLOW, SCREEN_WIDTH - 250, 290)
        else:
            # Player 2 Controls
            draw_text("PLAYER 2 CONTROLS:", control_font, WHITE, SCREEN_WIDTH - 250, 200)
            draw_text("Move: Left / Right", control_font, YELLOW, SCREEN_WIDTH - 250, 230)
            draw_text("Jump: Up", control_font, YELLOW, SCREEN_WIDTH - 250, 260)
            draw_text("Attack 1: Num 1", control_font, YELLOW, SCREEN_WIDTH - 250, 290)
            draw_text("Attack 2: Num 2", control_font, YELLOW, SCREEN_WIDTH - 250, 320)

    #function for drawing background
    def draw_bg():
        try:
            if not background_map or not background_map.image:
                print("Error: Background map or image is None")  # Debug print
                return
            scaled_bg = pygame.transform.scale(background_map.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
        except Exception as e:
            print(f"Error drawing background: {str(e)}")  # Debug print
            # Fill with black as fallback
            screen.fill((0, 0, 0))

    #function for drawing fighter health bars
    def draw_health_bar(health, x, y):
        ratio = health / 100
        pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(screen, RED, (x, y, 400, 30))
        pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

    #function for drawing AI debug info (optional)
    def draw_ai_debug_info(fighter, x, y):
        if not fighter.is_ai:
            return
        
        debug_info = fighter.ai_get_debug_info()
        debug_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 16)
        
        y_offset = 0
        for key, value in debug_info.items():
            text = f"{key}: {value}"
            debug_surface = debug_font.render(text, True, WHITE)
            screen.blit(debug_surface, (x, y + y_offset))
            y_offset += 20

    #function for drawing round timer
    def draw_timer(time_left, round_num, total_rounds):
        # Round text (top line) - no background, directly on game background
        round_text = f"Round {round_num}/{total_rounds}"
        round_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 24)
        round_surface = round_font.render(round_text, True, WHITE)
        round_rect = round_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(round_surface, round_rect)
        
        # Timer text (bottom line) - format as MM:SS, no background
        minutes = int(time_left) // 60
        seconds = int(time_left) % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"
        timer_color = RED if time_left <= 10 else WHITE
        timer_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 32)
        timer_surface = timer_font.render(timer_text, True, timer_color)
        timer_rect = timer_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(timer_surface, timer_rect)

    #function for drawing round announcement
    def draw_round_announcement(round_num, start_time, duration, fade_duration):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        
        if elapsed_time > duration:
            return False  # Animation finished
        
        # Calculate alpha for fade effect
        alpha = 255
        if elapsed_time > (duration - fade_duration):
            # Fade out phase
            fade_progress = (elapsed_time - (duration - fade_duration)) / fade_duration
            alpha = int(255 * (1 - fade_progress))
        
        # Create the announcement text
        announcement_text = f"ROUND {round_num}"
        announcement_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 120)
        
        # Create surface with per-pixel alpha
        text_surface = announcement_font.render(announcement_text, True, WHITE)
        text_surface.set_alpha(alpha)
        
        # Center the text on screen
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # Draw semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(alpha // 3)  # Much more transparent background
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw the text
        screen.blit(text_surface, text_rect)
        
        return True  # Animation still running

    #function for drawing pause menu
    def draw_pause_menu():
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        screen.blit(overlay, (0, 0))
        
        # Pause title
        pause_title = count_font.render("PAUSED", True, WHITE)
        title_rect = pause_title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(pause_title, title_rect)
        
        # Menu options with red rounded buttons
        button_width = 350
        button_height = 50
        button_spacing = 70
        start_y = 220
        
        menu_options = [
            f"BACKGROUND SOUND: {'ON' if background_sound_on else 'OFF'}",
            f"PLAYER SOUND: {'ON' if player_sound_on else 'OFF'}",
            "RESUME",
            "QUIT"
        ]
        
        # Get mouse position for hover effect
        mouse_pos = pygame.mouse.get_pos()
        button_rects = []
        
        for i, option in enumerate(menu_options):
            button_y = start_y + i * button_spacing
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            
            # Button background (red with white border)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            button_rects.append(button_rect)
            
            # Check if mouse is hovering over button
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Button color based on hover
            if is_hovered:
                pygame.draw.rect(screen, (255, 100, 100), button_rect, border_radius=10)  # Lighter red when hovered
            else:
                pygame.draw.rect(screen, (200, 0, 0), button_rect, border_radius=10)  # Dark red
            
            pygame.draw.rect(screen, WHITE, button_rect, 3, border_radius=10)  # White border
            
            # Button text
            button_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 24)
            text_surface = button_font.render(option, True, WHITE)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
        
        return button_rects

    #function for drawing victory menu
    def draw_victory_menu():
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        screen.blit(overlay, (0, 0))
        
        # Victory title with glow effect (same as main menu title)
        victory_text = f"{match_winner} WINS!"
        
        # Draw glow effect
        glow_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 65)
        glow_surf = glow_font.render(victory_text, True, (255, 0, 255))  # Pink glow
        glow_surf.set_alpha(150)
        glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(glow_surf, glow_rect)
        
        # Draw main victory text
        victory_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 60)
        victory_surface = victory_font.render(victory_text, True, WHITE)
        victory_rect = victory_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(victory_surface, victory_rect)
        
        # Menu buttons
        button_width = 300
        button_height = 50
        button_spacing = 70
        start_y = 250
        
        menu_options = [
            "REPLAY",
            "CHANGE CHARACTER",
            "MAIN MENU",
            "QUIT"
        ]
        
        # Get mouse position for hover effect
        mouse_pos = pygame.mouse.get_pos()
        button_rects = []
        
        for i, option in enumerate(menu_options):
            button_y = start_y + i * button_spacing
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            
            # Button background (red with white border)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            button_rects.append(button_rect)
            
            # Check if mouse is hovering over button
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Button color based on hover
            if is_hovered:
                pygame.draw.rect(screen, (255, 100, 100), button_rect, border_radius=10)  # Lighter red when hovered
            else:
                pygame.draw.rect(screen, (200, 0, 0), button_rect, border_radius=10)  # Dark red
            
            pygame.draw.rect(screen, WHITE, button_rect, 3, border_radius=10)  # White border
            
            # Button text
            button_font = pygame.font.Font(resource_path("assets/fonts/turok.ttf"), 24)
            text_surface = button_font.render(option, True, WHITE)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
        
        return button_rects

    # Create fighters based on selection
    def create_fighter(player_num, x_pos, y_pos, character, is_ai=False):
        if character == "WARRIOR":
            return Fighter(player_num, x_pos, y_pos, player_num == 2, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx, is_ai, character)
        elif character == "WIZARD":
            return Fighter(player_num, x_pos, y_pos, player_num == 2, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx, is_ai, character)
        elif character == "HUNTRESS":
            return Fighter(player_num, x_pos, y_pos, player_num == 2, HUNTRESS_DATA, huntress_sheet, HUNTRESS_ANIMATION_STEPS, sword_fx, is_ai, character)
        elif character == "KING":
            return Fighter(player_num, x_pos, y_pos, player_num == 2, KING_DATA, king_sheet, KING_ANIMATION_STEPS, sword_fx, is_ai, character)
        elif character == "HERO_KNIGHT":
            return Fighter(player_num, x_pos, y_pos, player_num == 2, HERO_KNIGHT_DATA, hero_knight_sheet, HERO_KNIGHT_ANIMATION_STEPS, sword_fx, is_ai, character)
        else:  # MARTIAL_HERO
            return Fighter(player_num, x_pos, y_pos, player_num == 2, MARTIAL_HERO_DATA, martial_hero_sheet, MARTIAL_HERO_ANIMATION_STEPS, sword_fx, is_ai, character)

    #create two instances of fighters based on selection
    fighter_1 = create_fighter(1, 250, 310, p1_character, False)
    fighter_2 = create_fighter(2, 650, 310, p2_character, pvc_mode)
    
    # AI difficulty adjustment variables
    ai_performance_tracker = {"wins": 0, "losses": 0, "rounds": 0}
    ai_difficulty_adjustment_timer = 0

    #game loop
    run = True
    while run:
        clock.tick(FPS)

        #draw background
        draw_bg()

        #show player stats
        draw_health_bar(fighter_1.health, 20, 20)
        draw_health_bar(fighter_2.health, 580, 20)
        draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
        if pvc_mode:
            draw_text("AI: " + str(score[1]), score_font, RED, 580, 60)
            # Optional: Draw AI debug info (uncomment to enable)
            # draw_ai_debug_info(fighter_2, 20, 100)
        else:
            draw_text("P2: " + str(score[1]), score_font, RED, 580, 60)
        
        # Draw timer
        if not game_paused and intro_count <= 0 and not round_over:
            draw_timer(current_round_time, current_round, total_rounds)

        # Handle round announcement
        if show_round_announcement and not game_paused and not match_over:
            if round_announcement_start_time == 0:
                round_announcement_start_time = pygame.time.get_ticks()
            
            # Draw round announcement and check if it's finished
            if not draw_round_announcement(current_round, round_announcement_start_time, 
                                         round_announcement_duration, round_announcement_fade_duration):
                show_round_announcement = False
                # Start the intro countdown after round announcement
                if intro_count == 5:  # Only reset if this is the first time
                    last_count_update = pygame.time.get_ticks()

        #update countdown and timer logic
        if not game_paused and not match_over and not show_round_announcement:
            if intro_count <= 0:
                # Start round timer if not started
                if round_start_time == 0:
                    round_start_time = pygame.time.get_ticks()
                
                # Update round timer
                if not round_over and not time_up:
                    elapsed_time = (pygame.time.get_ticks() - round_start_time) / 1000.0
                    current_round_time = max(0, ROUND_TIME - elapsed_time)
                    
                    # Check if time is up
                    if current_round_time <= 0:
                        time_up = True
                        round_over = True
                        round_over_time = pygame.time.get_ticks()
                        
                        # Determine winner based on health - player with LOWER health loses
                        if fighter_1.health > fighter_2.health:
                            score[0] += 1  # Player 1 wins (has more health)
                            print(f"Time's up! Player 1 wins with {fighter_1.health} health vs Player 2's {fighter_2.health} health")
                            # Check for match winner
                            if score[0] >= rounds_to_win:
                                match_over = True
                                match_winner = "PLAYER 1"
                        elif fighter_2.health > fighter_1.health:
                            score[1] += 1  # Player 2/AI wins (has more health)
                            if pvc_mode:
                                print(f"Time's up! AI wins with {fighter_2.health} health vs Player 1's {fighter_1.health} health")
                            else:
                                print(f"Time's up! Player 2 wins with {fighter_2.health} health vs Player 1's {fighter_1.health} health")
                            # Check for match winner
                            if score[1] >= rounds_to_win:
                                match_over = True
                                if pvc_mode:
                                    match_winner = "AI"
                                else:
                                    match_winner = "PLAYER 2"
                        else:
                            # Equal health - it's a draw (no score change)
                            print(f"Time's up! Draw - both players have {fighter_1.health} health")
                
                #move fighters
                if not round_over and not game_paused:
                    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
                    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
            else:
                #display count timer
                draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
                #display control keys
                draw_controls()
                #update count timer
                if (pygame.time.get_ticks() - last_count_update) >= 1000:
                    intro_count -= 1
                    last_count_update = pygame.time.get_ticks()

        #update fighters
        if not game_paused and not match_over:
            fighter_1.update()
            fighter_2.update()

        #draw fighters
        fighter_1.draw(screen)
        fighter_2.draw(screen)

        #check for player defeat
        if round_over == False and not match_over:
            if fighter_1.alive == False:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
                # Track AI performance for difficulty adjustment
                if pvc_mode:
                    ai_performance_tracker["wins"] += 1
                    ai_performance_tracker["rounds"] += 1
                
                # Check for match winner
                if score[1] >= rounds_to_win:
                    match_over = True
                    if pvc_mode:
                        match_winner = "AI"
                    else:
                        match_winner = "PLAYER 2"
                    
            elif fighter_2.alive == False:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
                # Track AI performance for difficulty adjustment
                if pvc_mode:
                    ai_performance_tracker["losses"] += 1
                    ai_performance_tracker["rounds"] += 1
                
                # Check for match winner
                if score[0] >= rounds_to_win:
                    match_over = True
                    match_winner = "PLAYER 1"
        else:
            #display victory image
            screen.blit(victory_img, (360, 150))
            
            # Record match result in database (only once per match)
            if match_over and not match_recorded:
                game_mode = "PvC" if pvc_mode else "PvP"
                
                # Determine winner for database
                if match_winner == "PLAYER 1":
                    winner = "P1"
                elif match_winner in ["PLAYER 2", "AI"]:
                    winner = "P2"
                else:
                    winner = "DRAW"
                
                # Record the match result
                record_game_result(
                    p1_character, p2_character, winner, game_mode,
                    score[0], score[1], score[1], score[0]
                )
                match_recorded = True
                print(f"Match recorded: {match_winner} wins ({score[0]}-{score[1]})")
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                intro_count = 5
                
                # Increment round number if match isn't over
                if not match_over:
                    current_round += 1
                    # Reset timer for new round
                    current_round_time = ROUND_TIME
                    round_start_time = 0
                    time_up = False
                    
                    # Reset round announcement for new round
                    show_round_announcement = True
                    round_announcement_start_time = 0
                
                # Dynamic AI difficulty adjustment
                if pvc_mode and ai_performance_tracker["rounds"] >= 3:
                    win_rate = ai_performance_tracker["wins"] / ai_performance_tracker["rounds"]
                    
                    # Adjust AI difficulty based on performance
                    if win_rate > 0.7:  # AI winning too much
                        print("AI difficulty decreased - AI was winning too often")
                        # Make AI slightly easier
                        fighter_2.ai_difficulty_modifier = max(0.5, fighter_2.ai_difficulty_modifier - 0.1)
                        fighter_2.ai_reaction_time = min(500, fighter_2.ai_reaction_time + 50)
                    elif win_rate < 0.3:  # AI losing too much
                        print("AI difficulty increased - Player was winning too often")
                        # Make AI slightly harder
                        fighter_2.ai_difficulty_modifier = min(1.5, fighter_2.ai_difficulty_modifier + 0.1)
                        fighter_2.ai_reaction_time = max(150, fighter_2.ai_reaction_time - 50)
                    
                    # Reset tracker every few rounds
                    if ai_performance_tracker["rounds"] >= 5:
                        ai_performance_tracker = {"wins": 0, "losses": 0, "rounds": 0}
                
                fighter_1 = create_fighter(1, 250, 310, p1_character, False)
                fighter_2 = create_fighter(2, 650, 310, p2_character, pvc_mode)
                
                # Apply difficulty modifier to new AI fighter
                if pvc_mode and hasattr(fighter_2, 'ai_difficulty_modifier'):
                    fighter_2.ai_difficulty_modifier = getattr(fighter_2, 'ai_difficulty_modifier', 1.0)

        #event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            # Handle pause functionality
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not round_over:
                    game_paused = not game_paused
                    if game_paused:
                        print("Game Paused")
                    else:
                        print("Game Resumed")
            
            # Handle mouse clicks on pause menu
            if event.type == pygame.MOUSEBUTTONDOWN and game_paused:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check which button was clicked
                    button_width = 350
                    button_height = 50
                    button_spacing = 70
                    start_y = 220
                    
                    for i in range(4):  # 4 buttons
                        button_y = start_y + i * button_spacing
                        button_x = SCREEN_WIDTH // 2 - button_width // 2
                        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                        
                        if button_rect.collidepoint(mouse_pos):
                            if i == 0:  # Background Sound
                                background_sound_on = not background_sound_on
                                if background_sound_on:
                                    pygame.mixer.music.set_volume(0.5)
                                    print("Background sound ON")
                                else:
                                    pygame.mixer.music.set_volume(0.0)
                                    print("Background sound OFF")
                                
                                # Save setting to database
                                from game_integration import update_sound_preferences
                                update_sound_preferences(background_sound_on, player_sound_on)
                                
                            elif i == 1:  # Player Sound
                                player_sound_on = not player_sound_on
                                if player_sound_on:
                                    sword_fx.set_volume(0.5)
                                    magic_fx.set_volume(0.75)
                                    print("Player sound ON")
                                else:
                                    sword_fx.set_volume(0.0)
                                    magic_fx.set_volume(0.0)
                                    print("Player sound OFF")
                                
                                # Save setting to database
                                from game_integration import update_sound_preferences
                                update_sound_preferences(background_sound_on, player_sound_on)
                            elif i == 2:  # Resume
                                game_paused = False
                                print("Game Resumed")
                            elif i == 3:  # Quit
                                print("Returning to menu...")
                                next_screen = "main_menu"
                                run = False
                            break
            
            # Handle mouse clicks on victory menu
            if event.type == pygame.MOUSEBUTTONDOWN and match_over:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check which button was clicked
                    button_width = 300
                    button_height = 50
                    button_spacing = 70
                    start_y = 250
                    
                    for i in range(4):  # 4 buttons
                        button_y = start_y + i * button_spacing
                        button_x = SCREEN_WIDTH // 2 - button_width // 2
                        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                        
                        if button_rect.collidepoint(mouse_pos):
                            if i == 0:  # Replay
                                print("Restarting match...")
                                # Reset match variables
                                match_over = False
                                match_winner = ""
                                score = [0, 0]
                                match_recorded = False  # Reset for new match
                                
                                # Start new match tracking
                                session = get_game_session()
                                session.start_match()
                                current_round = 1
                                round_over = False
                                intro_count = 5
                                current_round_time = ROUND_TIME
                                round_start_time = 0
                                time_up = False
                                # Reset round announcement
                                show_round_announcement = True
                                round_announcement_start_time = 0
                                # Reset fighters
                                fighter_1 = create_fighter(1, 250, 310, p1_character, False)
                                fighter_2 = create_fighter(2, 650, 310, p2_character, pvc_mode)
                            elif i == 1:  # Change Character
                                print("Going to character selection...")
                                next_screen = "character_select"
                                run = False
                            elif i == 2:  # Main Menu
                                print("Going to main menu...")
                                next_screen = "main_menu"
                                run = False
                            elif i == 3:  # Quit
                                print("Quitting game...")
                                pygame.quit()
                                sys.exit()
                            break

        # Draw pause menu if paused
        if game_paused:
            pause_button_rects = draw_pause_menu()
        
        # Draw victory menu if match is over
        if match_over:
            victory_button_rects = draw_victory_menu()
        
        #update display
        pygame.display.update()

    # Return the appropriate screen based on user choice
    if next_screen:
        return next_screen
    return None  # Default return when game ends normally

if __name__ == "__main__":
    # Initialize Pygame for the menu
    pygame.init()
    mixer.init()
    
    # Initialize database system
    from game_integration import initialize_game_database, cleanup_game_database, start_player_session
    
    if not initialize_game_database():
        print("Warning: Database system failed to initialize. Game will run without data persistence.")
    
    # Start default player session (we'll add proper player selection later)
    start_player_session("Player1")
    
    # Main game loop to handle different states
    start_screen = "MENU"
    start_pvc_mode = False
    
    while True:
        # Get selections from menu
        result = main_menu.main_menu(start_screen, start_pvc_mode)
        
        if result:
            p1_char, p2_char, selected_bg, pvc_mode = result
            
            # Game loop to handle victory menu returns
            while True:
                # Start the actual game
                game_result = start_game(p1_char, p2_char, selected_bg, pvc_mode)
                
                if game_result == "character_select":
                    # Go directly to character selection with same PvC mode
                    print("Going to character selection...")
                    start_screen = "CHARACTER_SELECT"
                    start_pvc_mode = pvc_mode
                    break
                elif game_result == "main_menu":
                    # Go back to main menu
                    print("Going to main menu...")
                    start_screen = "MENU"
                    start_pvc_mode = False
                    break
                elif game_result == "quit":
                    # Exit completely
                    pygame.quit()
                    sys.exit()
                elif game_result is None:
                    # Game ended normally (ESC or window close)
                    start_screen = "MENU"
                    start_pvc_mode = False
                    break
                # If game_result is anything else, continue the inner loop (replay)
        else:
            # User quit from main menu
            cleanup_game_database()
            pygame.quit()
            sys.exit()