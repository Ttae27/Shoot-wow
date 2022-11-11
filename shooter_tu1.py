import os
from random import randint
import pygame
import csv
import button
from pathlib import Path

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("shoot wow")
icon_img = pygame.image.load('img\Approve_icon.svg.png').convert_alpha()
pygame.display.set_icon(icon_img)

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 2
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
page = "menu"
score = 0
score_tmp = 0
highscore_file = 'highscore.csv'

# define player action
moving_left = False
moving_right = False
shoot = False

#load images
# button images
start_img = pygame.image.load('img/play.png').convert_alpha()
start_img = pygame.transform.scale(start_img, (start_img.get_width() // 2, start_img.get_height() // 2))
score_img = pygame.image.load('img/prize.png').convert_alpha()
score_img = pygame.transform.scale(score_img, (score_img.get_width() // 2, score_img.get_height() // 2))
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
restart_img = pygame.transform.scale(restart_img, (restart_img.get_width() // 3, restart_img.get_height() // 3))
back_img = pygame.image.load('img/prew.png').convert_alpha()
back_img = pygame.transform.scale(back_img, (back_img.get_width() // 2, back_img.get_height() // 2))
# back ground
back_1 = pygame.image.load('LevelEditor/background/plx-1.png').convert_alpha()
back_1 = pygame.transform.scale(back_1, (int(back_1.get_width() * 2.9), int(back_1.get_height() * 2.9)))
back_2 = pygame.image.load('LevelEditor/background/plx-2.png').convert_alpha()
back_2 = pygame.transform.scale(back_2, (int(back_2.get_width() * 2.9), int(back_2.get_height() * 2.9)))
back_3 = pygame.image.load('LevelEditor/background/plx-3.png').convert_alpha()
back_3 = pygame.transform.scale(back_3, (int(back_3.get_width() * 2.9), int(back_3.get_height() * 3.2)))
back_4 = pygame.image.load('LevelEditor/background/plx-4.png').convert_alpha()
back_4 = pygame.transform.scale(back_4, (int(back_4.get_width() * 2.9), int(back_4.get_height() * 3)))
back_5 = pygame.image.load('LevelEditor/background/plx-5.png').convert_alpha()
back_5 = pygame.transform.scale(back_5, (int(back_5.get_width() * 2.9), int(back_5.get_height() * 3)))
# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/tile/{x}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

leaderBoard = []
if Path(highscore_file).is_file() == False:
    tmp_list1 = ['xxx', 0]
    tmp_list2 = ['xxx', 0]
    tmp_list3 = ['xxx', 0]
    tmp_list4 = ['xxx', 0]
    tmp_list5 = ['xxx', 0]
    leaderBoard.append(tmp_list1)
    leaderBoard.append(tmp_list2)
    leaderBoard.append(tmp_list3)
    leaderBoard.append(tmp_list4)
    leaderBoard.append(tmp_list5)
    with open("highscore.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for x in range(5):
            writer.writerow(leaderBoard[x])
else:
    with open("highscore.csv", 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x in reader:
            leaderBoard.append(x)

# bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()

# pick up boxes
heal_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
item_boxes = {
    'Health'    : heal_box_img,
    'Ammo'      : ammo_box_img
}

# define colors
BG = (144, 201, 120)

# define font
font = pygame.font.Font("img/font/monogram.ttf", 50)
font_in_game = pygame.font.Font("img/font/monogram.ttf", 35)
font_extend = pygame.font.Font("img/font/monogram-extended.ttf", 85)
font_name_game = pygame.font.Font("img/font/HACKED.ttf", 200)


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def draw_bg():
    width = back_1.get_width()
    for x in range(6):
        screen.blit(back_1, (x * width - bg_scroll * 0.4, 0))
        screen.blit(back_2, (x * width - bg_scroll * 0.5, 0))
        screen.blit(back_3, (x * width - bg_scroll * 0.6, 0))
        screen.blit(back_4, (x * width - bg_scroll * 0.7, 0))
        screen.blit(back_5, (x * width - bg_scroll * 0.8, 0))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    lava_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, health):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = health
        self.max_health = self.health
        self.ammo = ammo
        self.start_ammo = ammo
        self.direction = 1
        self.jump = False
        self.vel_y = 0
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 
        self.score = 0
        self.update_time = pygame.time.get_ticks()
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        self.stop_score = 0

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temp list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()    
        self.height = self.image.get_height()  

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
                
    def move(self, moving_left, moving_right):
        # reset movemont variables
        dx = 0
        dy = 0

        screen_scroll = 0

        # assign movement variables if moving
        if moving_left:
            dx = -self.speed
            self.direction = -1
            self.flip = True
        if moving_right:
            dx = self.speed
            self.direction = 1
            self.flip = False
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        dy = self.vel_y
        
        # check for collision
        for tile in world.obstacle_list:
            # check in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # check in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with lava
        if pygame.sprite.spritecollide(self, lava_group, False):
            self.health = 0
        # check for collision for score
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True
        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == "player":
            if self.rect.left + dx <= 0 or self.rect.right + dx >= SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < world.map_len * TILE_SIZE - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20            
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery - 5, self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and randint(1, 100) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            # check if the ai near player
            if self.vision.colliderect(player.rect):
                # stop running
                self.update_action(0)
                # shoot player
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1                    
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100

        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            if self.char_type == "player":
                if self.frame_index < len(self.animation_list[self.action]) - 1:
                    self.frame_index += 1
                else:
                    if self.action != 3:
                        self.frame_index = 0
            if self.char_type == "enemy":
                if self.frame_index < len(self.animation_list[self.action]) - 1:
                    self.frame_index += 1
                else:
                    if self.action != 3:
                        self.frame_index = 0
                        self.stop_score = 0
                    if self.action == 3:
                        self.stop_score = 1
                    rand = randint(1, 5)
                    if self.alive == False and rand == 1:
                        item_box = ItemBox("Ammo", self.rect.x, self.rect.y)
                        item_box_group.add(item_box)
                        self.kill()
                
                    elif self.alive == False and rand == 2:
                        item_box = ItemBox("Health", self.rect.x, self.rect.y)
                        item_box_group.add(item_box)
                        self.kill()
                    


    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            if self.action == 3 and self.char_type != 'player':
                player.score += 50
            self.update_time = pygame.time.get_ticks()
            

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

            

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.map_len = len(data[0])
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 13:
                        self.obstacle_list.append(tile_data)
                    elif tile == 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 2, 3, 20, 100)
                        health_bar = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.5, 2, 20, 100)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        lava = Lava(img, x * TILE_SIZE, y * TILE_SIZE)
                        lava_group.add(lava)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Lava(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            #delete the item box
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health

        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, "white", (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, "RED", (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, "GREEN", (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.direction = direction
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed)  + screen_scroll
        # check if the bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 50
                    self.kill()

# create buttons
start_button = button.Button(SCREEN_WIDTH - 180, SCREEN_HEIGHT // 2 - 150, start_img, 1)
score_button = button.Button(SCREEN_WIDTH - 180, SCREEN_HEIGHT // 2 + 50, score_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 50, restart_img, 1)
back_button = button.Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 200, back_img, 1)

# create sprite groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f"LevelEditor/level{level}_data.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

def inpt():
    word=""
    draw_text("Please enter your name: ",font, "red", 50,400) 
    pygame.display.flip()
    done = True
    while done:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key <= 127 and event.key != pygame.K_BACKSPACE:
                    word += str(chr(event.key))
                if event.key == pygame.K_BACKSPACE:
                    word = word.strip(word[len(word) - 1])
                    pygame.display.flip()
                if event.key == pygame.K_RETURN:
                    done=False
            draw_text(word , font, "blue", 500, 400)
            pygame.display.flip()
    word = word.strip('\r')
    return word

run = True
# page = "get_score"
while run:

    clock.tick(FPS)
    if start_game == False and page == "menu":
        # draw menu
        draw_bg()
        draw_text("SHOOT", font_name_game, "white", 70, 120)
        draw_text("WOW", font_name_game, "white", 70, 320)
        # add buttons
        if start_button.draw(screen):
            start_game = True
        if score_button.draw(screen):
            page = "score"

    elif start_game == False and page == "score":
        draw_bg()
        draw_text("LEADERBOARD", font_extend, "white", SCREEN_WIDTH // 2 - 150, 50)
        with open("highscore.csv", 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, x1 in enumerate(reader):
                for y, y1 in enumerate(x1):
                    draw_text(f"{y1}", font, "white", 200 + (y * 370), 150 + (x * 80))
        if back_button.draw(screen):
            page = "menu"

    elif start_game == False and page == "get_score":
        draw_bg()
        draw_text(f"Your Score: {score}", font, "RED", 100, 100)
        name = []
        text = inpt()
        name.append(text)
        name.append(score)
        leaderBoard.append(name)
        for x in range(5):
            if score > int(leaderBoard[x][1]):
                tmp = 1
                leaderBoard.remove(leaderBoard[4])
                while 4 - tmp >= x:
                    leaderBoard[4 - tmp + 1] = leaderBoard[4 - tmp]
                    tmp += 1
                leaderBoard[x] = name
                break

        with open("highscore.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for x in range(5):
                writer.writerow(leaderBoard[x])
        page = "menu"
        score = 0
        player.score = 0
        score_tmp = 0
    else:
        # update background
        draw_bg()
        world.draw()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        # update and draw group
        bullet_group.update()
        item_box_group.update()
        decoration_group.update()
        player.update()
        lava_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        # show health
        health_bar.draw(player.health)
        # show ammo
        draw_text(f'AMMO: {player.ammo}', font_in_game, 'WHITE', 10, 35)
        score = score_tmp + player.score
        draw_text(f'SCORE: {score}', font_in_game, 'WHITE', SCREEN_WIDTH - 150, 10)
        # update player action
        if player.alive:
            if shoot:
                player.shoot()
            if player.in_air:
                player.update_action(2) # 2 = jump
            elif moving_left or moving_right:
                player.update_action(1) # 1 = run
            else:
                player.update_action(0) # 0 = idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # check if player has completed the level
            if level_complete:
                tmp_health = player.health
                tmp_ammo = player.ammo
                level += 1    
                bg_scroll = 0
                score_tmp += player.score
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # load in level data and create world
                    with open(f"LevelEditor/level{level}_data.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                    player.health = tmp_health
                    player.ammo = tmp_ammo
                if level > MAX_LEVELS:
                    page = 'get_score'
                    level = 1
                    start_game = False
                    bg_scroll = 0
                    world_data = reset_level()
                    if level <= MAX_LEVELS:
                        # load in level data and create world
                        with open(f"LevelEditor/level{level}_data.csv", newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            page = 'get_score'
            start_game = False
            level = 1
            world_data = reset_level()
            if level <= MAX_LEVELS:
                # load in level data and create world
                with open(f"LevelEditor/level{level}_data.csv", newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_j:
                shoot = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False 
            if event.key == pygame.K_j:
                shoot = False

    pygame.display.update()

pygame.quit()