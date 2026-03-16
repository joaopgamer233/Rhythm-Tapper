import pygame
import random
import time
import sys

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rhythm Tapper")
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE  = (0, 100, 255)
GRAY  = (100, 100, 100)

# --- Fonts ---
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 32)

# --- Game States ---
MENU = "menu"
DIFFICULTY = "difficulty"
GAME = "game"
SETTINGS = "settings"
GAME_OVER = "gameover"
state = MENU

# --- Player ---
player_radius = 15
player_x = WIDTH // 2
player_y = HEIGHT - 100
mouse_sensitivity = 1.0
keyboard_mode = False
show_mouse = False
fullscreen = False

# --- Notes ---
notes = []
note_radius = 10
note_speed = 4
spawn_interval = 0.8
last_spawn_time = time.time()

# --- Feedback & Score ---
feedback_text = ""
feedback_timer = 0
score = 0
combo = 0
health = 100  # max 100

# --- Difficulty settings ---
difficulty_settings = {
    "Easy": {"note_speed": 3, "spawn_interval": 1.0},
    "Normal": {"note_speed": 5, "spawn_interval": 0.7},
    "Hard": {"note_speed": 7, "spawn_interval": 0.5}
}
selected_difficulty = None

# --- Functions ---
def reset_game():
    global notes, score, combo, feedback_text, feedback_timer, last_spawn_time, health
    notes = []
    score = 0
    combo = 0
    feedback_text = ""
    feedback_timer = 0
    last_spawn_time = time.time()
    health = 100

def spawn_note():
    x = random.randint(note_radius, WIDTH - note_radius)
    notes.append({"x": x, "y": -note_radius, "hit": False})

def draw_feedback():
    if feedback_text:
        text_surf = small_font.render(feedback_text, True, WHITE)
        screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, HEIGHT // 2))

def check_hit(note):
    global score, combo, feedback_text, feedback_timer, health

    distance = abs(note["x"] - player_x)
    if distance < 20:
        timing_window = abs(note["y"] - player_y)
        if timing_window < 10:
            feedback_text = "Perfect!"
            score += 300
            combo += 1
        elif timing_window < 25:
            feedback_text = "Good!"
            score += 100
            combo += 1
        else:
            feedback_text = "X"
            combo = 0
            health -= 10
        feedback_timer = 0.5
        note["hit"] = True

def draw_health_bar():
    bar_width = 200
    bar_height = 20
    x = WIDTH - bar_width - 20
    y = 20
    fill = (health / 100) * bar_width
    pygame.draw.rect(screen, GRAY, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, RED, (x, y, fill, bar_height))
    pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2)

