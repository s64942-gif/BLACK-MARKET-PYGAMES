# Version: Final Beta Version (1.0.18 - XP Loop Fix and Stabilization)

import pygame, random, math, sys

 

pygame.init()

WIDTH, HEIGHT = 900, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Veggie Vengeance")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 20)

BIGFONT = pygame.font.SysFont("arial", 36)

MONO_FONT = pygame.font.SysFont("couriernew", 16) # For shop details

 

# --- Colors (Expanded for Shading/Texture) ---

WHITE=(255,255,255); GRAY=(60,60,60); DARK_BG=(24,24,28)

GREEN=(40,180,90); STEM_GREEN=(0,120,0); LEAF_DARK=(0,80,0)

GREEN_DARK=(24,140,70); GREEN_LIGHT=(100,210,140)

RED=(220,60,60); TOMATO_SHADE=(180,50,50)

BROWN=(139,69,19); POTATO_LIGHT=(170,110,60); DARK_BROWN=(80,40,10)

LIGHT_GREEN=(120,200,120); SPROUT_SHADE=(90,180,90)

YELLOW=(240,200,70); ORANGE=(255,165,0); PALE=(200,200,255); BLUE_PALE=(180,200,255)

CHILI_RED=(255,80,80); CHILI_HIGHLIGHT=(255,120,120)

CARROT_ORANGE=(255,140,0); CARROT_SHADE=(200,100,0)

BEAN_GREEN=(80,200,120); BEAN_POD=(70,180,110); BEAN_DARK=(50,150,90)

FOOD_ORANGE=(255,140,80); FOOD_LEAF=(60,170,90)

UI_ACCENT=(90,90,140)

COIN_COLOR=(255,215,0) # Gold

AVOCADO_GREEN=(70,140,70); AVOCADO_BROWN=(100,70,40); AVOCADO_LIME=(150,200,100)

 

# Game states

STATE_MENU = "menu"

STATE_PLAY = "play"

STATE_SHOP = "shop"

STATE_ACH = "achievements"

game_state = STATE_MENU

 

def clamp(x,a,b): return max(a,min(b,x))

def vec_from_angle(deg,length):

    rad=math.radians(deg); return math.cos(rad)*length, math.sin(rad)*length

 

# Sprite groups (initialized in reset_game)

all_sprites=None

enemies=None

bullets=None

enemy_bullets=None

orbs=None

globs=None

foods=None

explosions=None # NEW group for visual AoE

 

# --- Global Shop Scroll Variables ---

SHOP_CONTENT_AREA = pygame.Rect(50, 100, WIDTH - 100, HEIGHT - 180)

SHOP_SCROLL_OFFSET = 0

SHOP_CONTENT_HEIGHT = 0

SHOP_MAX_SCROLL = 0

SHOP_DRAG_START_Y = None

SHOP_SCROLL_START = 0

 

 

# ---------------- Bullet base ----------------

class Bullet(pygame.sprite.Sprite):

    def __init__(self,x,y,angle_deg,speed,damage,color=WHITE,pierce=0,range_limit=None,slow=0.0,slow_duration=0,knockback=0.0,surf=None):

        super().__init__()

        # Use custom surface if provided

        self.original_image=surf if surf is not None else self.create_default_image(color)

        self.image=pygame.transform.rotate(self.original_image, -angle_deg)

        self.rect=self.image.get_rect(center=(x,y))

        self.angle_deg=angle_deg

        self.vx,self.vy=vec_from_angle(angle_deg,speed)

        self.damage=damage

        self.pierce=pierce

        self.range_limit=range_limit; self.travel=0

        self.slow=slow; self.slow_duration=slow_duration

        self.knockback=knockback

 

    def create_default_image(self,color):

        # Simple fallback for safety, though all weapons now have custom surfaces

        surf=pygame.Surface((10,10),pygame.SRCALPHA)

        pygame.draw.circle(surf,color,(5,5),5)

        return surf

   

    def hit_enemy(self, enemy):

        """Placeholder for special effects on hit (prevents AttributeError)."""

        pass

 

    def update(self):

        # Update position

        self.rect.x+=int(self.vx); self.rect.y+=int(self.vy)

        self.travel+=abs(self.vx)+abs(self.vy)

 

        # Rotate the image for directional movement if the projectile has a defined direction/shape

        center = self.rect.center

        self.image = pygame.transform.rotate(self.original_image, -self.angle_deg)

        self.rect = self.image.get_rect(center=center)

 

        # Check range and boundaries

        if self.rect.right<0 or self.rect.left>WIDTH or self.rect.bottom<0 or self.rect.top>HEIGHT: self.kill()

        if self.range_limit and self.travel>=self.range_limit: self.kill()

 

# --- Special Bullet Types ---

class DoTBomb(Bullet):

    """Bullet that applies a damage-over-time effect (used for Hot Sauce)."""

    def __init__(self,x,y,angle_deg,speed,damage,color,pierce=0,range_limit=None,surf=None, dot_damage=1.0, dot_duration=60):

        super().__init__(x,y,angle_deg,speed,damage,color,pierce,range_limit,surf=surf)

        self.dot_damage=dot_damage

        self.dot_duration=dot_duration

        self.max_travel = 100 + random.randint(0,20) # Short range

 

    def update(self):

        super().update()

        if self.travel > self.max_travel:

            self.kill() # Self-destruct after short travel

       

    def hit_enemy(self, enemy):

        """Called when this projectile hits an enemy."""

        # Only apply the burn if it's stronger or the enemy isn't currently burning

        if enemy.burn_timer == 0 or self.dot_damage > enemy.burn_damage:

            enemy.burn_damage = self.dot_damage

            enemy.burn_timer = self.dot_duration

 

