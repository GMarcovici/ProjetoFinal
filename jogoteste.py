import pygame, random, math

# Inicialização
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Duel Minigames")

# Cores e Fontes
WHITE, BLACK, RED, BLUE, GREEN, YELLOW, ORANGE = ((255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 165, 0))
font = pygame.font.SysFont('Arial', 30)
big_font = pygame.font.SysFont('Arial', 50)
clock = pygame.time.Clock()
FPS = 60

# Classes -------------------------------------------------------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, shoot_key):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = color
        self.speed = 5
        self.controls = controls 
        self.shoot_key = shoot_key
        self.direction = "right"
        self.lives = 3
        self.cooldown = 0
        self.cooldown_max = 15
        self.bullets = pygame.sprite.Group()
    
    def update(self, obstacles):
        keys = pygame.key.get_pressed()
        new_rect = self.rect.copy()
        
        if keys[self.controls[0]]:  # up
            new_rect.y -= self.speed
            self.direction = "up"
        if keys[self.controls[1]]:  # down
            new_rect.y += self.speed
            self.direction = "down"
        if keys[self.controls[2]]:  # left
            new_rect.x -= self.speed
            self.direction = "left"
        if keys[self.controls[3]]:  # right
            new_rect.x += self.speed
            self.direction = "right"
        
        # Check obstacle collision
        can_move = True
        for obstacle in obstacles:
            if new_rect.colliderect(obstacle.rect):
                can_move = False
                break
        
        if can_move:
            # Keep within screen bounds
            new_rect.x = max(0, min(WIDTH - self.rect.width, new_rect.x))
            new_rect.y = max(0, min(HEIGHT - self.rect.height, new_rect.y))
            self.rect = new_rect
    
    def shoot(self):
        if self.cooldown <= 0:
            bullet_speed = 7
            if self.direction == "right":
                bullet = Bullet(self.rect.right, self.rect.centery - 2, bullet_speed, 0, self.color)
            elif self.direction == "left":
                bullet = Bullet(self.rect.left - 5, self.rect.centery - 2, -bullet_speed, 0, self.color)
            elif self.direction == "up":
                bullet = Bullet(self.rect.centerx - 2, self.rect.top - 5, 0, -bullet_speed, self.color)
            elif self.direction == "down":
                bullet = Bullet(self.rect.centerx - 2, self.rect.bottom, 0, bullet_speed, self.color)
            
            self.bullets.add(bullet)
            self.cooldown = self.cooldown_max
    
    def update_bullets(self, obstacles, enemies=None, other_player=None):
        if self.cooldown > 0:
            self.cooldown -= 1
        
        self.bullets.update()
        
        # Remove off-screen bullets
        for bullet in self.bullets.copy():
            if (bullet.rect.right < 0 or bullet.rect.left > WIDTH or
                bullet.rect.bottom < 0 or bullet.rect.top > HEIGHT):
                bullet.kill()
        
        # Check collisions with obstacles
        for obstacle in obstacles:
            pygame.sprite.spritecollide(obstacle, self.bullets, True)
        
        # Check collisions with enemies
        if enemies:
            for enemy in enemies:
                if pygame.sprite.spritecollide(enemy, self.bullets, True):
                    enemy.kill()
        
        # Check collision with other player
        if other_player:
            if pygame.sprite.spritecollide(other_player, self.bullets, True):
                other_player.lives -= 1
    
    def draw_lives(self, surface):
        life_color = GREEN if self.lives >= 3 else YELLOW if self.lives == 2 else RED
        for i in range(self.lives):
            pygame.draw.rect(surface, life_color, (self.rect.x + i * 10, self.rect.y - 15, 8, 8))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, color):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = color
        self.dx = dx
        self.dy = dy
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = WHITE

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = RED
        self.speed = 2
        self.bullets = pygame.sprite.Group()
        self.cooldown = random.randint(30, 90)
    
    def update(self, players):
        # Find closest player
        closest_player = min(players, key=lambda p: math.hypot(
            self.rect.centerx - p.rect.centerx, 
            self.rect.centery - p.rect.centery))
        
        dx = closest_player.rect.centerx - self.rect.centerx
        dy = closest_player.rect.centery - self.rect.centery
        dist = max(1, math.hypot(dx, dy))
        
        self.rect.x += (dx / dist) * self.speed
        self.rect.y += (dy / dist) * self.speed
    
    def shoot(self):
        if self.cooldown <= 0:
            bullet_speed = 4
            # Shoot in 4 directions
            self.bullets.add(
                Bullet(self.rect.centerx, self.rect.top, 0, -bullet_speed, YELLOW),
                Bullet(self.rect.centerx, self.rect.bottom, 0, bullet_speed, YELLOW),
                Bullet(self.rect.left, self.rect.centery, -bullet_speed, 0, YELLOW),
                Bullet(self.rect.right, self.rect.centery, bullet_speed, 0, YELLOW)
            )
            self.cooldown = random.randint(60, 120)
        else:
            self.cooldown -= 1
    
    def update_bullets(self, players, obstacles):
        self.bullets.update()
        
        # Remove off-screen bullets
        for bullet in self.bullets.copy():
            if (bullet.rect.right < 0 or bullet.rect.left > WIDTH or
                bullet.rect.bottom < 0 or bullet.rect.top > HEIGHT):
                bullet.kill()
        
        # Check collisions with obstacles
        for obstacle in obstacles:
            pygame.sprite.spritecollide(obstacle, self.bullets, True)
        
        # Check collisions with players
        for player in players:
            if pygame.sprite.spritecollide(player, self.bullets, True):
                player.lives -= 1

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('bosspygame.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH//2 - 30
        self.rect.y = HEIGHT//2 - 30
        self.color = RED
        self.speed = 4
        self.bullets = pygame.sprite.Group()
        self.cooldown = 0
        self.cooldown_max = 30
        self.health = 20
        self.move_direction = 1
        self.start_delay = 2 * FPS
    
    def update(self):
        if self.start_delay > 0:
            self.start_delay -= 1
            return
            
        self.rect.x += self.speed * self.move_direction
        
        if self.rect.left <= 0:
            self.move_direction = 1
        elif self.rect.right >= WIDTH:
            self.move_direction = -1
    
    def shoot(self):
        if self.start_delay > 0:
            return
            
        if self.cooldown <= 0:
            bullet_speed = 5
            num_bullets = 12
            
            for i in range(num_bullets):
                angle = (2 * math.pi / num_bullets) * i
                dx = math.cos(angle) * bullet_speed
                dy = math.sin(angle) * bullet_speed
                
                self.bullets.add(Bullet(
                    self.rect.centerx,
                    self.rect.centery,
                    dx, dy, YELLOW
                ))
            
            self.cooldown = self.cooldown_max
        else:
            self.cooldown -= 1
    
    def update_bullets(self, players):
        self.bullets.update()
        
        # Remove off-screen bullets
        for bullet in self.bullets.copy():
            if (bullet.rect.right < 0 or bullet.rect.left > WIDTH or
                bullet.rect.bottom < 0 or bullet.rect.top > HEIGHT):
                bullet.kill()
        
        # Check collisions with players
        for player in players:
            if pygame.sprite.spritecollide(player, self.bullets, True):
                player.lives -= 1
    
    def take_hit(self):
        self.health -= 1
        if self.health <= 10:
            self.image.fill(ORANGE)
    
    def draw_health(self, surface):
        health_width = self.rect.width * (self.health / 20)
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, self.rect.width, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, health_width, 5))

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Carrega a imagem da bola de futebol
        self.image = pygame.image.load('bolafutebolpygame-1.png.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))  # Ajusta o tamanho para 30x30
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH//2 - 15
        self.rect.y = HEIGHT//2 - 15
        self.dx = random.choice([-4, -3, 3, 4])
        self.dy = random.choice([-4, -3, 3, 4])
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Bounce off top and bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1
        
        # Bounce off sides
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.dx *= -1
        
        # Keep ball on screen
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))
#----------------------------------------------------------------------------------------------------------------------Classes