# --- Main Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- MENU ---
        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Play
                if 300 < mx < 500 and 250 < my < 300:
                    state = DIFFICULTY
                # Settings
                if 300 < mx < 500 and 350 < my < 400:
                    state = SETTINGS
                # Quit
                if 300 < mx < 500 and 450 < my < 500:
                    running = False

        # --- DIFFICULTY ---
        elif state == DIFFICULTY:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 300 < mx < 500 and 200 < my < 250:
                    selected_difficulty = "Easy"
                elif 300 < mx < 500 and 280 < my < 330:
                    selected_difficulty = "Normal"
                elif 300 < mx < 500 and 360 < my < 410:
                    selected_difficulty = "Hard"
                if selected_difficulty:
                    settings = difficulty_settings[selected_difficulty]
                    note_speed = settings["note_speed"]
                    spawn_interval = settings["spawn_interval"]
                    reset_game()
                    pygame.mouse.set_visible(show_mouse)
                    state = GAME

        # --- SETTINGS ---
        elif state == SETTINGS:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Toggle fullscreen
                if 300 < mx < 500 and 200 < my < 250:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                # Toggle show mouse
                if 300 < mx < 500 and 280 < my < 330:
                    show_mouse = not show_mouse
                # Quit settings
                if 300 < mx < 500 and 440 < my < 490:
                    state = MENU

        # --- GAME ---
        elif state == GAME:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = MENU
                pygame.mouse.set_visible(True)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for note in notes:
                    if not note["hit"] and abs(note["y"] - player_y) < 30:
                        check_hit(note)

    # --- GAMEPLAY LOGIC ---
    if state == GAME:
        # Mouse mode
        if not keyboard_mode:
            mouse_x, _ = pygame.mouse.get_pos()
            player_x += (mouse_x - player_x) * mouse_sensitivity

        # Spawn notes
        if time.time() - last_spawn_time > spawn_interval:
            spawn_note()
            last_spawn_time = time.time()

        # Update notes
        for note in notes:
            note["y"] += note_speed
            if note["y"] > player_y + 20 and not note["hit"]:
                health -= 10
                note["hit"] = True

        # Remove off-screen notes
        notes = [n for n in notes if n["y"] < HEIGHT + note_radius]

        # Check for game over
        if health <= 0:
            state = GAME_OVER
            pygame.mouse.set_visible(True)

    # --- DRAWING ---
    screen.fill(BLACK)

    if state == MENU:
        title = font.render("Rhythm Tapper", True, WHITE)
        play_button = small_font.render("Play", True, BLACK)
        settings_button = small_font.render("Settings", True, BLACK)
        quit_button = small_font.render("Quit", True, BLACK)
        pygame.draw.rect(screen, WHITE, (300, 250, 200, 50))
        pygame.draw.rect(screen, WHITE, (300, 350, 200, 50))
        pygame.draw.rect(screen, WHITE, (300, 450, 200, 50))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        screen.blit(play_button, (400 - play_button.get_width()//2, 265 - play_button.get_height()//2))
        screen.blit(settings_button, (400 - settings_button.get_width()//2, 365 - settings_button.get_height()//2))
        screen.blit(quit_button, (400 - quit_button.get_width()//2, 465 - quit_button.get_height()//2))

    elif state == SETTINGS:
        title = font.render("Settings", True, BLACK)
        fullscreen_text = small_font.render(f"Fullscreen: {'ON' if fullscreen else 'OFF'}", True, BLACK)
        mouse_text = small_font.render(f"Show Mouse: {'ON' if show_mouse else 'OFF'}", True, BLACK)
        quit_text = small_font.render("Back", True, BLACK)
        pygame.draw.rect(screen, WHITE, (300, 200, 200, 50))
        pygame.draw.rect(screen, WHITE, (300, 280, 200, 50))
        pygame.draw.rect(screen, WHITE, (300, 440, 200, 50))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        screen.blit(fullscreen_text, (400 - fullscreen_text.get_width()//2, 215 - fullscreen_text.get_height()//2))
        screen.blit(mouse_text, (400 - mouse_text.get_width()//2, 295 - mouse_text.get_height()//2))
        screen.blit(quit_text, (400 - quit_text.get_width()//2, 455 - quit_text.get_height()//2))

    elif state == DIFFICULTY:
        title = font.render("Select Difficulty", True, WHITE)
        easy = small_font.render("Easy", True, BLACK)
        normal = small_font.render("Normal", True, BLACK)
        hard = small_font.render("Hard", True, BLACK)
        pygame.draw.rect(screen, WHITE, (300, 200, 200, 50))
        pygame.draw.rect(screen, WHITE, (300, 280, 200, 50))
        pygame.draw.rect(screen, WHITE, (300, 360, 200, 50))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        screen.blit(easy, (400 - easy.get_width()//2, 225 - easy.get_height()//2))
        screen.blit(normal, (400 - normal.get_width()//2, 305 - normal.get_height()//2))
        screen.blit(hard, (400 - hard.get_width()//2, 385 - hard.get_height()//2))

    elif state == GAME:
        pygame.draw.line(screen, WHITE, (0, player_y), (WIDTH, player_y), 2)
        pygame.draw.circle(screen, GREEN, (int(player_x), player_y), player_radius)
        for note in notes:
            if not note["hit"]:
                pygame.draw.circle(screen, YELLOW, (int(note["x"]), int(note["y"])), note_radius)
        draw_health_bar()
        if feedback_timer > 0:
            draw_feedback()
            feedback_timer -= dt
        score_text = small_font.render(f"Score: {score}  Combo: {combo}", True, WHITE)
        screen.blit(score_text, (10, 50))

    elif state == GAME_OVER:
        over_text = font.render("GAME OVER", True, RED)
        score_text = small_font.render(f"Final Score: {score} Combo: {combo}", True, WHITE)
        back_text = small_font.render("Back to Menu", True, BLACK)
        pygame.draw.rect(screen, WHITE, (300, 400, 200, 50))
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, 200))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 300))
        screen.blit(back_text, (400 - back_text.get_width()//2, 415 - back_text.get_height()//2))
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if 300 < mx < 500 and 400 < my < 450:
                state = MENU

    pygame.display.flip()

pygame.quit()
sys.exit()
