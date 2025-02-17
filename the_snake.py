import random

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
DEFAULT_COLOR = (255, 255, 255)

# Координаты центра экрана для змейки
SNAKE_START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
# Координата (0, 0) для базовых объектов
DEFAULT_POSITION = (0, 0)

SPEED = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Base class for all game objects."""

    def __init__(self, position=DEFAULT_POSITION, color=DEFAULT_COLOR):
        self.position = position
        self.body_color = color

    def draw_cell(self, position, color):
        """Рисует клетку с указанным цветом.
        Если цвет не равен цвету фона, рисуется рамка.
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        # Рисуем рамку только если цвет клетки не совпадает с цветом фона
        if color != BOARD_BACKGROUND_COLOR:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Draws the game object."""
        ...


class Apple(GameObject):
    """Represents an apple in the game."""

    def __init__(self, occupied_positions=None):
        """Initializes the apple at a random, unoccupied position."""
        super().__init__(DEFAULT_POSITION, APPLE_COLOR)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Moves the apple to a random position not occupied by the snake."""
        while True:
            x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if occupied_positions is None or (x, y) not in occupied_positions:
                self.position = (x, y)
                break

    def draw(self):
        """Draws the apple on the screen."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Represents the snake in the game."""

    def __init__(self, position=SNAKE_START_POSITION, color=SNAKE_COLOR):
        """Initializes the snake with a starting position and direction."""
        super().__init__(position, color)
        self.length = 1
        self.positions = [self.position]
        # При старте игры движение вправо
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Updates the snake's direction if a new one is set."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Moves the snake by adding a new head and removing the tail."""
        x, y = self.get_head_position()
        dx, dy = self.direction

        # Переносим змейку на противоположную сторону, если вышла за границы
        new_x = (x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        self.positions.insert(0, new_head)
        # Хвост убираем, если длина превысила заданную; иначе None
        self.last = self.positions.pop() if len(self.positions) > self.length else None

    def draw(self):
        """Draws the snake on the screen."""
        # Рисуем голову
        self.draw_cell(self.positions[0], self.body_color)
        # Стираем хвост, если он был
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self):
        """Returns the position of the snake's head."""
        return self.positions[0]

    def reset(self):
        """Resets the snake to its initial state."""
        self.length = 1
        self.positions = [self.position]
        self.last = None
        self.next_direction = None
        # После столкновения движение в случайном направлении
        possible_directions = [UP, DOWN, LEFT, RIGHT]
        self.direction = random.choice(possible_directions)


DIRECTION_MAPPING = {
    (UP, pygame.K_LEFT): LEFT,
    (UP, pygame.K_RIGHT): RIGHT,
    (DOWN, pygame.K_LEFT): LEFT,
    (DOWN, pygame.K_RIGHT): RIGHT,
    (LEFT, pygame.K_UP): UP,
    (LEFT, pygame.K_DOWN): DOWN,
    (RIGHT, pygame.K_UP): UP,
    (RIGHT, pygame.K_DOWN): DOWN,
}


def handle_keys(game_object):
    """Handles keyboard events to change the game object's direction."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            else:
                new_direction = DIRECTION_MAPPING.get(
                    (game_object.direction, event.key),
                    game_object.direction
                )
                game_object.next_direction = new_direction


def main():
    """Main function that runs the game loop and updates the game state."""
    pygame.init()
    # Передаём позицию центра экрана (можно было оставить и по умолчанию)
    snake = Snake(position=SNAKE_START_POSITION)
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Если змейка съедает яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_positions=snake.positions)
        # Если змейка столкнулась с собой
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(occupied_positions=snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