# Funções ---------------------------------------------------------------------------------------------------------------------
def draw_text(text, font, color, x, y, surface, centered=True):
    text_surface = font.render(text, True, color)
    if centered:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    surface.blit(text_surface, text_rect)

def title_screen():
    state = "main"  # Can be "main" or "instructions"
    pulse_timer = 0  # For pulsing text effect
    pulse_max = 30  # Frames for one pulse cycle
    
    while True:
        screen.fill(BLACK)
        
        if state == "main":
            # Draw title
            draw_text("Duelo de Jogadores", big_font, WHITE, WIDTH//2, HEIGHT//3, screen)
            
            # Pulsing "Press ENTER to Start" text
            pulse_scale = 1 + 0.1 * math.sin(2 * math.pi * pulse_timer / pulse_max)
            start_text = font.render("Pressione ENTER para Iniciar", True, WHITE)
            start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            start_rect = start_rect.inflate(start_rect.width * (pulse_scale - 1), 
                                         start_rect.height * (pulse_scale - 1))
            screen.blit(pygame.transform.scale(start_text, start_rect.size), 
                       start_rect)
            
            # Instructions prompt
            draw_text("Pressione I para Instruções", font, YELLOW, WIDTH//2, HEIGHT*2//3, screen)
            
            # Exit prompt
            draw_text("Pressione ESC para Sair", font, RED, WIDTH//2, HEIGHT*3//4, screen)
        
        elif state == "instructions":
            draw_text("Instruções", big_font, WHITE, WIDTH//2, HEIGHT//5, screen)
            draw_text("Jogador 1: WASD para mover, ESPAÇO para atirar", font, BLUE, WIDTH//2, HEIGHT*2//5, screen)
            draw_text("Jogador 2: Setas para mover, ENTER para atirar", font, RED, WIDTH//2, HEIGHT*3//5, screen)
            draw_text("Pressione ENTER para Voltar", font, WHITE, WIDTH//2, HEIGHT*4//5, screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False
                if event.key == pygame.K_RETURN:
                    if state == "main":
                        return True  # Start the game
                    else:
                        state = "main"  # Return to main menu
                if event.key == pygame.K_i and state == "main":
                    state = "instructions"
        
        pulse_timer = (pulse_timer + 1) % pulse_max
        clock.tick(FPS)

def show_game_over(winner):
    while True:
        screen.fill(BLACK)
        
        if winner == 0:
            draw_text("Empate!", big_font, WHITE, WIDTH//2, HEIGHT//2 - 50, screen)
        else:
            color = BLUE if winner == 1 else RED
            draw_text(f"Jogador {winner} venceu!", big_font, color, WIDTH//2, HEIGHT//2 - 50, screen)
        
        draw_text("Pressione ENTER para sair", font, WHITE, WIDTH//2, HEIGHT//2 + 50, screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        
        clock.tick(FPS)
#--------------------------------------------------------------------------------------------------------------------Funções




# Níveis ---------------------------------------------------------------------------------------------------------------------
def level_1(player1, player2):
    obstacles = [
        Obstacle(0, 0, 20, HEIGHT),
        Obstacle(0, 0, WIDTH, 20),
        Obstacle(WIDTH-20, 0, 20, HEIGHT),
        Obstacle(0, HEIGHT-20, WIDTH, 20),
        Obstacle(0, HEIGHT*0.6, WIDTH*0.35, 50),
        Obstacle(110, HEIGHT*0.79, WIDTH*0.32, 60),
        Obstacle(WIDTH*0.55, HEIGHT*0.45, 50, HEIGHT*0.40),
        Obstacle(WIDTH*0.18, HEIGHT*0.20, WIDTH*0.39, 60),
        Obstacle(WIDTH*0.34, 220, 50, HEIGHT*0.20),
        Obstacle(WIDTH*0.69, 100, WIDTH*0.20, HEIGHT*0.35),
        Obstacle(WIDTH*0.15, HEIGHT*0.40, 100, 90)
    ]
    
    # Valid enemy positions
    valid_positions = []
    for x, y in [(100,100),(900,100),(200,300),(700,200),
                (300,400),(600,100),(100,600),(800,600),
                (400,700),(700,500)]:
        temp_rect = pygame.Rect(x, y, 25, 25)
        if not any(temp_rect.colliderect(o.rect) for o in obstacles):
            valid_positions.append((x, y))
    
    enemies = pygame.sprite.Group()
    enemies_to_spawn = [Enemy(*random.choice(valid_positions)) for _ in range(5)]
    enemy_spawn_timer = 3 * FPS
    
    # Position players
    for player in [player1, player2]:
        while True:
            player.rect.x = random.randint(0, WIDTH - player.rect.width)
            player.rect.y = random.randint(0, HEIGHT - player.rect.height)
            if not any(player.rect.colliderect(o.rect) for o in obstacles):
                break
    
    running = True
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            if event.type == pygame.KEYDOWN:
                if event.key == player1.shoot_key:
                    player1.shoot()
                if event.key == player2.shoot_key:
                    player2.shoot()
        
        player1.update(obstacles)
        player2.update(obstacles)
        
        player1.update_bullets(obstacles, enemies, player2)
        player2.update_bullets(obstacles, enemies, player1)
        
        if enemy_spawn_timer > 0:
            enemy_spawn_timer -= 1
        elif enemies_to_spawn:
            enemies.add(enemies_to_spawn.pop())
            enemy_spawn_timer = 1 * FPS
        
        for enemy in enemies:
            enemy.update([player1, player2])
            enemy.shoot()
            enemy.update_bullets([player1, player2], obstacles)
        
        for obstacle in obstacles:
            screen.blit(obstacle.image, obstacle.rect)
        
        enemies.draw(screen)
        screen.blit(player1.image, player1.rect)
        screen.blit(player2.image, player2.rect)
        
        player1.draw_lives(screen)
        player2.draw_lives(screen)
        
        player1.bullets.draw(screen)
        player2.bullets.draw(screen)
        for enemy in enemies:
            enemy.bullets.draw(screen)
        
        draw_text(f"Placar: J1 - {player1_score} x J2 - {player2_score}", font, WHITE, WIDTH//2, 10, screen)
        
        if player1.lives <= 0 or player2.lives <= 0:
            running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return 1 if player1.lives > 0 and player2.lives <= 0 else 2 if player2.lives > 0 and player1.lives <= 0 else 0

def level_2(player1, player2):
    player1.rect.x = WIDTH // 2 - player1.rect.width // 2
    player1.rect.y = HEIGHT - 50
    player1.direction = "up"
    
    player2.rect.x = WIDTH // 2 - player2.rect.width // 2
    player2.rect.y = 20
    player2.direction = "down"
    
    boss = Boss()
    
    running = True
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            if event.type == pygame.KEYDOWN:
                if event.key == player1.shoot_key:
                    player1.shoot()
                if event.key == player2.shoot_key:
                    player2.shoot()
        
        keys = pygame.key.get_pressed()
        
        if keys[player1.controls[2]]:  # left
            player1.rect.x = max(0, player1.rect.x - player1.speed)
        if keys[player1.controls[3]]:  # right
            player1.rect.x = min(WIDTH - player1.rect.width, player1.rect.x + player1.speed)
        
        if keys[player2.controls[2]]:  # left
            player2.rect.x = max(0, player2.rect.x - player2.speed)
        if keys[player2.controls[3]]:  # right
            player2.rect.x = min(WIDTH - player2.rect.width, player2.rect.x + player2.speed)
        
        player1.update_bullets([], None, player2)
        player2.update_bullets([], None, player1)
        
        for bullet in player1.bullets:
            if bullet.rect.colliderect(boss.rect):
                boss.take_hit()
                bullet.kill()
        
        for bullet in player2.bullets:
            if bullet.rect.colliderect(boss.rect):
                boss.take_hit()
                bullet.kill()
        
        boss.update()
        boss.shoot()
        boss.update_bullets([player1, player2])
        
        screen.blit(player1.image, player1.rect)
        screen.blit(player2.image, player2.rect)
        screen.blit(boss.image, boss.rect)
        
        player1.draw_lives(screen)
        player2.draw_lives(screen)
        boss.draw_health(screen)
        
        player1.bullets.draw(screen)
        player2.bullets.draw(screen)
        boss.bullets.draw(screen)
        
        draw_text(f"Placar: J1 - {player1_score} x J2 - {player2_score}", font, WHITE, WIDTH//2, 10, screen)
        
        if player1.lives <= 0 or player2.lives <= 0 or boss.health <= 0:
            running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    if player1.lives > 0 and player2.lives <= 0:
        return 1
    elif player2.lives > 0 and player1.lives <= 0:
        return 2
    else:
        return 1 if player1.lives > player2.lives else 2 if player2.lives > player1.lives else 0

def level_3(player1, player2):
    player1.rect.x = WIDTH // 4 - player1.rect.width // 2
    player1.rect.y = HEIGHT // 2 - player1.rect.height // 2
    player1.direction = "right"
    player1.float_speed = 2
    
    player2.rect.x = 3 * WIDTH // 4 - player2.rect.width // 2
    player2.rect.y = HEIGHT // 2 - player2.rect.height // 2
    player2.direction = "left"
    player2.float_speed = 2
    
    global_direction = 1
    timer = 3 * FPS
    game_started = False
    winner = 0
    
    running = True
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            
            if game_started and event.type == pygame.KEYDOWN:
                if event.key == player1.shoot_key and len(player1.bullets) == 0:
                    player1.shoot()
                    for bullet in player1.bullets:
                        if bullet.rect.colliderect(player2.rect):
                            winner = 1
                            running = False
                
                if event.key == player2.shoot_key and len(player2.bullets) == 0:
                    player2.shoot()
                    for bullet in player2.bullets:
                        if bullet.rect.colliderect(player1.rect):
                            winner = 2
                            running = False
        
        if game_started:
            player1.rect.y += player1.float_speed * global_direction
            player2.rect.y -= player2.float_speed * global_direction
            
            if (player1.rect.y <= HEIGHT // 4 or player1.rect.y >= 3 * HEIGHT // 4 or
                player2.rect.y <= HEIGHT // 4 or player2.rect.y >= 3 * HEIGHT // 4):
                global_direction *= -1
        else:
            timer -= 1
            if timer <= 0:
                game_started = True
            else:
                draw_text(str(int(timer / FPS) + 1), big_font, WHITE, WIDTH//2, HEIGHT//2, screen)
        
        if game_started:
            player1.update_bullets([], None, player2)
            player2.update_bullets([], None, player1)
            
            for bullet in player1.bullets:
                if bullet.rect.colliderect(player2.rect):
                    winner = 1
                    running = False
            
            for bullet in player2.bullets:
                if bullet.rect.colliderect(player1.rect):
                    winner = 2
                    running = False
        
        screen.blit(player1.image, player1.rect)
        screen.blit(player2.image, player2.rect)
        
        player1.draw_lives(screen)
        player2.draw_lives(screen)
        
        player1.bullets.draw(screen)
        player2.bullets.draw(screen)
        
        draw_text(f"Placar: J1 - {player1_score} x J2 - {player2_score}", font, WHITE, WIDTH//2, 10, screen)
        
        if player1.lives <= 0 or player2.lives <= 0:
            winner = 1 if player2.lives <= 0 else 2 if player1.lives <= 0 else 0
            running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return winner

def level_4(player1, player2):
    player1.rect.x = WIDTH // 4 - player1.rect.width // 2
    player1.rect.y = HEIGHT // 2 - player1.rect.height // 2
    player1.direction = "right"
    
    player2.rect.x = 3 * WIDTH // 4 - player2.rect.width // 2
    player2.rect.y = HEIGHT // 2 - player2.rect.height // 2
    player2.direction = "left"
    
    square_size = 50
    square = pygame.Rect(WIDTH*0.5 - square_size*1.7, HEIGHT*0.5 - square_size*3.5, square_size, square_size)
    square_color = RED
    square_change_time = random.randint(2, 4) * FPS
    square_timer = 0
    can_shoot = False
    winner = 0
    shot_fired = False
    
    green_square = pygame.image.load('farolverde-1.png.png').convert_alpha()
    green_square = pygame.transform.scale(green_square, (150, 150))
    red_square = pygame.image.load('farolvermelho-1.png.png').convert_alpha()
    red_square = pygame.transform.scale(red_square, (150, 150))

    running = True
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            
            if can_shoot and not shot_fired and event.type == pygame.KEYDOWN:
                if event.key == player1.shoot_key:
                    player1.shoot()
                    shot_fired = True
                
                if event.key == player2.shoot_key:
                    player2.shoot()
                    shot_fired = True
        
        square_timer += 1
        if square_timer >= square_change_time:
            if square_color == RED:
                square_color = GREEN
                can_shoot = True
                shot_fired = False
                square_change_time = 1 * FPS
            else:
                square_color = RED
                can_shoot = False
                square_change_time = random.randint(2, 4) * FPS
            square_timer = 0
        
        player1.update_bullets([], None, player2 if shot_fired and player1.bullets else None)
        player2.update_bullets([], None, player1 if shot_fired and player2.bullets else None)
        
        if shot_fired:
            for bullet in player1.bullets:
                if bullet.rect.colliderect(player2.rect):
                    winner = 1
                    running = False
            
            for bullet in player2.bullets:
                if bullet.rect.colliderect(player1.rect):
                    winner = 2
                    running = False
        
        if player1.lives <= 0 or player2.lives <= 0:
            running = False
        
        screen.blit(player1.image, player1.rect)
        screen.blit(player2.image, player2.rect)
        
        player1.draw_lives(screen)
        player2.draw_lives(screen)
        
        if square_color == GREEN:
            screen.blit(green_square, square)
        else:
            screen.blit(red_square, square)
        
        if can_shoot and not shot_fired:
            draw_text("ATIRE AGORA!", font, WHITE, WIDTH//2, HEIGHT//2 + 70, screen)
        elif can_shoot and shot_fired:
            draw_text("TIRO DISPARADO!", font, YELLOW, WIDTH//2, HEIGHT//2 + 70, screen)
        else:
            draw_text("Espere o quadrado ficar verde...", font, WHITE, WIDTH//2, HEIGHT//2 + 70, screen)
        
        draw_text(f"Placar: J1 - {player1_score} x J2 - {player2_score}", font, WHITE, WIDTH//2, 10, screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return 1 if player2.lives <= 0 else 2 if player1.lives <= 0 else 0

def level_5(player1, player2):
    player1.rect.x = 50
    player1.rect.y = HEIGHT // 2 - player1.rect.height // 2
    player1.direction = "right"
    player1.speed = 8
    
    player2.rect.x = WIDTH - 50 - player2.rect.width
    player2.rect.y = HEIGHT // 2 - player2.rect.height // 2
    player2.direction = "left"
    player2.speed = 8
    
    # ...existing code...
    ball = Ball()
    goals_p1 = 0
    goals_p2 = 0

    goal_width = 30
    goal_height = 150
    goal1 = pygame.Rect(0, HEIGHT//2 - goal_height//2, goal_width, goal_height)
    goal2 = pygame.Rect(WIDTH - goal_width, HEIGHT//2 - goal_height//2, goal_width, goal_height)

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0

        keys = pygame.key.get_pressed()

        # Player 1 movement
        if keys[player1.controls[0]]:  # w - up
            player1.rect.y = max(0, player1.rect.y - player1.speed)
        if keys[player1.controls[1]]:  # s - down
            player1.rect.y = min(HEIGHT - player1.rect.height, player1.rect.y + player1.speed)
        if keys[player1.controls[2]]:  # a - left
            player1.rect.x = max(0, player1.rect.x - player1.speed)
        if keys[player1.controls[3]]:  # d - right
            player1.rect.x = min(WIDTH - player1.rect.width, player1.rect.x + player1.speed)

        # Player 2 movement
        if keys[player2.controls[0]]:  # up - up
            player2.rect.y = max(0, player2.rect.y - player2.speed)
        if keys[player2.controls[1]]:  # down - down
            player2.rect.y = min(HEIGHT - player2.rect.height, player2.rect.y + player2.speed)
        if keys[player2.controls[2]]:  # left - left
            player2.rect.x = max(0, player2.rect.x - player2.speed)
        if keys[player2.controls[3]]:  # right - right
            player2.rect.x = min(WIDTH - player2.rect.width, player2.rect.x + player2.speed)

        ball.update()
        
        if ((ball.rect.x-player1.rect.x)**2+(ball.rect.y-player1.rect.y)**2)**0.5 < 40:
            ball.dx = -abs(ball.dx)
            if player1.rect.y < ball.rect.y and player1.rect.x < ball.rect.x:
                ball.dy = 4
                ball.dx = 4
            elif player1.rect.y < ball.rect.y and player1.rect.x > ball.rect.x:
                ball.dy = 4
                ball.dx = -4
            elif player1.rect.y > ball.rect.y and player1.rect.x < ball.rect.x:
                ball.dy = -4
                ball.dx = 4
            elif player1.rect.y > ball.rect.y and player1.rect.x > ball.rect.x:
                ball.dy = -4
                ball.dx = -4
            else:
                ball.dy = 0
                ball.dx = 4
        
        if ((ball.rect.x-player2.rect.x)**2+(ball.rect.y-player2.rect.y)**2)**0.5 < 40:
            ball.dx = -abs(ball.dx)
            if player2.rect.y < ball.rect.y and player2.rect.x < ball.rect.x:
                ball.dy = 4
                ball.dx = 4
            elif player2.rect.y < ball.rect.y and player2.rect.x > ball.rect.x:
                ball.dy = 4
                ball.dx = -4
            elif player2.rect.y > ball.rect.y and player2.rect.x < ball.rect.x:
                ball.dy = -4
                ball.dx = 4
            elif player2.rect.y > ball.rect.y and player2.rect.x > ball.rect.x:
                ball.dy = -4
                ball.dx = -4
            else:
                ball.dy = 0
                ball.dx = 4

        # Gol para o jogador 2
        if ball.rect.colliderect(goal1):
            goals_p2 += 1
            ball = Ball()
            if goals_p2 >= 3:
                return 2

        # Gol para o jogador 1
        if ball.rect.colliderect(goal2):
            goals_p1 += 1
            ball = Ball()
            if goals_p1 >= 3:
                return 1

        screen.blit(player1.image, player1.rect)
        screen.blit(player2.image, player2.rect)
        screen.blit(ball.image, ball.rect)

        pygame.draw.rect(screen, WHITE, goal1, 2)
        pygame.draw.rect(screen, WHITE, goal2, 2)

        draw_text(f"{goals_p1} x {goals_p2}", font, WHITE, WIDTH//2, 20, screen)
        draw_text(f"Placar Geral: J1 - {player1_score} x J2 - {player2_score}", font, WHITE, WIDTH//2, HEIGHT - 30, screen)

        pygame.display.flip()
        clock.tick(FPS)

    return 0
# ...existing code...
#níveis------------------------------------------------------------------------------------------------------------------------





# Roda o jogo---------------------------------------------------------------------------------------------------------------------
def main():
    global player1_score, player2_score
    
    # Show title screen
    if not title_screen():
        return  # Exit if title screen returns False (user quit)
    
    player1 = Player(100, HEIGHT//2, BLUE, 
                    [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d], 
                    pygame.K_SPACE)
    
    player2 = Player(WIDTH-130, HEIGHT//2, RED,
                    [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
                    pygame.K_RETURN)
    
    player1_score = 0
    player2_score = 0
    
    levels = [level_1, level_2, level_3, level_4, level_5]
    
    for level in levels:
        player1.lives = 3
        player2.lives = 3
        player1.bullets.empty()
        player2.bullets.empty()
        
        result = level(player1, player2)
        
        if result == 1:
            player1_score += 1
        elif result == 2:
            player2_score += 1
        
        pygame.time.delay(1000)
    
    final_winner = 1 if player1_score > player2_score else 2 if player2_score > player1_score else 0
    show_game_over(final_winner)
    pygame.quit()

if __name__ == "__main__":
    main()