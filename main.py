# main.py
import pygame, sys, time
from pathlib import Path
from config import *
from utils import list_audio_files, load_beatmap
from level_editor import LevelEditorScene

# --- Scene system (same as before) ---
class Scene:
    def __init__(self, game): self.game = game
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surface): pass

class SceneManager:
    def __init__(self, start_scene): self.scene = start_scene
    def go_to(self, scene): self.scene = scene

# --- Menu ---
class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_big = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 36)
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.scene_manager.go_to(SongListScene(self.game))
            elif event.key == pygame.K_e and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if not self.game.playing_song:
                    self.game.scene_manager.go_to(LevelEditorScene(self.game))
        elif event.type == pygame.QUIT:
            self.game.running = False
    def draw(self, surface):
        surface.fill((0,0,0))
        title = self.font_big.render("Rhythm Tapper", True, (255,255,255))
        hint = self.font.render("[Enter] Song List | [Ctrl + E] Editor | [Esc] Quit", True, (200,200,200))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))
        surface.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 220))

# --- Song List ---
class SongListScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 36)
        self.audio_files = list_audio_files()
        self.selected = 0
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.scene_manager.go_to(MenuScene(self.game))
            elif event.key == pygame.K_DOWN:
                if self.audio_files:
                    self.selected = min(self.selected + 1, len(self.audio_files)-1)
            elif event.key == pygame.K_UP:
                if self.audio_files:
                    self.selected = max(self.selected - 1, 0)
            elif event.key == pygame.K_RETURN and self.audio_files:
                self.game.current_song = self.audio_files[self.selected]
                self.game.scene_manager.go_to(GameplayScene(self.game))
    def draw(self, surface):
        surface.fill((20,20,20))
        title = self.font.render("Song List", True, (255,255,255))
        surface.blit(title, (40,40))
        for i, p in enumerate(self.audio_files):
            color = (255,255,0) if i==self.selected else (200,200,200)
            # show folder/artist - filename
            rel = p.parent.name
            text = ("-> " if i==self.selected else "   ") + f"{rel} - {p.name}"
            surface.blit(self.font.render(text, True, color), (60, 100 + i*36))

# --- Pause Overlay (used inside GameplayScene) ---
class PauseOverlay:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 40)
        # menu buttons as (label, action)
        self.options = [("Resume", self.resume), ("Restart", self.restart), ("Quit", self.quit_to_menu)]
        self.sel = 0
    def resume(self):
        self.game.resume_game()
    def restart(self):
        # restart current gameplay scene by reloading it
        self.game.scene_manager.go_to(GameplayScene(self.game))
    def quit_to_menu(self):
        pygame.mixer.music.stop()
        self.game.playing_song = False
        self.game.scene_manager.go_to(self.game.menu_scene)
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.sel = (self.sel - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.sel = (self.sel + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.options[self.sel][1]()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx,my = pygame.mouse.get_pos()
            # calculate button positions and check clicks
            cx = SCREEN_WIDTH//2
            by = SCREEN_HEIGHT//2 - 30
            for i,(label,action) in enumerate(self.options):
                rect = pygame.Rect(cx - 100, by + i*50, 200, 40)
                if rect.collidepoint(mx,my):
                    action()
    def draw(self, surface):
        # translucent overlay
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,180))
        surface.blit(s, (0,0))
        title = self.font.render("PAUSED", True, (255,255,255))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 120))
        cx = SCREEN_WIDTH//2
        by = SCREEN_HEIGHT//2 - 30
        for i,(label,_) in enumerate(self.options):
            color = (255,255,0) if i==self.sel else (220,220,220)
            pygame.draw.rect(surface, (50,50,50), (cx - 100, by + i*50, 200, 40), border_radius=6)
            surface.blit(self.font.render(label, True, color), (cx - 40, by + i*50 + 6))

