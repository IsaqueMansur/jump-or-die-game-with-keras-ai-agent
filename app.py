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
        self.x = 200
        self.y = SCREEN_HEIGHT - self.height - 10
        self.velocity = 10
        self.is_jumping = False
        self.jump_height = 150
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = True 

    def handle_input(self, keys):
        if keys[pygame.K_UP] and not self.is_jumping and self.on_ground:
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


class Game:
    def __init__(self):
        self.obstacle = Obstacle()
        self.player = Player(self.obstacle)
        self.score = 0
        self.clock = pygame.time.Clock()

    def show_text(self, text, x, y):
        render = font.render(text, True, (255, 255, 255))
        screen.blit(render, (x, y))

    def reset(self):
        self.score = 0
        self.player.y = SCREEN_HEIGHT - self.player.height - 10
        self.obstacle.reset()

    def check_collision(self):
        if self.player.rect.colliderect(self.obstacle.rect):
            print("Colisão")

    def check_pass(self):
        if not self.obstacle.passed_player and (self.obstacle.x + self.obstacle.width) < self.player.x:
            self.score += 1
            self.obstacle.passed_player = True
            self.obstacle.reset()
            
    def predict_jump_result(self):
        T = 2 * (self.player.jump_height / self.player.velocity)
        obstacle_final_x = self.obstacle.x - self.obstacle.velocity * T
        if self.player.x < obstacle_final_x:
            return "Pulo à toa"
        elif self.player.x < obstacle_final_x + self.obstacle.width:
            return "Colisão"
        else:
            return "Sucesso"

    def run(self):
        running = True
        while running:
            screen.fill((0, 0, 0)) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:
                print(self.predict_jump_result())
            self.player.handle_input(keys)
            self.player.update()
            self.obstacle.update()
            self.check_collision()
            self.check_pass() 

            self.player.draw()
            self.obstacle.draw()
            self.show_text(f"Pontos: {self.score}", 10, 10)

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
