import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pula ou morre")

font = pygame.font.Font(None, 36)

class Player:
    def __init__(self, obstacle):
        self.obstacle = obstacle
        self.width = 50
        self.height = 50
        self.x = 100
        self.y = SCREEN_HEIGHT - self.height - 10
        self.velocity = 10
        self.is_jumping = False
        self.jump_height = 150
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = True 

    def handle_input(self, keys):
        if keys[pygame.K_UP] and not self.is_jumping and self.on_ground and not self.obstacle.player_jumped_this:
            self.is_jumping = True
            self.jump_peak = self.y - self.jump_height
            self.on_ground = False 
            self.obstacle.player_jumped_this = True

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
        self.player_jumped_this = False

    def update(self):
        self.x -= self.velocity
        if self.x < -self.width:
            self.reset()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def reset(self):
        self.x = SCREEN_WIDTH
        self.velocity = random.randint(4, 10)
        self.passed_player = False
        self.player_jumped_this = False

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)


class Game:
    def __init__(self):
        self.obstacle = Obstacle()
        self.player = Player(self.obstacle)
        self.score = 0
        self.clock = pygame.time.Clock()
        self.game_over = False

    def show_text(self, text, x, y):
        render = font.render(text, True, (255, 255, 255))
        screen.blit(render, (x, y))

    def reset(self):
        self.game_over = False
        self.score = 0
        self.player.y = SCREEN_HEIGHT - self.player.height - 10
        self.obstacle.reset()

    def check_collision(self):
        if self.player.rect.colliderect(self.obstacle.rect):
            self.game_over = True

    def check_pass(self):
        if not self.obstacle.passed_player and (self.obstacle.x + self.obstacle.width) < self.player.x and self.obstacle.player_jumped_this:
            self.score += 1
            self.obstacle.passed_player = True

    def run(self):
        running = True
        while running:
            screen.fill((0, 0, 0)) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if not self.game_over:
                self.player.handle_input(keys)
                self.player.update()
                print(self.player.is_jumping)
                self.obstacle.update()
                self.check_collision()
                self.check_pass() 

            else:
                if keys[pygame.K_r]:
                    self.reset()

            self.player.draw()
            self.obstacle.draw()
            self.show_text(f"Pontos: {self.score}", 10, 10)
            if self.game_over:
                self.show_text("Fim de Jogo! Pressione R para reiniciar", 200, 200)

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
