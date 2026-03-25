import pygame
import sys
import time
import os
import math 

pygame.init()

# Screen
width, height = 800, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Little Guardian - Version 1")

# ================= GRENADE CLASS =================
class Grenade:
    def __init__(self, x, y, direction): 
        self.rect = pygame.Rect(x, y, 25, 25)
        self.vel_x = 7 * direction 
        self.vel_y = -10
        self.gravity = 0.5
        self.exploding = False
        self.explosion_time = 0

    def update(self):
        if not self.exploding:
            self.vel_y += self.gravity
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

# ================= PIXEL FONTS (RETRO) =================
title_font = pygame.font.SysFont("consolas", 32, bold=True)
menu_font   = pygame.font.SysFont("consolas", 22, bold=True)
small_font    = pygame.font.SysFont("consolas", 16)

# ================= IMAGES =================
def resource_path(rel_path):
    try:
        base_path = sys._MEIPASS 
    except Exception:
        base_path = os.path.abspath("..")
    return os.path.join(base_path, rel_path)

def load_img(name, size):
    try:
        path = resource_path(os.path.join("assets", name))
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((200, 0, 0))
        return surf
        
cover_img = load_img("capa1.png", (800, 400))
background = load_img("fundo.png", (800, 400))
player_img = load_img("player.png", (60, 60))
player_jump_img = load_img("player_pu.png", (60, 60))
player_crouch_img = load_img("player_ag.png", (60, 60))
player_grenade_img = load_img("player_pu_granada.png", (60, 60))
enemy_img = load_img("inimigo.png", (90, 90))
enemy_bullet_img = load_img("mag_1.png", (25, 25))
player_bullet_img = load_img("mag_p_1.png", (30, 30))
grenade_img = load_img("grana_1.png", (25, 25))
grenade_damage_img = load_img("dano_granada.png", (50, 50))
laser_img = load_img("lay_1.png", (800, 320))
life_img = load_img("v_1.png", (25, 25))
life_lost_img = load_img("v_-1.png", (25, 25))
ray_img = load_img("raio-.png", (40, 40))
stone_img = load_img("pedra.png", (80, 60))

# ================= GROUND =================
ground_map = []
for x in range(800):
    if x < 130: y = 380
    elif x < 160: y = 411 + (x - 179) * 0.8
    elif x < 240: y = 390
    elif x < 289: y = 423 - (x - 188) * 0.63
    elif x < 390: y = 355
    elif x < 423: y = 275 + (x - 181) * 0.4
    elif x < 669: y = 376
    elif x < 779: y = 388
    else: y = 405 - (x - 770) * 1.2
    ground_map.append(int(y))

# ================= GAME STATES =================
STATE_COVER = -1
STATE_MENU = 0
STATE_TUTORIAL = 1
STATE_PLAYING = 2
STATE_PAUSE = 3
STATE_END = 4 

state = STATE_COVER
cover_start_time = time.time()
result_text = "" 

# ================= MENU =================
selected_option = 0
main_menu = ["PLAY", "TUTORIAL", "EXIT"]
pause_menu = ["RESUME", "EXIT"]
end_menu = ["PLAY AGAIN", "BACK TO MENU"] 

# ================= PLAYER =================
player = pygame.Rect(100, 100, 60, 60)
speed = 5
vel_y = 0
gravity = 0.6
on_ground = False
lives = 5
hits = 0
damage_time = 0
FOOT_OFFSET = 2
jumps = 0
MAX_JUMPS = 2
grenades_stock = 5
grenade_list = []
throwing_grenade = False
grenade_sprite_time = 0
facing_right = True
current_platform = None
ray_uses = 0
MAX_RAY_USES = 3
ray_damage_accumulated = 0
ray_active = False
ray_start_time = 0 

# ================= MOVING PLATFORM =================
class MovingPlatform:
    def __init__(self, x, y, width, height, left_limit, right_limit):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel_x = 2
        self.left_limit = left_limit
        self.right_limit = right_limit

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.right >= self.right_limit or self.rect.left <= self.left_limit:
            self.vel_x *= -1

