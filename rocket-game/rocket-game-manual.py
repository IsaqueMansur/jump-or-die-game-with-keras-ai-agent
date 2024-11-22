import pygame
import os

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

ROCKET_WIDTH, ROCKET_HEIGHT = 50, 70
ROCKET_DEFAULT_SPEED = 0.7
ROCKET_MAX_SPEED = 5

rocket_image = pygame.transform.scale(pygame.image.load(os.path.join('F:/repositories/minigame-python/rocket-game/rocket.png')), (ROCKET_WIDTH, ROCKET_HEIGHT))
rocket_x, rocket_y = SCREEN_WIDTH // 2 - ROCKET_WIDTH // 2, SCREEN_HEIGHT - ROCKET_HEIGHT
rocket_speed = ROCKET_DEFAULT_SPEED
rocket_speed_up = 1.02
rocket_gravity_down = 1.05
rocket_gravity_desaceleration = 0.95
rocket_max_gravity_down = 2.3
rocket_started_up_on_gravity_down = False
rocket_win_gravity_down = False
rocket_start_desacelerattion = False



move_left = move_right = thrust = False

started_thrust = False

clock = pygame.time.Clock()
FPS = 60

def draw_rocket(x, y):
    screen.blit(rocket_image, (x, y))

try:
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:  
                if event.key == pygame.K_w:
                    thrust = True
                if event.key == pygame.K_a:
                    move_left = True
                if event.key == pygame.K_d:
                    move_right = True
            elif event.type == pygame.KEYUP:  
                if event.key == pygame.K_w:
                    thrust = False
                if event.key == pygame.K_a:
                    move_left = False
                if event.key == pygame.K_d:
                    move_right = False
                    
        if rocket_y == (SCREEN_HEIGHT - ROCKET_HEIGHT):
            rocket_started_up_on_gravity_down = False
            rocket_win_gravity_down = False
            rocket_start_desacelerattion = False
            
            
                
                    
        if rocket_y < (SCREEN_HEIGHT - ROCKET_HEIGHT) and not thrust and not rocket_started_up_on_gravity_down:
            
            if rocket_y < (SCREEN_HEIGHT - ROCKET_HEIGHT) and not rocket_start_desacelerattion:
                rocket_start_desacelerattion = True
                rocket_speed = ROCKET_DEFAULT_SPEED
            else:
                rocket_win_gravity_down = False
                started_thrust = False
                rocket_y += rocket_speed
            
            if rocket_speed < ROCKET_MAX_SPEED:
                rocket_speed *= rocket_gravity_down
            
        if rocket_started_up_on_gravity_down:
            if rocket_speed > ROCKET_DEFAULT_SPEED:
                rocket_speed *= rocket_gravity_desaceleration
                rocket_y += rocket_speed
            else:
                rocket_started_up_on_gravity_down = False
                rocket_win_gravity_down = True
                

        if thrust and not rocket_started_up_on_gravity_down:
            if not rocket_win_gravity_down:
                rocket_start_desacelerattion = False
                rocket_started_up_on_gravity_down = True
            
            started_thrust = True
                          
            rocket_y -= rocket_speed
            
            if rocket_speed < ROCKET_MAX_SPEED:
                rocket_speed *= rocket_speed_up    
                 
        if move_left:
            rocket_x -= rocket_speed
        if move_right:
            rocket_x += rocket_speed
            
            
        if (rocket_y == SCREEN_HEIGHT - ROCKET_HEIGHT):
            rocket_speed = ROCKET_DEFAULT_SPEED

        if rocket_x < 0:
            rocket_x = 0
        elif rocket_x > SCREEN_WIDTH - ROCKET_WIDTH:
            rocket_x = SCREEN_WIDTH - ROCKET_WIDTH
        if rocket_y < 0:
            rocket_y = 0
        elif rocket_y > SCREEN_HEIGHT - ROCKET_HEIGHT:
            rocket_y = SCREEN_HEIGHT - ROCKET_HEIGHT

        screen.fill(BLACK)

        draw_rocket(rocket_x, rocket_y)

        pygame.display.update()

        clock.tick(FPS)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    pygame.quit()
    input("Press enter to exit...")