class AvocadoGrenade(Bullet):

    """Slow-moving projectile that explodes on impact or range limit."""

    def __init__(self, x, y, angle_deg, stars=1):

        # Stats based on stars

        self.stars = stars

        speed = 4

        damage = 1.0 + 0.5 * (stars - 1)

        range_limit = 200 + 30 * (stars - 1)

       

        # Draw Avocado

        size = 18

        avocado_surf = pygame.Surface((size, size), pygame.SRCALPHA)

        pygame.draw.circle(avocado_surf, AVOCADO_GREEN, (size//2, size//2), size//2 - 1)

        pygame.draw.circle(avocado_surf, AVOCADO_LIME, (size//2, size//2), size//2 - 4)

        pygame.draw.circle(avocado_surf, AVOCADO_BROWN, (size//2, size//2), 3) # Pit

       

        super().__init__(x, y, angle_deg, speed, damage, AVOCADO_GREEN, pierce=0, range_limit=range_limit, surf=avocado_surf)

 

    def explode(self):

        # Calculate explosion radius and effects based on stars

        radius = 50 + 10 * self.stars

        damage = self.damage * 2.0

        slow_factor = 0.5 + 0.1 * self.stars

       

        # Create the explosion visualization

        exp = Explosion(self.rect.centerx, self.rect.centery, radius)

        explosions.add(exp); all_sprites.add(exp)

       

        # Apply effects to enemies in radius

        explosion_rect = pygame.Rect(0, 0, radius*2, radius*2)

        explosion_rect.center = self.rect.center

       

        for e in pygame.sprite.spritecollide(exp, enemies, False):

            # Distance based falloff (simple)

            dist = math.hypot(e.rect.centerx - self.rect.centerx, e.rect.centery - self.rect.centery)

            if dist < radius:

                # Apply damage

                e.health -= damage * (1 - dist / radius * 0.5) # Max damage at center

                # Apply high slow effect

                e.apply_slow(slow_factor, 45)

                # Apply knockback away from the center

                dx = e.rect.centerx - self.rect.centerx

                dy = e.rect.centery - self.rect.centery

                dist_norm = max(1.0, math.hypot(dx, dy))

                e.apply_knockback(dx/dist_norm, dy/dist_norm, 4.0)

       

        self.kill() # Destroy grenade after explosion

 

    def update(self):

        super().update()

        # Explode on range limit hit

        if self.range_limit and self.travel >= self.range_limit:

            self.explode()

 

# ---------------- Visual Explosion (No collision, short lived) ----------------

class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y, radius):

        super().__init__()

        self.radius = radius

        self.max_radius = radius

        self.life = 12 # frames

        self.frame = 0

        size = radius * 2

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        self.rect = self.image.get_rect(center=(x, y))

       

    def update(self):

        self.frame += 1

        if self.frame > self.life:

            self.kill()

            return

 

        # Visual update: pulsing fade effect

        fade_ratio = self.frame / self.life

        current_radius = int(self.max_radius * (1 - fade_ratio * 0.2)) # Slightly shrinks

        alpha = int(255 * (1 - fade_ratio)) # Fades out

       

        self.image.fill((0, 0, 0, 0)) # Clear surface

       

        # Draw the explosion ring/cloud

        color = (255, 165, 0, alpha) # Orange/Yellow color

        pygame.draw.circle(self.image, color, (self.max_radius, self.max_radius), current_radius, width=2)

       

        # Draw a faded inner core

        inner_color = (255, 255, 100, alpha // 3)

        pygame.draw.circle(self.image, inner_color, (self.max_radius, self.max_radius), current_radius // 2)

 

        # Update rect in case the radius change affects the center (though it shouldn't here)

        self.rect = self.image.get_rect(center=self.rect.center)

       

 

# ---------------- Player (Textured Broccoli) ----------------

class Player(pygame.sprite.Sprite):

    # Class-level variables to store persistence

    game_coins = 100

    owned_weapons_persist = set() # Will be initialized correctly in reset_game

 

    def __init__(self):

        super().__init__()

        self.image=self.draw_broccoli()

        self.rect=self.image.get_rect(center=(WIDTH//2,HEIGHT//2))

        self.speed=5

        self.health=10

        self.max_health=10

        self.invuln=0

       

        # Currency and persistence: Load saved data

        self.coins = Player.game_coins # Load saved coins

        # CRITICAL FIX: Load the persistent set of owned weapons (Shop + Starter)

        self.owned_weapons = Player.owned_weapons_persist.copy()

        

        self.level=1

        self.xp=0

        self.xp_to_next=10 # Base XP to next level

 

        # Weapons (Initialized empty in reset_game, filled by start_choice)

        self.weapons=[]

        self.fire_timers={}

        self.weapon_stars={}

        self.aim_angle=-90

       

        # FIX: Initialize run-time weapon data structures for all owned weapons.

        # This prevents crashes when picking any owned weapon as a starter/upgrade.

        for w_name in self.owned_weapons:

            # Check if w_name is a valid weapon name before initializing (safety)

            if w_name in ALL_WEAPONS:

                self.fire_timers[w_name] = 0 # Initialize timer

                # All owned weapons start at level 1 internally for their run data structure

                self.weapon_stars[w_name] = 1

 

 

    def end_run(self):

        # CRITICAL FIX: Save run coins back to the class variable upon exit

        Player.game_coins = self.coins

 

    def draw_broccoli(self):

        surf=pygame.Surface((48,48),pygame.SRCALPHA)

        # Stem (3D effect)

        pygame.draw.rect(surf, STEM_GREEN, (20,18,8,22), border_radius=4)

        pygame.draw.rect(surf, LEAF_DARK, (22,22,4,14), border_radius=2)

       

        # Crown (Shaded/Textured effect)

        pygame.draw.circle(surf, GREEN, (24,16), 16)

        # Highlights

        pygame.draw.circle(surf, GREEN_LIGHT, (17,12), 7)

        pygame.draw.circle(surf, GREEN_LIGHT, (31,12), 6)

        # Shadow/Texture

        pygame.draw.circle(surf, GREEN_DARK, (27,20), 5)

        pygame.draw.circle(surf, LEAF_DARK, (20,20), 4) # Small dark spot

        return surf

 

    def add_weapon(self,name):

        # When a weapon is added via level up/start choice, it is added to the run

        if name not in self.weapons:

            # IMPORTANT: Ensure the weapon is marked as owned (persistent) if it's new to the player

            Player.owned_weapons_persist.add(name)

            self.owned_weapons.add(name) # Also update current run's view

            self.weapons.append(name)

           

            if name not in self.fire_timers: self.fire_timers[name]=0

            if name not in self.weapon_stars: self.weapon_stars[name]=1

        else:

            if self.weapon_stars.get(name, 0) < 5:

                self.weapon_stars[name]=self.weapon_stars.get(name, 0)+1

 

    def update(self,keys):

        dx=(keys[pygame.K_d]-keys[pygame.K_a]); dy=(keys[pygame.K_s]-keys[pygame.K_w])

        self.rect.x+=dx*self.speed; self.rect.y+=dy*self.speed

        self.rect.x=clamp(self.rect.x,0,WIDTH-self.rect.width)

        self.rect.y=clamp(self.rect.y,0,HEIGHT-self.rect.height)

        if self.invuln>0: self.invuln-=1

 

        # auto-aim nearest enemy

        if enemies and len(enemies)>0:

            target=min(enemies,key=lambda e:(e.rect.centerx-self.rect.centerx)**2+(e.rect.centery-self.rect.centery)**2)

            tx=target.rect.centerx-self.rect.centerx; ty=target.rect.centery-self.rect.centery

            self.aim_angle=math.degrees(math.atan2(ty,tx))

 

        # auto-shoot

        for w in list(self.weapons):

            # FIX: Check if the weapon is in fire_timers dictionary before accessing

            if self.fire_timers.get(w, 0)>0: self.fire_timers[w]-=1

            else: self.fire_weapon(w)

 

    def fire_weapon(self,name):

        cx,cy=self.rect.center; angle=self.aim_angle

        stars=self.weapon_stars.get(name,1)

 

        # --- Fork (3D Tine) ---

        if name=="Fork":

            dmg=1.0+0.3*(stars-1)

            cooldown=max(10-(stars-1),5)

            # Draw Fork Tine (Simulated depth)

            tine_surf=pygame.Surface((18,6),pygame.SRCALPHA)

            pygame.draw.polygon(tine_surf,GRAY,[(0,3),(16,1),(16,5)]) # Main shaft

            pygame.draw.rect(tine_surf,WHITE,(14,2,2,2)) # Highlight tip

            b=Bullet(cx,cy,angle,10,dmg,WHITE,pierce=stars,surf=tine_surf)

            bullets.add(b); all_sprites.add(b); self.fire_timers[name]=cooldown

 

        # --- Maple Syrup (Thick Bottle) ---

        elif name=="Maple Syrup":

            cooldown=45-(stars-1)*5

            # Draw Bottle (Syrup dripping/thick)

            bottle_surf=pygame.Surface((18,18),pygame.SRCALPHA)

            pygame.draw.rect(bottle_surf,DARK_BROWN,(7,2,4,4),border_radius=1) # Cap

            pygame.draw.circle(bottle_surf,YELLOW,(9,11),8) # Base

            pygame.draw.circle(bottle_surf,(250,220,100),(9,11),6) # Syrup highlight

            pygame.draw.circle(bottle_surf,(180,150,50),(13,15),3) # Thick drop

            b=MapleBottle(cx,cy,angle,stars,surf=bottle_surf)

            bullets.add(b); all_sprites.add(b); self.fire_timers[name]=max(cooldown,20)

 

        # --- Corn Blaster (Textured Popcorn) ---

        elif name=="Corn Blaster":

            dmg=0.5+0.1*(stars-1)

            cooldown=max(4-(stars-1),1)

            # Draw Popcorn (Irregular shape)

            pop_surf=pygame.Surface((10,10),pygame.SRCALPHA)

            # Outer white body

            pygame.draw.polygon(pop_surf,WHITE,[(0,5),(5,0),(10,5),(5,10)])

            # Yellow kernel center

            pygame.draw.circle(pop_surf,YELLOW,(5,5),3)

            pygame.draw.circle(pop_surf,(255,255,200),(3,3),1) # Highlight

            b=Bullet(cx,cy,angle,12,dmg,YELLOW,surf=pop_surf)

            bullets.add(b); all_sprites.add(b); self.fire_timers[name]=cooldown

 

        # --- Garlic Burst (Detailed Clove) ---

        elif name=="Garlic Burst":

            dmg=1.0+0.2*(stars-1)

            knock=6.0+(stars-1)

            cooldown=max(40-(stars-1)*4,20)

            pellets=8+(stars-1)*2

            # Draw Clove (Layered)

            clove_surf=pygame.Surface((14,14),pygame.SRCALPHA)

            pygame.draw.circle(clove_surf,PALE,(7,7),7)

            pygame.draw.circle(clove_surf,BLUE_PALE,(7,7),5)

            pygame.draw.circle(clove_surf,WHITE,(4,4),2) # Small highlight

            for a in range(0,360,int(360/pellets)):

                b=Bullet(cx,cy,a,8,dmg,PALE,range_limit=100+20*(stars-1),knockback=knock,surf=clove_surf)

                bullets.add(b); all_sprites.add(b)

            self.fire_timers[name]=cooldown

 

        # --- Carrot Cannon (Textured Carrot) ---

        elif name=="Carrot Cannon":

            dmg=1.0+0.2*(stars-1)

            cooldown=max(14-(stars-1),6)

            # Draw Mini Carrot (Lines for texture)

            carrot_surf=pygame.Surface((18,10),pygame.SRCALPHA)

            pygame.draw.polygon(carrot_surf,CARROT_ORANGE,[(0,5),(14,2),(14,8)])

            pygame.draw.line(carrot_surf,CARROT_SHADE,(4,4),(8,6),1)

            pygame.draw.line(carrot_surf,CARROT_SHADE,(10,3),(12,7),1)

            pygame.draw.polygon(carrot_surf,STEM_GREEN,[(14,3),(17,5),(14,7)]) # Stem

            for a in [angle-4,angle,angle+4]:

                b=Bullet(cx,cy,a,11,dmg,ORANGE,surf=carrot_surf)

                bullets.add(b); all_sprites.add(b)

            self.fire_timers[name]=cooldown

 

        # --- Onion Tears (Detailed Teardrop) ---

        elif name=="Onion Tears":

            dmg=1.0+0.2*(stars-1)

            cooldown=max(10-(stars-1),6)

            spread=24+4*(stars-1)

            pellets=5+(stars-1)*2

            angles=[angle+i*(spread//(pellets-1))-spread//2 for i in range(pellets)]

            # Draw Teardrop (Gradient effect)

            tear_surf=pygame.Surface((10,12),pygame.SRCALPHA)

            pygame.draw.polygon(tear_surf,BLUE_PALE,[(5,0),(10,10),(0,10)]) # Lightest layer

            pygame.draw.polygon(tear_surf,(150,180,255),[(5,2),(9,9),(1,9)]) # Shade

            pygame.draw.circle(tear_surf,WHITE,(3,3),1) # Water shine

            for a in angles:

                b=Bullet(cx,cy,a,8,dmg,PALE,range_limit=280+20*(stars-1),surf=tear_surf)

                bullets.add(b); all_sprites.add(b)

            self.fire_timers[name]=cooldown

 

        # --- Tomato Launcher (3D Tomato Sphere) ---

        elif name=="Tomato Launcher":

            dmg=2.0+0.5*(stars-1)

            cooldown=max(24-(stars-1)*2,12)

            # Draw Tomato (Shaded sphere)

            tomo_surf=pygame.Surface((16,16),pygame.SRCALPHA)

            pygame.draw.circle(tomo_surf,RED,(8,8),8)

            pygame.draw.circle(tomo_surf,TOMATO_SHADE,(10,10),6) # Shadow

            pygame.draw.circle(tomo_surf,(255,100,100),(5,5),3) # Highlight

            pygame.draw.rect(tomo_surf,STEM_GREEN,(6,2,4,4),border_radius=1) # Stem

            b=Bullet(cx,cy,angle,6,dmg,RED,surf=tomo_surf)

            bullets.add(b); all_sprites.add(b); self.fire_timers[name]=cooldown

 

        # --- Asparagus Spear (Thickened Javelin) ---

        elif name=="Asparagus Spear":

            dmg=1.2+0.3*(stars-1)

            cooldown=max(18-(stars-1)*3,8)

            range_lim=300+40*(stars-1)

            pierce=1+(stars//2)

            count=1 if stars<3 else (2 if stars<5 else 3)

            offsets=[0] if count==1 else ([-3,3] if count==2 else [-5,0,5])

            # Draw Javelin (Spear texture)

            spear_surf=pygame.Surface((22,8),pygame.SRCALPHA)

            # Main shaft

            pygame.draw.rect(spear_surf, BEAN_GREEN, (0,3,18,2))

            pygame.draw.rect(spear_surf, BEAN_DARK, (2,4,14,1)) # Inner shading

            # Tip

            pygame.draw.polygon(spear_surf, (60,160,90), [(18,1),(22,4),(18,7)])

            for off in offsets:

                b=Bullet(cx,cy,angle+off,12,dmg,BEAN_GREEN,pierce=pierce,range_limit=range_lim,surf=spear_surf)

                bullets.add(b); all_sprites.add(b)

            self.fire_timers[name]=cooldown

 

        # --- Knife (Straight-line piercing) ---

        elif name=="Knife":

            dmg = 1.8 + 0.4 * (stars - 1)

            pierce = 2 + (stars - 1)

            cooldown = max(24 - (stars - 1) * 3, 10)

            range_lim = 400

           

            # Draw Knife Blade (Long, sharp)

            knife_surf = pygame.Surface((36, 6), pygame.SRCALPHA)

            pygame.draw.polygon(knife_surf, GRAY, [(0, 3), (30, 1), (30, 5)]) # Blade body

            pygame.draw.polygon(knife_surf, WHITE, [(30, 2), (36, 3), (30, 4)]) # Tip highlight

            pygame.draw.rect(knife_surf, BROWN, (0, 1, 6, 4), border_radius=1) # Handle

           

            b = Bullet(cx, cy, angle, 14, dmg, GRAY, pierce=pierce, range_limit=range_lim, surf=knife_surf)

            bullets.add(b); all_sprites.add(b); self.fire_timers[name] = cooldown

 

        # --- Spoon (Heavy knockback AoE) ---

        elif name=="Spoon":

            # Buff applied here: 3.5x damage and knockback

            dmg = 9.0 + 1.8 * (stars - 1)

            knock = 35.0 + 10.0 * (stars - 1)

            range_lim = 240 + 30 * (stars - 1)

            cooldown = max(50 - (stars - 1) * 5, 30)

 

            # Draw Spoon (Curved, deep)

            spoon_surf = pygame.Surface((24, 18), pygame.SRCALPHA)

            pygame.draw.ellipse(spoon_surf, GRAY, (0, 0, 18, 18)) # Bowl

            pygame.draw.rect(spoon_surf, GRAY, (18, 7, 6, 4)) # Handle stub

            pygame.draw.ellipse(spoon_surf, WHITE, (2, 2, 14, 14), 1) # Highlight rim

           

            b = Bullet(cx, cy, angle, 4, dmg, GRAY, knockback=knock, range_limit=range_lim, surf=spoon_surf)

            bullets.add(b); all_sprites.add(b); self.fire_timers[name]=cooldown

 

        # --- Hot Sauce Sprayer (Fire Hose DoT) ---

        elif name=="Hot Sauce Sprayer":

            dot_dmg = 0.5 + 0.2 * (stars - 1)

            dot_dur = 60 + 15 * (stars - 1)

            cooldown = 0

           

            # Draw Chili Drop (Tiny, red)

            chili_surf = pygame.Surface((6, 6), pygame.SRCALPHA)

            pygame.draw.circle(chili_surf, CHILI_RED, (3, 3), 3)

            pygame.draw.circle(chili_surf, CHILI_HIGHLIGHT, (2, 2), 1)

           

            # Fire the continuous stream projectile (no spread)

            b = DoTBomb(cx, cy, angle, 16, 0.1, CHILI_RED, dot_damage=dot_dmg, dot_duration=dot_dur, surf=chili_surf)

            bullets.add(b); all_sprites.add(b)

               

            self.fire_timers[name] = cooldown # Resets to 0, ensuring it fires next frame

 

        # --- Avocado Grenade (AoE Slow/Damage) ---

        elif name=="Avocado Grenade":

            cooldown = max(70 - 5 * (stars - 1), 40)

           

            b = AvocadoGrenade(cx, cy, angle, stars)

            bullets.add(b); all_sprites.add(b)

            self.fire_timers[name] = cooldown

 

 

    def gain_xp(self,amount):

        # Apply 50% XP buff if player is Level 6 or higher

        if self.level > 5:

            amount *= 1.5

       

        # XP FIX: Ensure proper loop for multi-level gains and correct overflow

        leveled=False

        self.xp += int(amount)

       

        # CRITICAL WHILE LOOP FIX

        while self.xp >= self.xp_to_next:

            self.xp -= self.xp_to_next # Subtract the exact amount needed for the level

            self.level += 1

           

            # Recalculate xp_to_next for the *new* level

            # Using the existing formula: XP_next = Previous_XP_next * (1.5 + 0.1 * Current_Level)

            # Starting at Level 1 with 10 XP to next.

            self.xp_to_next = int(10 * (1.5**self.level + 0.1 * self.level)) # Reworked the progression curve to be more consistent

           

            # Clamp to prevent tiny or astronomical numbers

            self.xp_to_next = clamp(self.xp_to_next, 10, 999999)

            

            leveled = True

           

        # Ensure xp_to_next is always at least 1 (safety clamp)

        self.xp_to_next = max(1, self.xp_to_next)

 

        return leveled

 

# ---------------- Coin Orb ----------------

class Coin(pygame.sprite.Sprite):

    def __init__(self, x, y):

        super().__init__()

        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)

        # Gold Coin visual

        pygame.draw.circle(self.image, COIN_COLOR, (5, 5), 5)

        pygame.draw.circle(self.image, WHITE, (4, 4), 1) # Highlight

        self.rect = self.image.get_rect(center=(x, y))

        self.value = 1

        self.t = 0

   

    def update(self):

        global player

        self.t += 1

       

        # Simple up/down bob

        self.rect.y += int(math.sin(self.t/12)*0.4)

        

        dx=player.rect.centerx-self.rect.centerx

        dy=player.rect.centery-self.rect.centery

        dist=math.hypot(dx,dy)

       

        if dist<160:

            if dist > 1:

                speed = 0.06 * (160 - dist) / 160 + 0.06

                self.rect.centerx+=int(dx*speed);

                self.rect.centery+=int(dy*speed);

 

 

# ---------------- Enemy projectile (Carrot Shot) ----------------

class EnemyProjectile(pygame.sprite.Sprite):

    def __init__(self,x,y,angle_deg,speed,damage,surf=None):

        super().__init__()

        # Custom Carrot Tank Projectile

        self.original_image=surf

        self.image=pygame.transform.rotate(self.original_image, -angle_deg)

        self.rect=self.image.get_rect(center=(x,y))

        self.angle_deg=angle_deg

        self.vx,self.vy=vec_from_angle(angle_deg,speed)

        self.damage=damage

        self.travel=0

        self.range_limit=500

 

    def update(self):

        center = self.rect.center

        self.image = pygame.transform.rotate(self.original_image, -self.angle_deg)

        self.rect = self.image.get_rect(center=center)

 

        self.rect.x+=int(self.vx); self.rect.y+=int(self.vy)

        self.travel+=abs(self.vx)+abs(self.vy)

        if self.rect.right<0 or self.rect.left>WIDTH or self.rect.bottom<0 or self.rect.top>HEIGHT: self.kill()

        if self.range_limit and self.travel>=self.range_limit: self.kill()

 

# ---------------- Maple Syrup bottle and sticky glob ----------------

class MapleBottle(Bullet):

    def __init__(self,x,y,angle_deg,stars=1,surf=None):

        # MapleBottle inherits from Bullet, so it now has the hit_enemy method too

        super().__init__(x,y,angle_deg, speed=7, damage=0.5+0.2*(stars-1), color=YELLOW, pierce=0, range_limit=220, surf=surf)

        self.spawned_glob=false

        self.stars=stars

        self.spin_rate=15

 

    def spawn_glob(self):

        if not self.spawned_glob:

            g=StickyGlob(self.rect.centerx,self.rect.centery,self.stars)

            globs.add(g); all_sprites.add(g)

            self.spawned_glob=True

 

    def update(self):

        # Spinning effect

        self.angle_deg += self.spin_rate

        self.image = pygame.transform.rotate(self.original_image, -self.angle_deg)

        center = self.rect.center

        self.rect = self.image.get_rect(center=center)

 

        self.rect.x+=int(self.vx); self.rect.y+=int(self.vy)

        self.travel+=abs(self.vx)+abs(self.vy)

        out=(self.rect.right<0 or self.rect.left>WIDTH or self.rect.bottom<0 or self.rect.top>HEIGHT)

        ended=(self.range_limit and self.travel>=self.range_limit)

        if out or ended:

            self.spawn_glob()

            self.kill()

 

class StickyGlob(pygame.sprite.Sprite):

    def __init__(self,x,y,stars=1):

        super().__init__()

        base_radius=26

        self.radius=base_radius + 2*(stars-1)

        self.slow_factor=clamp(0.35 + 0.05*(stars-1), 0.0, 0.6)

        size=self.radius*2

        self.image=pygame.Surface((size,size),pygame.SRCALPHA)

        # Draw translucent yellow glob (Layered for depth)

        pygame.draw.circle(self.image,(240,200,70,180),(self.radius,self.radius),self.radius)

        pygame.draw.circle(self.image,(240,220,120,200),(int(self.radius*0.6),int(self.radius*0.6)),int(self.radius*0.35))

        pygame.draw.circle(self.image,(200,160,50,150),(int(self.radius*1.2),int(self.radius*1.2)),int(self.radius*0.4)) # Shadow spot

        self.rect=self.image.get_rect(center=(x,y))

        self.timer=240

 

    def update(self):

        self.timer-=1

        if self.timer<=0: self.kill()

        for e in pygame.sprite.spritecollide(self,enemies,False):

            e.apply_slow(self.slow_factor,30)

 

# ---------------- Base Enemy with HP scaling ----------------

class BaseEnemy(pygame.sprite.Sprite):

    def __init__(self,color,size,base_hp,base_speed,wave=1):

        super().__init__()

        self.size=size

        self.image=pygame.Surface((size,size),pygame.SRCALPHA)

        pygame.draw.circle(self.image,color,(size//2,size//2),size//2) # Default shape

        self.rect=self.spawn_from_side(size)

        self.health=min(base_hp*5, base_hp+wave)

        self.max_health=self.health # Used for burn calc

        self.base_speed=base_speed

        self.speed_mult=1.0

        self.slow_timer=0

        self.knockback_resist=0.0

        self.burn_damage=0.0

        self.burn_timer=0

        self.burn_tick_timer=0 # Ticks every 30 frames (0.5s)

 

    def spawn_from_side(self,size):

        side=random.choice(["top","bottom","left","right"])

        if side=="top": return self.image.get_rect(center=(random.randint(0,WIDTH),-size))

        if side=="bottom": return self.image.get_rect(center=(random.randint(0,WIDTH),HEIGHT+size))

        if side=="left": return self.image.get_rect(center=(-size,random.randint(0,HEIGHT)))

        return self.image.get_rect(center=(WIDTH+size,random.randint(0,HEIGHT)))

 

    def apply_slow(self,factor,duration):

        self.speed_mult=max(0.4,1.0-factor)

        self.slow_timer=max(self.slow_timer,duration)

 

    def apply_knockback(self,kx,ky,strength):

        strength=max(0.0,strength*(1.0-self.knockback_resist))

        self.rect.x+=int(kx*strength); self.rect.y+=int(ky*strength)

       

    def handle_dot(self):

        if self.burn_timer > 0:

            self.burn_timer -= 1

            self.burn_tick_timer += 1

            # Apply burn damage every 30 frames

            if self.burn_tick_timer >= 30:

                self.health -= self.burn_damage

                self.burn_tick_timer = 0

           

            # Change color slightly to show burn effect

            if self.burn_timer % 10 < 5:

                pass # This is where you might implement a visual flash

            else:

                pass # Use original drawing method if complex

               

            if self.burn_timer == 0:

                self.burn_damage = 0.0

 

 

    def update(self):

        self.handle_dot()

        dx=player.rect.centerx-self.rect.centerx; dy=player.rect.centery-self.rect.centery

        dist=max(1,math.hypot(dx,dy))

        self.rect.x+=int((dx/dist)*self.base_speed*self.speed_mult)

        self.rect.y+=int((dy/dist)*self.base_speed*self.speed_mult)

        if self.slow_timer>0:

            self.slow_timer-=1

            if self.slow_timer==0: self.speed_mult=1.0

 

# ---------------- Specific enemies (ADVANCED VISUALS) ----------------

class Tomato(BaseEnemy):

    def __init__(self,wave=1):

        size=random.randint(28,36)

        super().__init__(RED,size,base_hp=6,base_speed=2.0,wave=wave)

        self.image=pygame.Surface((size,size),pygame.SRCALPHA)

        # Main body (Layered shading for sphere effect)

        pygame.draw.circle(self.image,RED,(size//2,size//2),size//2-2)

        pygame.draw.circle(self.image,TOMATO_SHADE,(int(size*0.6),int(size*0.6)),size//2-5) # Shadow

        pygame.draw.circle(self.image,(255,110,110),(int(size*0.3),int(size*0.3)),size//6) # Highlight

        # Stem/leaf

        pygame.draw.rect(self.image,STEM_GREEN,(size//2-5,0,10,8))

 

class BrusselSprout(BaseEnemy):

    def __init__(self,wave=5):

        size=random.randint(20,26)

        super().__init__(LIGHT_GREEN,size,base_hp=4,base_speed=2.8,wave=wave)

        self.image=pygame.Surface((size,size),pygame.SRCALPHA)

        # Layers for texture/depth

        pygame.draw.circle(self.image,LIGHT_GREEN,(size//2,size//2),size//2)

        pygame.draw.circle(self.image,SPROUT_SHADE,(size//2,size//2),size//2-2,width=2)

        pygame.draw.circle(self.image,GREEN_DARK,(size//2,size//2),size//4,width=1)

        pygame.draw.circle(self.image,LIGHT_GREEN,(size//2+1,size//2-1),size//8) # Central highlight

 

class Potato(BaseEnemy):

    def __init__(self,wave=7):

        size=random.randint(30,40)

        super().__init__(BROWN,size,base_hp=12,base_speed=1.3,wave=wave)

        self.knockback_resist=0.8

        self.image=pygame.Surface((size,size),pygame.SRCALPHA)

       

        # Main body (Irregular ellipse for potato shape)

        surf_w, surf_h = size-8, size-10

        pygame.draw.ellipse(self.image,BROWN,(4,4,surf_w,surf_h))

        pygame.draw.ellipse(self.image,POTATO_LIGHT,(6,6,surf_w-4,surf_h-4)) # Highlight/Texture

       

        # Eyes/spots (Irregular texture)

        pygame.draw.circle(self.image,DARK_BROWN,(size//3,size//3),2)

        pygame.draw.circle(self.image,DARK_BROWN,(size-size//4,size//2),2)

        pygame.draw.circle(self.image,DARK_BROWN,(size//2,size-size//4),1)

 

class ChiliPepper(BaseEnemy):

    def __init__(self,wave=10):

        size=random.randint(24,30)

        super().__init__(CHILI_RED,size,base_hp=7,base_speed=2.4,wave=wave)

        self.dash_cooldown=random.randint(60,120)

        self.dashing=0

        self.image=pygame.Surface((size,size),pygame.SRCALPHA)

        # Pepper body (Curved/pointed shape)

        pygame.draw.polygon(self.image,CHILI_RED,[(size//4, size//2),(size-4,size//3),(size//2,size-6)])

        pygame.draw.polygon(self.image,CHILI_HIGHLIGHT,[(size//4+2, size//2-2),(size-6,size//3+1),(size//2,size-8)]) # Highlight streak

        # Green stem/cap

        pygame.draw.rect(self.image,STEM_GREEN,(size//4-2, size//2-6, 4, 4))

    def update(self):

        if self.dashing>0:

            self.dashing-=1

            sm=self.speed_mult; self.speed_mult=2.2

            super().update()

            self.speed_mult=sm

        else:

            self.dash_cooldown-=1

            if self.dash_cooldown<=0:

                self.dashing=20

                self.dash_cooldown=random.randint(90,140)

            super().update()

 

class CarrotTank(BaseEnemy):

    def __init__(self,wave=12):

        size=random.randint(34,44)

        super().__init__(CARROT_ORANGE,size,base_hp=16,base_speed=1.1,wave=wave)

        self.knockback_resist=0.9

        self.shoot_timer=300

        self.image=pygame.Surface((size,size),pygame.SRCALPHA)

        # Carrot body (Cone/Triangle shape with contour)

        pts = [(size//4, size//4), (size-4, size//2), (size//4, size-size//4)]

        pygame.draw.polygon(self.image,CARROT_ORANGE,pts)

       

        # Texture lines/treads

        pygame.draw.line(self.image,CARROT_SHADE,(size//4,size//4+2),(size-6,size//2+1),2)

        pygame.draw.line(self.image,CARROT_SHADE,(size//4,size-size//4-2),(size-6,size//2-1),2)

        pygame.draw.line(self.image,CARROT_ORANGE,(size//4+4,size//4+4),(size-10,size//2),2) # Brightening line

 

    def update(self):

        super().update()

        self.shoot_timer-=1

        if self.shoot_timer<=0:

            self.shoot_timer=300

            dx=player.rect.centerx-self.rect.centerx

            dy=player.rect.centery-self.rect.centery

            angle=math.degrees(math.atan2(dy,dx))

            # Custom Enemy Projectile Surf (Detailed)

            surf=pygame.Surface((18,8),pygame.SRCALPHA)

            pygame.draw.polygon(surf,CARROT_ORANGE,[(0,4),(14,1),(14,7)])

            pygame.draw.line(surf,CARROT_SHADE,(3,3),(8,5),1)

            pygame.draw.polygon(surf,STEM_GREEN,[(14,2),(18,4),(14,6)])

            proj=EnemyProjectile(self.rect.centerx,self.rect.centery,angle,speed=5,damage=2.0,surf=surf)

            enemy_bullets.add(proj); all_sprites.add(proj)

 

class GreenBeans(BaseEnemy):

    def __init__(self,wave=6):

        size=random.randint(25,35)

        super().__init__(BEAN_GREEN,size,base_hp=5,base_speed=2.2,wave=wave)

        self.image=pygame.Surface((size,size),pygame.SRCALPHA)

       

        # Bean pod (Curved, layered for texture)

        pygame.draw.ellipse(self.image,BEAN_POD,(2,size//4,size-4,size//2))

        pygame.draw.arc(self.image,BEAN_DARK,(2,size//4,size-4,size//2), math.radians(100), math.radians(260), 1) # Shadow line

       

        # Individual beans (Layered)

        for x_offset in [size//3, size//2, size - size//3]:

             pygame.draw.circle(self.image,BEAN_GREEN,(x_offset,size//2),3)

             pygame.draw.circle(self.image,BEAN_DARK,(x_offset,size//2),1) # Tiny dark spot for depth

 

 

# ---------------- XP Orb ----------------

class XPOrb(pygame.sprite.Sprite):

    def __init__(self,x,y,value=1):

        super().__init__()

        self.image=pygame.Surface((12,12),pygame.SRCALPHA)

        # Shaded orb

        pygame.draw.circle(self.image,YELLOW,(6,6),6)

        pygame.draw.circle(self.image,(255,255,150),(4,4),2) # Highlight

        self.rect=self.image.get_rect(center=(x,y)); self.value=int(value)

   

    def update(self):

        # FIX: Correctly referencing the global player object for attraction

        global player

       

        dx=player.rect.centerx-self.rect.centerx

        dy=player.rect.centery-self.rect.centery

        dist=math.hypot(dx,dy)

       

        if dist<160:

            # Normalize direction vector and move orb towards player

            if dist > 1: # Avoid division by zero

                speed = 0.06 * (160 - dist) / 160 + 0.06 # Speed increases as orb gets closer (up to 0.12)

                self.rect.centerx+=int(dx*speed);

                self.rect.centery+=int(dy*speed);

 

 

# ---------------- Food (healing item) ----------------

class Food(pygame.sprite.Sprite):

    def __init__(self,x,y):

        super().__init__()

        self.image=pygame.Surface((16,16),pygame.SRCALPHA)

        # Orange fruit (Shaded)

        pygame.draw.circle(self.image, FOOD_ORANGE, (8,9), 7)

        pygame.draw.circle(self.image, (255,180,120), (5,5), 3) # Highlight

        # Leaf

        pygame.draw.polygon(self.image, FOOD_LEAF, [(7,2),(11,2),(9,5)])

        self.rect=self.image.get_rect(center=(x,y))

        self.t=0

    def update(self):

        self.t += 1

        self.rect.y += int(math.sin(self.t/12)*0.6) # gentle bob

 

# ---------------- Weapon choice menu (with stars) ----------------

# Weapons that must be bought in the shop first

SHOP_WEAPONS=["Maple Syrup","Corn Blaster","Garlic Burst","Carrot Cannon","Onion Tears","Tomato Launcher","Asparagus Spear", "Hot Sauce Sprayer", "Avocado Grenade"]

# Weapons available from start and cannot be blocked

START_WEAPONS=list(set(["Fork", "Spoon", "Knife"])) # Use set/list to ensure unique order/content

# Consolidated list of all weapons for easy reference

ALL_WEAPONS=list(set(SHOP_WEAPONS + START_WEAPONS))

 

def weapon_description(name):

    if name=="Fork": return "Fast piercing stab. Scales with stars (damage & pierce)."

    if name=="Maple Syrup": return "Bottle → sticky field. Bigger & stronger with stars."

    if name=="Corn Blaster": return "Rapid popcorn shots. Damage & rate scale."

    if name=="Garlic Burst": return "Radial blast. More pellets & range with stars."

    if name=="Carrot Cannon": return "3-shot burst. Damage & cooldown scale."

    if name=="Onion Tears": return "Cone spray. More pellets & wider cone with stars."

    if name=="Tomato Launcher": return "Heavy shot. Damage & cooldown scale."

    if name=="Asparagus Spear": return "Long piercing spear. More spears, range, damage."

    if name=="Knife": return "Long, high-damage pierce shot. Scales with damage and pierce."

    if name=="Spoon": return "Short range heavy hitter. Massive knockback. Scales with range and knockback. (HEAVILY BUFFED)"

    if name=="Hot Sauce Sprayer": return "Continuous hose of chili sauce. Massive DoT damage and duration scaling. (Shoots every frame!)"

    if name=="Avocado Grenade": return "Tosses a grenade that explodes, dealing AoE damage and heavy slow."

    return "Veggie mystery."

   

def get_weapon_cost(name):

    # Base costs range from 100 to 250

    if name in ["Corn Blaster", "Maple Syrup"]: return 100

    if name in ["Garlic Burst", "Onion Tears", "Hot Sauce Sprayer"]: return 150

    if name in ["Carrot Cannon", "Tomato Launcher", "Asparagus Spear"]: return 200

    if name == "Avocado Grenade": return 250

    return 120 # Default for safety

 

def wrap_blit(text, x, y, width, font, color):

    words = text.split()

    line = ""; yy = y

    for w in words:

        test = (line + " " + w).strip()

        surf = font.render(test, True, color)

        if surf.get_width() <= width:

            line = test

        else:

            screen.blit(font.render(line, True, color), (x, yy))

            yy += font.render(line, True, color).get_height() + 2

            line = w

    if line:

        screen.blit(font.render(line, True, color), (x, yy))

        return yy + font.render(line, True, color).get_height() + 2 # Return final y

    return yy # Return initial y if no text

 

def stars_text(name):

    s = player.weapon_stars.get(name,0)

    return "★"*s if s>0 else ""

 

def open_level_up_menu(is_start_choice=False):

    global game_state

   

    if is_start_choice:

        # CRITICAL FIX: The pool is STRICTLY the START_WEAPONS. Shop weapons are NOT allowed here.

        full_pool = START_WEAPONS

        options = full_pool # Guaranteed 3 options: Fork, Spoon, Knife

        k_choices = 3

        

    else:

        k_choices = 3

        # 1. Get current run weapons eligible for upgrades (Level < 5)

        upgrade_options = [w for w in player.weapons if player.weapon_stars.get(w, 0) < 5]

       

        # 2. Get ALL owned weapons *not yet in the current run* for adding

        # The pool here includes START_WEAPONS + Shop-bought weapons

        add_options = [w for w in player.owned_weapons if w not in player.weapons]

       

        menu_pool = upgrade_options + add_options

       

        if not menu_pool:

            # Future: handle no upgrade/add option gracefully (e.g., stat boost)

            return

            

        # Selection logic: prioritize upgrades if already capped on weapons

        if len(player.weapons) >= 3 and upgrade_options:

            options = random.sample(upgrade_options, k=min(k_choices, len(upgrade_options)))

        else:

            # Otherwise, mix of upgrades and new acquisitions from the entire pool

            options = random.sample(menu_pool, k=min(k_choices, len(menu_pool)))

       

        if not options:

            return

        

    selected = 0

    paused = True

    while paused:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit(); sys.exit(0)

            elif event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_RIGHT, pygame.K_d): selected = (selected + 1) % len(options)

                elif event.key in (pygame.K_LEFT, pygame.K_a): selected = (selected - 1) % len(options)

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):

                   

                    chosen_weapon = options[selected]

                   

                    # Ensure the chosen weapon's run data is initialized if it's a new weapon for this run (redundant safety)

                    if chosen_weapon not in player.fire_timers:

                        player.fire_timers[chosen_weapon] = 0

                        player.weapon_stars[chosen_weapon] = 1

                       

                    player.add_weapon(chosen_weapon); paused = False

                    if is_start_choice:

                        game_state = STATE_PLAY

 

        screen.fill((20,20,24))

       

        if is_start_choice:

            title = BIGFONT.render("CHOOSE YOUR STARTER WEAPON (1 of 3 available)", True, WHITE)

        else:

            title = BIGFONT.render("Level Up! Choose/Upgrade a weapon", True, WHITE)

           

            # Show current level

            level_text = FONT.render(f"Current Level: {player.level}", True, YELLOW)

            screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 120))

 

        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

 

        card_w, card_h = 240, 150

        gap = 40

        # Now len(options) is correctly capped at 3 for start choice, and 3 for level up

        total_w = card_w * len(options) + gap * max(0, len(options)-1)

        start_x = WIDTH//2 - total_w//2

        y = 220

 

        for i,opt in enumerate(options):

            x = start_x + i*(card_w+gap)

            rect = pygame.Rect(x,y,card_w,card_h)

            pygame.draw.rect(screen, (60,60,90) if i!=selected else UI_ACCENT, rect, border_radius=14)

            pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=14)

 

            # Name + stars

            current_stars = player.weapon_stars.get(opt, 0)

           

            if opt not in player.weapons:

                status_text = "Acquire New"

            elif current_stars < 5:

                status_text = f"Upgrade {current_stars} → {current_stars+1}"

            else:

                status_text = "MAX LEVEL"

               

            star_str = stars_text(opt)

            name_str = f"{opt} {star_str}"

            label = FONT.render(name_str, True, WHITE)

            screen.blit(label, (x + card_w//2 - label.get_width()//2, y + 14))

 

            # Status

            status_label = FONT.render(status_text, True, COIN_COLOR if current_stars < 5 else RED)

            screen.blit(status_label, (x + card_w//2 - status_label.get_width()//2, y + 120))

           

            # Description

            desc = weapon_description(opt)

            wrap_blit(desc, x+14, y+44, card_w-28, FONT, WHITE)

 

        hint = FONT.render("← → choose • Enter to upgrade/pick", True, WHITE)

        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))

        pygame.display.flip()

        clock.tick(60)

 

# ---------------- Combat helpers ----------------

def handle_bullet_enemy_collisions():

    for b in list(bullets):

        hits = pygame.sprite.spritecollide(b, enemies, False)

        if not hits:

            # If a grenade hits nothing and is done moving, explode it anyway

            if isinstance(b, AvocadoGrenade) and b.travel >= b.range_limit:

                 b.explode()

            continue

 

        # Maple bottle or Avocado grenade: break/explode on first hit

        if isinstance(b, MapleBottle):

            b.spawn_glob()

            b.kill()

            continue

        elif isinstance(b, AvocadoGrenade):

            b.explode()

            continue

 

        pierce_used = 0

        for e in hits:

            # Special effects before damage is applied

            b.hit_enemy(e)

 

            # Apply base damage

            e.health -= b.damage

 

            # Knockback if bullet has it

            if getattr(b, "knockback", 0.0) > 0.0:

                # Use player as the center of impulse for player-fired knockback

                dx = e.rect.centerx - player.rect.centerx

                dy = e.rect.centery - player.rect.centery

                dist = max(1.0, math.hypot(dx, dy))

                kx, ky = dx/dist, dy/dist

                e.apply_knockback(kx, ky, b.knockback)

 

            pierce_used += 1

            if pierce_used > b.pierce:

                b.kill()

                break

 

def handle_enemy_projectiles_vs_player():

    hits=pygame.sprite.spritecollide(player, enemy_bullets, True)

    if hits and player.invuln==0:

        player.health-=1

        player.invuln=40

 

def cleanup_dead_enemies_and_drop_rewards():

    for e in list(enemies):

        if e.health <= 0:

            # XP drop scaling and NERFED food chance by enemy type

            if isinstance(e, CarrotTank):

                xp_values=[3,4]; xp_drop_chance=0.9; food_chance=0.05

            elif isinstance(e, Potato):

                xp_values=[2,3]; xp_drop_chance=0.8; food_chance=0.05

            elif isinstance(e, ChiliPepper):

                xp_values=[2,3]; xp_drop_chance=0.75; food_chance=0.045

            elif isinstance(e, GreenBeans):

                xp_values=[1,2]; xp_drop_chance=0.7; food_chance=0.04

            elif isinstance(e, BrusselSprout):

                xp_values=[1,2]; xp_drop_chance=0.65; food_chance=0.035

            else:  # Tomato

                xp_values=[1]; xp_drop_chance=0.6; food_chance=0.02

 

            # Coin Drop (10% chance for 1 coin)

            if random.random() < 0.10:

                coin = Coin(e.rect.centerx, e.rect.centery)

                orbs.add(coin); all_sprites.add(coin)

 

            if random.random() < xp_drop_chance:

                orb = XPOrb(e.rect.centerx, e.rect.centery, value=random.choice(xp_values))

                orbs.add(orb); all_sprites.add(orb)

 

            if random.random() < food_chance:

                food = Food(e.rect.centerx, e.rect.centery)

                foods.add(food); all_sprites.add(food)

 

            e.kill()

 

# ---------------- HUD ----------------

def draw_hud(current_wave):

    # XP bar

    bar_w, bar_h = 280, 14

    x, y = 20, 20

    pygame.draw.rect(screen, GRAY, (x, y, bar_w, bar_h), border_radius=6)

    req = max(1, int(player.xp_to_next))

    fill_w = clamp(int(bar_w * (player.xp / req)), 0, bar_w)

    pygame.draw.rect(screen, YELLOW, (x, y, fill_w, bar_h), border_radius=6)

    txt = FONT.render(f"Level {player.level}  XP {player.xp}/{req}", True, WHITE)

    screen.blit(txt, (x, y + 18))

 

    # Weapons + stars

    wlist = [f"{w} {'★'*player.weapon_stars.get(w,0)}" for w in player.weapons]

    wtxt = FONT.render("Weapons: " + ", ".join(wlist), True, WHITE)

    screen.blit(wtxt, (20, 50))

   

    # Coins Display (shows current run coins)

    coin_txt = FONT.render(f"Coins: {player.coins}", True, COIN_COLOR)

    screen.blit(coin_txt, (20, 75))

 

    # Health

    htxt = FONT.render(f"HP: {player.health}/{player.max_health}", True, WHITE)

    screen.blit(htxt, (WIDTH - 200, 20))

 

    # Wave counter

    wct = BIGFONT.render(f"Wave {current_wave}", True, WHITE)

    screen.blit(wct, (WIDTH - wct.get_width() - 20, HEIGHT - wct.get_height() - 20))

 

# ---------------- Spawning with staggered unlocks ----------------

def spawn_enemy_wave(current_wave, count):

    pool=[]

    if current_wave>=1: pool += [Tomato]*6

    if current_wave>=5: pool += [BrusselSprout]*4

    if current_wave>=6: pool += [GreenBeans]*4

    if current_wave>=7: pool += [Potato]*3

    if current_wave>=10: pool += [ChiliPepper]*3

    if current_wave>=12: pool += [CarrotTank]*2

    if not pool: pool=[Tomato]

    for _ in range(count):

        kind=random.choice(pool)

        e=kind(current_wave)

        enemies.add(e); all_sprites.add(e)

 

# ---------------- Menu UI ----------------

class Button:

    def __init__(self, rect, text):

        self.rect=pygame.Rect(rect)

        self.text=text

    def draw(self):

        mx,my=pygame.mouse.get_pos()

        hover=self.rect.collidepoint(mx,my)

        bg=(60,60,90) if not hover else UI_ACCENT

        pygame.draw.rect(screen,bg,self.rect,border_radius=10)

        pygame.draw.rect(screen,WHITE,self.rect,2,border_radius=10)

        label=FONT.render(self.text,True,WHITE)

        screen.blit(label,(self.rect.centerx - label.get_width()//2, self.rect.centery - label.get_height()//2))

    def clicked(self, event):

        return event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(event.pos)

 

def draw_menu():

    screen.fill(DARK_BG)

    title=BIGFONT.render("Veggie Vengeance",True,WHITE)

    screen.blit(title,(WIDTH//2 - title.get_width()//2, 120))

    sub=FONT.render("Broccoli vs the pantry. XP loop is stable now!",True,WHITE)

    screen.blit(sub,(WIDTH//2 - sub.get_width()//2, 170))

   

    # Display persistent coins

    coin_txt = BIGFONT.render(f"Total Coins: {Player.game_coins}", True, COIN_COLOR)

    screen.blit(coin_txt, (WIDTH//2 - coin_txt.get_width()//2, 480))

 

def draw_shop(event):

    global SHOP_SCROLL_OFFSET, SHOP_MAX_SCROLL, SHOP_CONTENT_HEIGHT, SHOP_DRAG_START_Y, SHOP_SCROLL_START, game_state

   

    screen.fill(DARK_BG)

    title = BIGFONT.render("THE PANTRY'S BLACK MARKET", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

   

    # Current Coins (Now shows Player.game_coins which is up-to-date)

    coin_txt = FONT.render(f"Your Coins: {Player.game_coins}", True, COIN_COLOR)

    screen.blit(coin_txt, (WIDTH - coin_txt.get_width() - 30, 30))

 

    # Weapons available to buy (not yet owned)

    # CRITICAL FIX: Use the static persistence set for checking ownership

    buyable_weapons = [w for w in SHOP_WEAPONS if w not in Player.owned_weapons_persist]

   

    # --- Shop Drawing Surface (For Clipping) ---

    shop_surface = pygame.Surface((SHOP_CONTENT_AREA.width, SHOP_CONTENT_AREA.height), pygame.SRCALPHA)

    shop_surface.fill((30,30,40, 180)) # Semi-transparent background for the scrollable area

   

    card_w, card_h = 240, 150

    gap = 40

   

    cols = 3

   

    # --- Calculate Total Content Height ---

    if buyable_weapons:

        rows = math.ceil(len(buyable_weapons) / cols)

        # 30 is for cost/button row, 10 is padding for the last row

        SHOP_CONTENT_HEIGHT = rows * (card_h + gap + 30) + gap

    else:

        SHOP_CONTENT_HEIGHT = SHOP_CONTENT_AREA.height + 1 # Forces max scroll to 0 (or slightly more than area height for no scroll)

 

    SHOP_MAX_SCROLL = max(0, SHOP_CONTENT_HEIGHT - SHOP_CONTENT_AREA.height)

    SHOP_SCROLL_OFFSET = clamp(SHOP_SCROLL_OFFSET, -SHOP_MAX_SCROLL, 0) # Negative offset moves content UP

 

   

    total_w = card_w * cols + gap * (cols - 1)

    start_x_on_surface = SHOP_CONTENT_AREA.width // 2 - total_w // 2

   

    # --- Draw Items onto Shop Surface ---

    for i, opt in enumerate(buyable_weapons):

        cost = get_weapon_cost(opt)

       

        col = i % cols

        row = i // cols

       

        x = start_x_on_surface + col * (card_w + gap)

        # Apply scroll offset to the y position

        y = gap + row * (card_h + gap + 30) + SHOP_SCROLL_OFFSET

 

        rect = pygame.Rect(x, y, card_w, card_h)

       

        # Only draw if the card is visible within the surface's height

        if y + card_h > 0 and y < SHOP_CONTENT_AREA.height:

            # Check affordability against persistent coins

            can_afford = Player.game_coins >= cost

            bg_color = (60, 60, 90)

            if can_afford:

                bg_color = (40, 70, 40) # Greenish for buyable

           

            pygame.draw.rect(shop_surface, bg_color, rect, border_radius=10)

            pygame.draw.rect(shop_surface, WHITE, rect, width=2, border_radius=10)

 

            # Name

            name_label = BIGFONT.render(opt, True, WHITE)

            shop_surface.blit(name_label, (x + 14, y + 14))

 

            # Description

            desc = weapon_description(opt)

            wrap_blit_surface(shop_surface, desc, x + 14, y + 54, card_w - 28, FONT, WHITE)

 

            # Cost and Buy button

            cost_txt = MONO_FONT.render(f"Cost: {cost} Coins", True, COIN_COLOR)

            shop_surface.blit(cost_txt, (x + 14, y + card_h + 8))

           

            buy_rect_on_surface = pygame.Rect(x + card_w - 70, y + card_h + 4, 60, 24)

            buy_text = "BUY"

            if can_afford:

                pygame.draw.rect(shop_surface, GREEN, buy_rect_on_surface, border_radius=4)

            else:

                pygame.draw.rect(shop_surface, RED, buy_rect_on_surface, border_radius=4)

               

            buy_label = FONT.render(buy_text, True, WHITE)

            shop_surface.blit(buy_label, (buy_rect_on_surface.centerx - buy_label.get_width()//2, buy_rect_on_surface.centery - buy_label.get_height()//2))

 

    # Draw the shop surface onto the main screen

    screen.blit(shop_surface, (SHOP_CONTENT_AREA.x, SHOP_CONTENT_AREA.y))

   

    # Draw border around the scrollable area

    pygame.draw.rect(screen, UI_ACCENT, SHOP_CONTENT_AREA, width=4, border_radius=10)

 

    # --- Scroll Bar Visual (Simple) ---

    if SHOP_MAX_SCROLL > 0:

        bar_x = SHOP_CONTENT_AREA.right - 10

        bar_y = SHOP_CONTENT_AREA.y

        bar_w = 6

        bar_h = SHOP_CONTENT_AREA.height

       

        # Calculate thumb size and position

        thumb_h = max(20, int(bar_h * (bar_h / SHOP_CONTENT_HEIGHT)))

        scroll_ratio = -SHOP_SCROLL_OFFSET / SHOP_MAX_SCROLL

        thumb_y = bar_y + (bar_h - thumb_h) * scroll_ratio

       

        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=3) # Track

        pygame.draw.rect(screen, WHITE, (bar_x, thumb_y, bar_w, thumb_h), border_radius=3) # Thumb

 

    # --- Event Handling (Scroll, Drag, Buy, **NEW ARROW KEYS**) ---

    scroll_amount = 40

    

    if event:

        bought_item = False

       

        # Check for drag start or buy click

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and SHOP_CONTENT_AREA.collidepoint(event.pos):

            mx, my = event.pos

           

            # 1. Check for Buy button clicks (Must happen first)

            for i, opt in enumerate(buyable_weapons):

                cost = get_weapon_cost(opt)

                col = i % cols

                row = i // cols

                x = start_x_on_surface + col * (card_w + gap)

                y = gap + row * (card_h + gap + 30)

               

                # Convert screen coordinates to coordinates relative to the scrollable content

                virtual_mx = mx - SHOP_CONTENT_AREA.x

                virtual_my = my - SHOP_CONTENT_AREA.y - SHOP_SCROLL_OFFSET

                

                buy_rect_virtual = pygame.Rect(x + card_w - 70, y + card_h + 4, 60, 24)

               

                if buy_rect_virtual.collidepoint(virtual_mx, virtual_my):

                    # Check affordability against the static/persistent coin count

                    if Player.game_coins >= cost:

                        Player.game_coins -= cost

                        # CRITICAL FIX: Update the static persistence immediately

                        Player.owned_weapons_persist.add(opt)

                        

                        # We also need to update the currently loaded player object if it exists (for coin display)

                        if 'player' in globals():

                             player.coins = Player.game_coins # Sync the current player object's coins

                             player.owned_weapons = Player.owned_weapons_persist.copy() # Sync the player's weapon set

                             # The newly owned weapon must have its run-time data initialized too

                             player.fire_timers[opt] = 0

                             player.weapon_stars[opt] = 1

 

                        bought_item = True

                        break

                        

            # 2. Start Drag ONLY if no item was bought

            if not bought_item:

                SHOP_DRAG_START_Y = my

                SHOP_SCROLL_START = SHOP_SCROLL_OFFSET

 

        # Handle drag end

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

            SHOP_DRAG_START_Y = None

           

        # Handle continuous drag motion

        elif event.type == pygame.MOUSEMOTION and SHOP_DRAG_START_Y is not None:

            dy = event.pos[1] - SHOP_DRAG_START_Y

            new_offset = SHOP_SCROLL_START + dy

            SHOP_SCROLL_OFFSET = clamp(new_offset, -SHOP_MAX_SCROLL, 0)

       

        # Mouse wheel scrolling

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5) and SHOP_CONTENT_AREA.collidepoint(event.pos):

            if event.button == 4: # Scroll Up

                SHOP_SCROLL_OFFSET = clamp(SHOP_SCROLL_OFFSET + scroll_amount, -SHOP_MAX_SCROLL, 0)

            elif event.button == 5: # Scroll Down

                SHOP_SCROLL_OFFSET = clamp(SHOP_SCROLL_OFFSET - scroll_amount, -SHOP_MAX_SCROLL, 0)

 

        # KEYBOARD SCROLLING

        elif event.type == pygame.KEYDOWN and game_state == STATE_SHOP:

             if event.key == pygame.K_UP:

                SHOP_SCROLL_OFFSET = clamp(SHOP_SCROLL_OFFSET + scroll_amount, -SHOP_MAX_SCROLL, 0)

             elif event.key == pygame.K_DOWN:

                SHOP_SCROLL_OFFSET = clamp(SHOP_SCROLL_OFFSET - scroll_amount, -SHOP_MAX_SCROLL, 0)

 

 

        # If an item was bought, we need to return early to refresh the shop state

        if bought_item:

            # Rerun the drawing logic in the main loop to instantly show changes

            pass

 

    if not buyable_weapons:

        msg = FONT.render("You own all the purchasable weapons! Well done.", True, WHITE)

        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

 

    btn_back.draw()

 

# Helper function for drawing wrapped text onto a surface

def wrap_blit_surface(target_surface, text, x, y, width, font, color):

    words = text.split()

    line = ""; yy = y

    for w in words:

        test = (line + " " + w).strip()

        surf = font.render(test, True, color)

        if surf.get_width() <= width:

            line = test

        else:

            target_surface.blit(font.render(line, True, color), (x, yy))

            yy += font.render(line, True, color).get_height() + 2

            line = w

    if line:

        target_surface.blit(font.render(line, True, color), (x, yy))

        return yy + font.render(line, True, color).get_height() + 2 # Return final y

 

# ---------------- Game reset ----------------

def reset_game():

    global all_sprites, enemies, bullets, enemy_bullets, orbs, globs, foods, explosions, player, wave, spawn_timer, spawn_rate, wave_timer, game_state

   

    # CRITICAL FIX 1: Initialize owned_weapons_persist to ensure START_WEAPONS are always present.

    if not Player.owned_weapons_persist:

        Player.owned_weapons_persist = set(START_WEAPONS)

    # Ensure START_WEAPONS are always in the owned set (since they cannot be bought)

    Player.owned_weapons_persist.update(START_WEAPONS)

   

    # If a player object exists (i.e. run just ended), ensure coins are saved before resetting

    if 'player' in globals() and player is not None and game_state == STATE_PLAY:

        player.end_run()

    

    all_sprites=pygame.sprite.Group()

    enemies=pygame.sprite.Group()

    bullets=pygame.sprite.Group()

    enemy_bullets=pygame.sprite.Group()

    orbs=pygame.sprite.Group()

    globs=pygame.sprite.Group()

    foods=pygame.sprite.Group()

    explosions=pygame.sprite.Group() # Initialize new group

 

    player=Player() # Player initializes and loads persistent coins/owned_weapons/weapon data

    all_sprites.add(player)

 

    wave=1

    spawn_timer=0

    spawn_rate=48

    wave_timer=60*20  # 20s per wave

   

    # Game state remains at STATE_MENU or goes to STATE_PLAY via start choice

    if game_state != STATE_PLAY:

        game_state=STATE_MENU

   

    return True

 

# ---------------- Main loop ----------------

# Menu buttons

btn_play=Button((WIDTH//2-100, 260, 200, 54), "Start Run")

btn_shop=Button((WIDTH//2-100, 330, 200, 54), "Shop")

btn_ach =Button((WIDTH//2-100, 400, 200, 54), "Achievements")

btn_back=Button((20, 20, 120, 44), "Back")

 

# Initial setup

reset_game()

game_state = STATE_MENU

waiting_for_start_choice = False

 

running=True

while running:

    dt=clock.tick(60)

    keys=pygame.key.get_pressed()

   

    current_event = None

 

    for event in pygame.event.get():

        current_event = event

        if event.type==pygame.QUIT:

            # Save coins before quitting

            if 'player' in globals() and player is not None:

                 player.end_run()

            running=False

 

        if game_state==STATE_MENU:

            if btn_play.clicked(event):

                # We need a new player object for a fresh run

                reset_game()

                waiting_for_start_choice = True

            elif btn_shop.clicked(event):

                # CRITICAL FIX: Ensure current run's coins are saved before entering shop if coming from a run

                if 'player' in globals() and player is not None:

                    player.end_run()

                game_state=STATE_SHOP

            elif btn_ach.clicked(event):

                game_state=STATE_ACH

        elif game_state == STATE_SHOP:

             if btn_back.clicked(event):

                game_state=STATE_MENU

        elif game_state == STATE_ACH:

            if btn_back.clicked(event):

                game_state=STATE_MENU

       

        # Pass event to draw_shop for mouse wheel/click/key handling

        if game_state == STATE_SHOP:

            draw_shop(current_event)

 

    if waiting_for_start_choice:

        # This function handles the weapon choice and sets game_state=STATE_PLAY

        open_level_up_menu(is_start_choice=True)

        waiting_for_start_choice = False

        continue

 

    if game_state==STATE_MENU:

        draw_menu()

        btn_play.draw(); btn_shop.draw(); btn_ach.draw()

        pygame.display.flip()

        continue

 

    if game_state==STATE_SHOP:

        # Draw is handled by the event loop call, but we still need to flip

        draw_shop(None)

        pygame.display.flip()

        continue

 

    if game_state==STATE_ACH:

        screen.fill(DARK_BG)

        title=BIGFONT.render("Achievements",True,WHITE)

        screen.blit(title,(WIDTH//2 - title.get_width()//2, 120))

        msg=FONT.render("No achievements yet. Play to unlock in future updates.",True,WHITE)

        screen.blit(msg,(WIDTH//2 - msg.get_width()//2, 180))

        btn_back.draw()

        pygame.display.flip()

        continue

 

    # --------- STATE_PLAY ----------

    # Spawns

    spawn_timer+=1

    wave_timer-=1

    if spawn_timer>=spawn_rate:

        spawn_timer=0

        spawn_enemy_wave(wave, count=random.randint(2,4))

    if wave_timer<=0:

        wave+=1

        wave_timer=60*20

        spawn_rate=max(24,int(spawn_rate*0.92))

 

    # Updates

    player.update(keys)

    enemies.update()

    bullets.update()

    enemy_bullets.update()

    orbs.update()

    globs.update()

    foods.update()

    explosions.update() # Update the new explosion visuals

   

    # Collect Orbs and separate types

    collected_orbs=pygame.sprite.spritecollide(player,orbs,True)

    leveled=False

   

    # Coin/XP processing

    for orb in collected_orbs:

        if isinstance(orb, Coin):

            player.coins += orb.value

        elif isinstance(orb, XPOrb):

             leveled = player.gain_xp(orb.value) or leveled

 

    if leveled:

        open_level_up_menu()

 

    # Combat and cleanup

    handle_bullet_enemy_collisions()

    handle_enemy_projectiles_vs_player()

    cleanup_dead_enemies_and_drop_rewards()

 

    # Enemy contact with player (touch damage)

    if player.invuln==0:

        touch=pygame.sprite.spritecollide(player,enemies,False)

        if touch:

            player.health-=1

            player.invuln=40

 

    # Collect food and heal

    collected_food=pygame.sprite.spritecollide(player,foods,True)

    for _ in collected_food:

        player.health = min(player.health + 2, player.max_health)

 

    # Check death

    if player.health<=0:

        # Save coins before returning to menu

        player.end_run()

        game_state=STATE_MENU

 

    # Draw gameplay

    screen.fill(DARK_BG)

    all_sprites.draw(screen)

    globs.draw(screen)

    foods.draw(screen)

    explosions.draw(screen) # Draw explosions over everything else

    draw_hud(wave)

    pygame.display.flip()

 

pygame.quit()