import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pula ou morre")

font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = 100
        self.y = SCREEN_HEIGHT - self.height - 10
        self.velocity = 10
        self.is_jumping = False
        self.jump_height = 150
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = True 

    def jump(self):
        if self.on_ground:
            self.is_jumping = True
            self.jump_peak = self.y - self.jump_height
            self.on_ground = False

    def update(self):
        if self.is_jumping:
            if self.y > self.jump_peak:
                self.y -= self.velocity
            else:
                self.is_jumping = False
        elif self.y < SCREEN_HEIGHT - self.height - 10:
            self.y += self.velocity
        else:
            self.on_ground = True
            self.y = SCREEN_HEIGHT - self.height - 10

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)


class Obstacle:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - self.height - 10
        self.velocity = random.randint(6, 10)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.passed_player = False

    def update(self):
        self.x -= self.velocity
        if self.x < -self.width:
            self.reset()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def reset(self):
        self.x = SCREEN_WIDTH
        self.velocity = random.randint(6, 12)
        self.passed_player = False

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        
        
class Coin:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - self.height - 100
        self.velocity = random.randint(9, 25)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.passed_player = False

    def update(self):
        self.x -= self.velocity
        if self.x <= 0:
            self.reset()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def reset(self):
        self.x = SCREEN_WIDTH
        self.velocity = random.randint(9, 25)
        self.passed_player = False

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 0), self.rect)


class Game:
    def __init__(self):
        self.obstacle = Obstacle()
        self.player = Player()
        self.coin = Coin()
        self.score = 0
        self.coins = 0
        self.errors = 0

    def show_text(self, text, x, y, color=(255, 255, 255)):
        render = font.render(text, True, color)
        screen.blit(render, (x, y))

    def reset(self):
        self.score = 0
        self.errors = 0
        self.player.y = SCREEN_HEIGHT - self.player.height - 10
        self.obstacle.reset()

    def check_collision(self):
        player_final = self.player.x + self.player.width
        obstacle_final = self.obstacle.x + self.obstacle.width
        if obstacle_final < self.player.x: return 0.5
        if self.player.y >= self.obstacle.y and (player_final >= self.obstacle.x):
            self.errors += 1  
            self.obstacle.reset()
            return -5
        if self.player.y < self.obstacle.y and (obstacle_final <= self.player.x):
            self.errors += 1
            self.obstacle.reset()
            return -5
        return 0
    
    def check_capture_coin(self):
        player_final = self.player.x + self.player.width
        coin_final = self.coin.x + self.coin.width
        if coin_final < self.player.x: return 0
        if self.player.y <= self.coin.y and (player_final >= self.coin.x):
            self.coins += 1
            self.coin.reset()
            return 20
        if self.player.y <= self.coin.y and (coin_final <= self.player.x):
            self.coins += 1
            self.coin.reset()
        return 0
     

    def check_pass(self):
        if (self.obstacle.x + self.obstacle.width) < self.player.x:
            self.score += 1
            self.obstacle.passed_player = True
            self.obstacle.reset()
            return 20 
        return 0

    def run(self):
        running = True
        while running:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump() 

            self.player.update()
            self.obstacle.update()
            self.coin.update()

            self.check_collision()
            self.check_capture_coin()
            self.check_pass()

            self.player.draw()
            self.obstacle.draw()
            self.coin.draw()
            self.show_text(f"Pontos: {self.score}", 10, 10)
            self.show_text(f"Moedas: {self.coins}", 10, 30, color=(255, 255, 0))
            self.show_text(f"Erros: {self.errors}", 10, 50, color=(255, 0, 0))  # Exibir erros em vermelho

            pygame.display.flip()
            pygame.time.Clock().tick(50)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
