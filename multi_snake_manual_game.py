import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

num_snakes = 3


# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 2

snake_control_keys = [
    # Control keys for first snake
    {
        str(pygame.K_RIGHT) : Direction.RIGHT ,
        str(pygame.K_LEFT) : Direction.LEFT ,
        str(pygame.K_UP) : Direction.UP ,
        str(pygame.K_DOWN) : Direction.DOWN 
    },
    # Control keys for second snake
    {
        str(pygame.K_d) : Direction.RIGHT ,
        str(pygame.K_a) : Direction.LEFT ,
        str(pygame.K_w) : Direction.UP ,
        str(pygame.K_s) : Direction.DOWN 
    },
    # Control keys for third snake
    {
        str(pygame.K_h) : Direction.RIGHT ,
        str(pygame.K_f) : Direction.LEFT ,
        str(pygame.K_t) : Direction.UP ,
        str(pygame.K_g) : Direction.DOWN 
    }
]
    
# Stores snake attributes such as
# - Direction snake is moving
# - Grid points snake takes up
# - Status on whether snake is alive or not
# - Snakes cumulative score

# Provides a method _move which enables SnakeGame to update the snakes position
class Snake:
    def __init__(self, head):
        self.direction = Direction.RIGHT        
        self.head = head
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.is_alive = True
        self.score = 0

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        self.head = Point(x, y)

# Responsible for:
# - Rewarding snake if it get's food (increasing it's length too)
# - Killing snake if it crashes
# - Reading input from keyboard
# - Displaying game environment

class SnakeGame:
    def __init__(self, num_snakes=1 , w=640, h=480):
        self.w = w
        self.h = h

        # init display
        self.scoreboard = ''
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        # init game state
        self.num_snakes = num_snakes
        self.snakes = []
        for i in range(num_snakes):
            # Snake heads start in different points hence the i dependance in Point()
            self.snakes.append(Snake(Point(3*i*BLOCK_SIZE, 3*i*BLOCK_SIZE)))

        self.food = None
        self._place_food()
        
    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        for snake in self.snakes:
            if self.food in snake.snake:
                self._place_food()
        
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                for nth_snake in range(self.num_snakes):
                    if str(event.key) in snake_control_keys[nth_snake]:
                        print(snake_control_keys[nth_snake][str(event.key)])
                        self.snakes[nth_snake].direction = snake_control_keys[nth_snake][str(event.key)]

        # 2. move snakes by updating the head of the snake - moving it one BLOCK in direction snake is moving
        for snake in self.snakes:
            if snake.is_alive:
                snake._move(snake.direction) # update the head
                snake.snake.insert(0, snake.head)

        # 3. check for collisions
        self.check_collisions()
        
        # 4. place new food if eaten - pop one pixel off end of moved snakes that did not eat food
        for snake in self.snakes:
            if snake.is_alive:
                if snake.head == self.food:
                    snake.score += 1
                    self._place_food()
                else:
                    #Only pop the tail off the snake if we do not reach food
                    snake.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. Check if game is over (i.e. are any snakes still alive)
        game_over = True
        for snake in self.snakes:
            if snake.is_alive == True:
                game_over = False
                break
        
        self.scoreboard = str([f'Snake_{i}: {snake.score}' for (i, snake) in enumerate(self.snakes)])
        return game_over, self.scoreboard

    def check_collisions(self):
        # we need to set a local flag to kill each snake - and only update each snakes alive status after checking them all? Or we could remove snakes points at the end of loop they die?
        snakes_just_killed = []

        for snake in self.snakes:
            if snake.is_alive:
                #hits another snake - if so, kill both snakes (problem here if a third snake hit the second snake - it wouldn't die)
                if len(self.snakes) > 1:
                    for snake2 in self.snakes:
                        if snake2 != snake and snake2.is_alive:
                            if snake.head in snake2.snake:
                                snakes_just_killed.append(snake)
                                snakes_just_killed.append(snake2)

                # hits boundary
                if snake.head.x > self.w - BLOCK_SIZE or snake.head.x < 0 or snake.head.y > self.h - BLOCK_SIZE or snake.head.y < 0:
                    snake.is_alive = False
                
                # hits itself
                if snake.head in snake.snake[1:]:
                    snake.is_alive = False
        
        for snake in snakes_just_killed:
            snake.is_alive = False
    
    def _update_ui(self):
        self.display.fill(BLACK)
        for snake in self.snakes:
            if snake.is_alive:
                for pt in snake.snake:
                    pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
                
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + self.scoreboard, True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        

if __name__ == '__main__':
    game = SnakeGame(num_snakes)
    # game loop
    while True:
        game_over, scoreboard = game.play_step()
        
        if game_over == True:
            break
        
    print('Results: ', scoreboard )
        
    pygame.quit()            