# Create the moving platform (stone) in the middle of the map
stone_platform = MovingPlatform(width//2 - 75, 200, 150, 40, 150, 650)

# ================= LASER =================
charging_laser = False
laser_start_time = 0
laser_ready = False
laser_active = False
laser_time = 0
weapon_offset_x = 52
weapon_offset_y = 32
laser_damage_given = False 

# ================= ENEMY =================
enemy = pygame.Rect(600, 215, 90, 90)
enemy_lives = 5
enemy_hits = 0
enemy_vel_x = 1.5
enemy_direction = 1
enemy_state = "NORMAL" 
enemy_state_change_time = time.time()
already_dealt_charge_damage = False

# ================= BULLETS =================
player_bullets = [] 
enemy_bullets = [] 
last_player_shot = 0
last_enemy_shot = time.time()

clock = pygame.time.Clock()

def draw_centered_text(text, font, color, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (width//2 - surf.get_width()//2, y))

def show_menu(options, selected, background_img=None, title=None):
    if background_img:
        screen.blit(background_img, (0, 0))
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill((0,0,0))
    
    if title:
        draw_centered_text(title, title_font, (255, 255, 255), 100)

    for i, option in enumerate(options):
        color = (255, 255, 0) if i == selected else (255, 255, 255)
        arrow = "> " if i == selected else "  "
        text = menu_font.render(arrow + option, True, color)
        screen.blit(text, (width//2 - text.get_width()//2, 200 + i*50))

def show_tutorial():
    screen.fill((0,0,0))
    draw_centered_text("TUTORIAL - CONTROLS", title_font, (200, 255, 200), 40)
    instructions = [
        "UP ARROW ................. Jump",
        "DOWN ARROW ............... Crouch",
        "RIGHT / LEFT ARROW ...... Move right/left",
        "SPACE .................... Shoot",
        "HOLD 0 (1 sec) ........... MEGA LASER (Removes 1 life)",
        "JUMP + SPACE ............. Throw GRENADE (if available)",
        "KEY 9 .................... SUPER RAY (5s 10x faster shots)",
        "PLATFORM ................. Jump on the stone to escape",
        "",
        "Press ENTER or ESC to return"
    ]
    for i, line in enumerate(instructions):
        color = (220, 220, 255) if i < 8 else (180, 180, 180)
        text = small_font.render(line, True, color)
        screen.blit(text, (width//2 - text.get_width()//2, 110 + i*30))

def reset_game():
    global lives, enemy_lives, hits, enemy_hits, grenades_stock, grenade_list
    global player_bullets, enemy_bullets, player, enemy, laser_active, laser_damage_given
    global ray_damage_accumulated, ray_active, ray_start_time, enemy_state, enemy_state_change_time
    global current_platform, stone_platform, ray_uses
    lives, enemy_lives = 5, 5
    hits = enemy_hits = 0
    grenades_stock = 5
    grenade_list.clear()
    player_bullets.clear()
    enemy_bullets.clear()
    player.x, player.y = 100, 100
    enemy.x = 600
    laser_active = False
    laser_damage_given = False
    ray_damage_accumulated = 0
    ray_active = False
    ray_start_time = 0
    ray_uses = 0 
    enemy_state = "NORMAL"
    enemy_state_change_time = time.time()
    current_platform = None
    stone_platform.rect.x = width//2 - 75 

# ================= MAIN LOOP =================
while True:
    current_time = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if state == STATE_COVER:
                state = STATE_MENU
            elif state == STATE_TUTORIAL:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    state = STATE_MENU
            elif state in (STATE_MENU, STATE_PAUSE, STATE_END):
                current_menu = main_menu if state == STATE_MENU else (pause_menu if state == STATE_PAUSE else end_menu)
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(current_menu)
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(current_menu)
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    choice = current_menu[selected_option]
                    if choice in ("PLAY", "RESUME", "PLAY AGAIN"):
                        reset_game()
                        state = STATE_PLAYING
                        selected_option = 0
                    elif choice == "TUTORIAL":
                        state = STATE_TUTORIAL
                    elif choice == "BACK TO MENU":
                        state = STATE_MENU
                        selected_option = 0
                    elif choice == "EXIT":
                        pygame.quit()
                        sys.exit()

            elif state == STATE_PLAYING:
                if event.key == pygame.K_p:
                    state = STATE_PAUSE
                    selected_option = 0
                if event.key == pygame.K_UP and jumps < MAX_JUMPS:
                    vel_y = -12
                    jumps += 1
                    current_platform = None 
                if event.key == pygame.K_0:
                    charging_laser = True
                    laser_start_time = time.time()
                
                if (event.key == pygame.K_9 
                    and ray_damage_accumulated >= 60 
                    and not ray_active 
                    and ray_uses < MAX_RAY_USES):
                    ray_active = True
                    ray_start_time = current_time
                    ray_damage_accumulated = 0
                    ray_uses += 1
        if event.type == pygame.KEYUP:
            if state == STATE_PLAYING and event.key == pygame.K_0:
                charging_laser = False
                if laser_ready:
                    laser_active = True
                    laser_damage_given = False 
                    laser_time = time.time()
                    laser_ready = False
    if state == STATE_COVER:
        screen.blit(cover_img, (0, 0))
        if current_time - cover_start_time > 4:
            state = STATE_MENU
    elif state == STATE_MENU:
        show_menu(main_menu, selected_option, background_img=cover_img)

    elif state == STATE_TUTORIAL:
        show_tutorial()

    elif state == STATE_PAUSE:
        show_menu(pause_menu, selected_option, background_img=background)

    elif state == STATE_END:
        show_menu(end_menu, selected_option, background_img=background, title=result_text)

    elif state == STATE_PLAYING:
        screen.blit(background, (0, 0))
        
        if enemy_lives <= 0 or lives <= 0:
            result_text = "YOU WIN!" if enemy_lives <= 0 else "YOU LOSE!"
            state = STATE_END
            selected_option = 0
            continue

        if ray_active:
            if current_time - ray_start_time > 5:
                ray_active = False
            shot_delay = 0.05
            bullet_size = 50
            bullet_speed = 15
        else:
            shot_delay = 0.4
            bullet_size = 30
            bullet_speed = 10

        stone_platform.update()
        screen.blit(stone_img, stone_platform.rect)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= speed
            facing_right = False
        if keys[pygame.K_RIGHT]:
            player.x += speed
            facing_right = True
        vel_y += gravity
        player.y += vel_y
        on_ground = False
        pos_x = int(player.centerx)
        ground_height = ground_map[max(0, min(799, pos_x))]
        if player.bottom >= ground_height:
            player.bottom = ground_height + FOOT_OFFSET
            vel_y, on_ground, jumps = 0, True, 0
            current_platform = None
        if vel_y >= 0 and current_platform is None: 
            if player.colliderect(stone_platform.rect):
                if player.bottom <= stone_platform.rect.top + 15:
                    current_platform = stone_platform
                    vel_y, on_ground, jumps = 0, True, 0
                    player.bottom = stone_platform.rect.top + FOOT_OFFSET
        if current_platform:
            player.x += current_platform.vel_x
            player.bottom = current_platform.rect.top + FOOT_OFFSET
            # If walking off the platform, fall
            if not player.colliderect(stone_platform.rect):
                current_platform = None
        player.x = max(0, min(width - player.width, player.x))

        # ENEMY LOGIC 
        if enemy_state == "NORMAL":
            enemy.x += enemy_vel_x * enemy_direction
            if enemy.right >= width or enemy.left <= 0:
                enemy_direction *= -1
            if current_time - last_enemy_shot > 0.8:
                dx = player.centerx - enemy.centerx
                dy = player.centery - enemy.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    vx = (dx / dist) * 7
                    vy = (dy / dist) * 7
                    enemy_bullets.append({'rect': pygame.Rect(enemy.x, enemy.y + 40, 25, 25), 'vx': vx, 'vy': vy})
                last_enemy_shot = current_time
            if current_time - enemy_state_change_time > 7:
                enemy_state = "CHARGE"
                enemy_state_change_time = current_time
                already_dealt_charge_damage = False

        elif enemy_state == "CHARGE":
            if enemy.centerx < player.centerx:
                enemy.x += 8
            elif enemy.centerx > player.centerx:
                enemy.x -= 8
            
            if enemy.colliderect(player) and not already_dealt_charge_damage:
                if not current_platform:
                    lives -= 1
                    damage_time = current_time
                    already_dealt_charge_damage = True
            
            if current_time - enemy_state_change_time > 3:
                enemy_state = "NORMAL"
                enemy_state_change_time = current_time

        enemy.bottom = ground_map[max(0, min(799, int(enemy.centerx)))]

        # --- PLAYER SHOTS AND ABILITIES ---
        if keys[pygame.K_SPACE] and current_time - last_player_shot > shot_delay:
            direction = 1 if facing_right else -1
            if not on_ground and grenades_stock > 0:
                spawn_x = player.x + weapon_offset_x if facing_right else player.x
                grenade_list.append(Grenade(spawn_x, player.y, direction))
                grenades_stock -= 1
                throwing_grenade = True
                grenade_sprite_time = current_time
            else:
                spawn_x = player.x + weapon_offset_x if facing_right else player.x
                player_bullets.append({'rect': pygame.Rect(spawn_x, player.y + weapon_offset_y - 15, bullet_size, bullet_size), 'dir': direction})
            last_player_shot = current_time

        for g in grenade_list[:]:
            g.update()
            if not g.exploding:
                if g.rect.colliderect(enemy):
                    g.exploding, g.explosion_time = True, current_time
                    enemy_hits += 2
                    ray_damage_accumulated += 2
                    if enemy_hits >= 25: enemy_lives -= 1; enemy_hits = 0
                elif g.rect.y > 400 or g.rect.x > 800 or g.rect.x < 0: grenade_list.remove(g)
            elif current_time - g.explosion_time > 0.3: grenade_list.remove(g)

        if charging_laser and current_time - laser_start_time >= 1: laser_ready = True
        if laser_active and current_time - laser_time > 0.8: laser_active = False

        # Render Player
        if throwing_grenade and current_time - grenade_sprite_time < 0.3: img = player_grenade_img
        elif keys[pygame.K_DOWN]: img = player_crouch_img
        elif not on_ground: img = player_jump_img
        else: img = player_img

        if throwing_grenade and current_time - grenade_sprite_time >= 0.3: throwing_grenade = False
        if current_time - damage_time < 0.5: img = pygame.transform.grayscale(img)

        img = pygame.transform.flip(img, not facing_right, False)
        screen.blit(img, player)
        
        # Render Enemy
        screen.blit(enemy_img, enemy)

        # MEGA LASER
        if laser_active:
            lx = player.x + weapon_offset_x if facing_right else player.x - 800
            ly = player.y + weapon_offset_y - 160
            final_laser_img = pygame.transform.flip(laser_img, not facing_right, False)
            screen.blit(final_laser_img, (lx, ly))
            laser_rect = pygame.Rect(lx, ly, 800, 320)
            if laser_rect.colliderect(enemy) and not laser_damage_given:
                enemy_lives -= 1
                enemy_hits = 0
                ray_damage_accumulated += 25
                laser_damage_given = True

        # PLAYER BULLETS
        for bullet in player_bullets[:]:
            bullet['rect'].x += bullet_speed * bullet['dir']
            bullet_img_scaled = pygame.transform.scale(player_bullet_img, (bullet_size, bullet_size))
            screen.blit(bullet_img_scaled, bullet['rect'])
            
            if bullet['rect'].colliderect(enemy):
                enemy_hits += 1
                ray_damage_accumulated += 1
                if bullet in player_bullets: player_bullets.remove(bullet)
                if enemy_hits >= 25: enemy_lives -= 1; enemy_hits = 0
            elif bullet['rect'].x > width or bullet['rect'].x < 0:
                if bullet in player_bullets: player_bullets.remove(bullet)

        for g in grenade_list:
            screen.blit(grenade_damage_img if g.exploding else grenade_img, g.rect)

        for bullet_data in enemy_bullets[:]:
            bullet_rect = bullet_data['rect']
            bullet_rect.x += bullet_data['vx']
            bullet_rect.y += bullet_data['vy']
            screen.blit(enemy_bullet_img, bullet_rect)
            
            if bullet_rect.colliderect(player):
                hits += 1
                enemy_bullets.remove(bullet_data)
                if hits >= 15: lives -= 1; hits = 0; damage_time = current_time
            elif bullet_rect.x < -50 or bullet_rect.x > width + 50 or bullet_rect.y < -50 or bullet_rect.y > height + 50:
                if bullet_data in enemy_bullets: enemy_bullets.remove(bullet_data)

        # HUD
        for i in range(5):
            screen.blit(life_img if i < lives else life_lost_img, (10 + i*30, 10))
            screen.blit(life_img if i < enemy_lives else life_lost_img, (650 + i*30, 10))
            if i < grenades_stock: screen.blit(grenade_img, (10 + i*30, 40))
        
        if ray_damage_accumulated >= 60 or ray_active:
            screen.blit(ray_img, (160, 10))
            if ray_active:
                time_left = max(0, int(5 - (current_time - ray_start_time)))
                ray_text = small_font.render(f"{time_left}s (Uses:{ray_uses}/{MAX_RAY_USES})", True, (255,255,0))
                screen.blit(ray_text, (205, 20))

    pygame.display.update()
    clock.tick(60)