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
SPEED = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


def draw_cell(position, color, border=True):
    """Отрисовывает одну ячейку с заданным цветом и опциональной границей."""
    rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, color, rect)
    if border:
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class GameObject:
    """Базовый класс для всех игровых объектов."""
    def __init__(self, position=(0, 0), color=(255, 255, 255)):
        self.position = position
        self.body_color = color

    def draw(self):
        pass


class Apple(GameObject):
    """Класс яблока, появляется в случайной позиции."""
    def __init__(self, occupied_positions=None):
        # Инициализируем объект с пустой позицией, затем задаём случайную
        super().__init__((0, 0), APPLE_COLOR)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Перемещает яблоко в случайную позицию, не занятую змейкой."""
        while True:
            x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if occupied_positions is None or (x, y) not in occupied_positions:
                self.position = (x, y)
                break

    def draw(self):
        """Отрисовывает яблоко на экране."""
        draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки, управляет её движением и отрисовкой."""
    def __init__(self, color=SNAKE_COLOR):
        super().__init__((GRID_SIZE, GRID_SIZE), color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление, если задано новое."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку, добавляя новую голову и удаляя хвост."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        new_head = (x + dx * GRID_SIZE, y + dy * GRID_SIZE)
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Отрисовывает змейку: отрисовывает новую голову и затирает хвост."""
        # Отрисовываем новую голову
        draw_cell(self.positions[0], self.body_color)
        # Стираем старую ячейку хвоста
        if self.last:
            draw_cell(self.last, BOARD_BACKGROUND_COLOR, border=False)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки к начальному."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


# Словарь для смены направления, где (текущее направление, нажатая клавиша) → новое направление
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
    """Обрабатывает клавиатуру для изменения направления движения."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            else:
                new_direction = DIRECTION_MAPPING.get((game_object.direction, event.key), game_object.direction)
                game_object.next_direction = new_direction


def main():
    """Основная функция игры, запускает цикл событий и отрисовку."""
    pygame.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    # Первоначальная очистка экрана – при сбросе змейки она также вызывается
    screen.fill(BOARD_BACKGROUND_COLOR)
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        # Если голова змейки съела яблоко, увеличиваем длину и переставляем яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_positions=snake.positions)
        # Если змейка столкнулась сама с собой – сбрасываем её и переставляем яблоко
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(occupied_positions=snake.positions)
            # При сбросе очищаем экран, чтобы не оставалось старых фрагментов змейки
            screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
