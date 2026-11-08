import random
from collections import deque
from pathlib import Path

import pygame

CELL, COLS, ROWS = 24, 30, 20
BASE_FPS, MAX_FPS = 8, 20  
HIGHSCORE_FILE = Path("highscore.txt")

BG, SNAKE, HEAD, FOOD, TEXT = (24, 26, 33), (80, 200, 120), (140, 240, 170), (235, 80, 80), (235, 235, 235)
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
KEYS = {
    pygame.K_UP: UP, pygame.K_w: UP,
    pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
}

class SnakeGame:
    def __init__(self, cols: int = COLS, rows: int = ROWS, rng: random.Random | None = None):
        self.cols, self.rows = cols, rows
        self.rng = rng or random.Random()
        self.reset()

    def reset(self) -> None:
        x, y = self.cols // 2, self.rows // 2
        self.snake = deque([(x, y), (x - 1, y), (x - 2, y)])  # head first
        self.direction = self.next_direction = RIGHT
        self.score = 0
        self.alive = True
        self.food = self._place_food()

    def _place_food(self) -> tuple[int, int] | None:
        free = [
            (x, y)
            for x in range(self.cols)
            for y in range(self.rows)
            if (x, y) not in self.snake
        ]
        return self.rng.choice(free) if free else None

    def turn(self, new_direction: tuple[int, int]) -> None:
        """Queue a turn, ignoring 180-degree reversals into the snake's own neck."""
        dx, dy = new_direction
        if (dx + self.direction[0], dy + self.direction[1]) != (0, 0):
            self.next_direction = new_direction

    def step(self) -> None:
        """Advance one tick: move, eat, grow, or die."""
        if not self.alive:
            return
        self.direction = self.next_direction
        head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
        grows = head == self.food

        body = list(self.snake) if grows else list(self.snake)[:-1]
        out_of_bounds = not (0 <= head[0] < self.cols and 0 <= head[1] < self.rows)
        if out_of_bounds or head in body:
            self.alive = False
            return

        self.snake.appendleft(head)
        if grows:
            self.score += 1
            self.food = self._place_food()
            if self.food is None:  
                self.alive = False
        else:
            self.snake.pop()
          
def load_high_score() -> int:
    try:
        return int(HIGHSCORE_FILE.read_text())
    except (OSError, ValueError):
        return 0


def save_high_score(score: int) -> None:
    try:
        HIGHSCORE_FILE.write_text(str(score))
    except OSError:
        pass  


def draw_cell(screen, pos, color) -> None:
    x, y = pos
    pygame.draw.rect(screen, color, (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2), border_radius=6)


def draw_text(screen, font, text, center) -> None:
    surface = font.render(text, True, TEXT)
    screen.blit(surface, surface.get_rect(center=center))

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((COLS * CELL, ROWS * CELL))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    small, big = pygame.font.SysFont(None, 28), pygame.font.SysFont(None, 64)
    middle = (COLS * CELL // 2, ROWS * CELL // 2)

    game = SnakeGame()
    high_score = load_high_score()
    paused = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r and not game.alive:
                    game.reset()
                elif event.key in KEYS:
                    game.turn(KEYS[event.key])

        if not paused:
            was_alive = game.alive
            game.step()
            if was_alive and not game.alive and game.score > high_score:
                high_score = game.score
                save_high_score(high_score)

        screen.fill(BG)
        if game.food:
            draw_cell(screen, game.food, FOOD)
        for i, segment in enumerate(game.snake):
            draw_cell(screen, segment, HEAD if i == 0 else SNAKE)
        draw_text(screen, small, f"Score {game.score}   Best {high_score}", (110, 18))

        if not game.alive:
            draw_text(screen, big, "Game Over", middle)
            draw_text(screen, small, "Press R to restart", (middle[0], middle[1] + 50))
        elif paused:
            draw_text(screen, big, "Paused", middle)

        pygame.display.flip()
        clock.tick(min(BASE_FPS + game.score // 3, MAX_FPS))

    pygame.quit()


if __name__ == "__main__":
    main()
