from pathlib import Path
import pygame
from player import MusicPlayer

SCREEN_WIDTH = 760
SCREEN_HEIGHT = 280
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (100, 200, 255)
FPS = 30


def draw_ui(screen: pygame.Surface, font: pygame.font.Font, title_font: pygame.font.Font, player: MusicPlayer) -> None:
    screen.fill(BACKGROUND_COLOR)

    title = title_font.render("Keyboard Music Player", True, ACCENT_COLOR)
    screen.blit(title, (20, 20))

    for index, line in enumerate(player.get_status_lines()):
        text_surface = font.render(line, True, TEXT_COLOR)
        screen.blit(text_surface, (20, 80 + index * 35))

    pygame.draw.rect(screen, ACCENT_COLOR, pygame.Rect(20, 230, 720, 4))

    # Progress bar
    total = max(player.get_track_length(), 0.001)
    progress_ratio = min(player.get_position_seconds() / total, 1.0) if total > 0 else 0
    pygame.draw.rect(screen, (80, 80, 80), pygame.Rect(20, 200, 720, 18))
    pygame.draw.rect(screen, ACCENT_COLOR, pygame.Rect(20, 200, int(720 * progress_ratio), 18))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Music Player")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 30)
    title_font = pygame.font.SysFont(None, 42)

    music_dir = Path(__file__).resolve().parent / "music" / "sample_tracks"
    player = MusicPlayer(music_dir)

    running = True
    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.previous_track()
                elif event.key == pygame.K_q:
                    running = False

        draw_ui(screen, font, title_font, player)
        pygame.display.flip()
        clock.tick(FPS)

    player.stop()
    pygame.quit()


if __name__ == "__main__":
    main()