# --- Gameplay Scene (fixed) ---
class GameplayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 32)
        self.player_x = SCREEN_WIDTH//2
        self.player_y = SCREEN_HEIGHT - 100
        self.score = 0
        self.combo = 0
        self.health = 100
        self.notes = []
        self.spawn_index = 0
        self.paused = False
        self.pause_overlay = PauseOverlay(game)
        # load beatmap (custom _custom.json) else empty
        beatmap_path = Path(BEATMAPS_DIR) / (game.current_song.stem + "_custom.json")
        self.beatmap = load_beatmap(beatmap_path) if beatmap_path.exists() else {"notes": []}
        # playback
        pygame.mixer.music.load(str(game.current_song))
        pygame.mixer.music.play()
        self.game.playing_song = True
        self.start_time = time.time()
    def handle_event(self, event):
        # if paused, forward events to overlay
        if self.paused:
            self.pause_overlay.handle_event(event)
            # allow Esc to resume too
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.toggle_pause()
            return

        # Normal gameplay input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # toggle pause instead of quitting
                self.toggle_pause()
        if event.type == pygame.MOUSEMOTION:
            mx, _ = pygame.mouse.get_pos()
            # instantly follow or do smoothing if you want
            self.player_x = mx
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            for n in list(self.notes):
                if abs(mx - n["x"]) < 30 and abs(my - n["y"]) < 30:
                    self.notes.remove(n)
                    self.score += 100
                    self.combo += 1
    def toggle_pause(self):
        if not self.paused:
            # pause music (pygame's pause toggles mixer channels; for music use pause()/unpause())
            pygame.mixer.music.pause()
            self.paused = True
            self.game.playing_song = False
        else:
            pygame.mixer.music.unpause()
            self.paused = False
            self.game.playing_song = True
    def update(self, dt):
        if self.paused:
            return
        now = time.time() - self.start_time
        if self.spawn_index < len(self.beatmap.get("notes", [])):
            n = self.beatmap["notes"][self.spawn_index]
            if now >= n["time"]:
                self.notes.append({"x": n["x"], "y": -10})
                self.spawn_index += 1
        for n in list(self.notes):
            n["y"] += NOTE_SPEED * dt
            if n["y"] > self.player_y + 40:
                self.notes.remove(n)
                self.combo = 0
                self.health -= 10
                if self.health <= 0:
                    pygame.mixer.music.stop()
                    self.game.playing_song = False
                    self.game.scene_manager.go_to(GameOverScene(self.game, self.score, self.combo))
        # if music ended naturally and not paused
        if not pygame.mixer.music.get_busy() and not self.paused:
            self.game.playing_song = False
            self.game.scene_manager.go_to(ResultsScene(self.game, self.score, self.combo))
    def draw(self, surface):
        surface.fill((0,0,0))
        pygame.draw.line(surface, (255,255,255), (0, self.player_y), (SCREEN_WIDTH, self.player_y), 2)
        # player circle now follows mouse X every frame (player_x is updated on MOUSEMOTION)
        pygame.draw.circle(surface, (0,255,0), (int(self.player_x), self.player_y), 15)
        for n in self.notes:
            pygame.draw.circle(surface, (255,200,0), (int(n["x"]), int(n["y"])), 10)
        txt = f"Score: {self.score} | Combo: {self.combo} | HP: {self.health}"
        surface.blit(self.font.render(txt, True, (255,255,255)), (10,10))
        if self.paused:
            self.pause_overlay.draw(surface)

# --- Game Over & Results (unchanged) ---
class GameOverScene(Scene):
    def __init__(self, game, score, combo):
        super().__init__(game)
        self.score = score
        self.combo = combo
        self.font = pygame.font.Font(None, 48)
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.game.scene_manager.go_to(MenuScene(self.game))
    def draw(self, surface):
        surface.fill((50,0,0))
        t = self.font.render("GAME OVER", True, (255,0,0))
        s = self.font.render(f"Score: {self.score}", True, (255,255,255))
        surface.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 120))
        surface.blit(s, (SCREEN_WIDTH//2 - s.get_width()//2, 220))

class ResultsScene(Scene):
    def __init__(self, game, score, combo):
        super().__init__(game)
        self.score = score
        self.combo = combo
        self.font = pygame.font.Font(None, 48)
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.game.scene_manager.go_to(MenuScene(self.game))
    def draw(self, surface):
        surface.fill((0,50,0))
        t = self.font.render("Results", True, (255,255,255))
        s = self.font.render(f"Score: {self.score} | Combo: {self.combo}", True, (255,255,255))
        surface.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 120))
        surface.blit(s, (SCREEN_WIDTH//2 - s.get_width()//2, 220))

# --- Game Container ---
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rhythm Tapper - SHOW Build (Fixed)")
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing_song = False
        self.current_song = None
        self.menu_scene = MenuScene(self)
        self.scene_manager = SceneManager(self.menu_scene)
    def resume_game(self):
        # helper used by pause overlay to resume
        current = self.scene_manager.scene
        if isinstance(current, GameplayScene):
            current.toggle_pause()
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)/1000.0
            for event in pygame.event.get():
                # Ctrl+E to editor from anywhere if not playing
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    if not self.playing_song:
                        self.scene_manager.go_to(LevelEditorScene(self))
                # pass to current scene
                self.scene_manager.scene.handle_event(event)
            self.scene_manager.scene.update(dt)
            self.scene_manager.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
