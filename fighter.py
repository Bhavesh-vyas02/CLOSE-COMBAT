import pygame

class Fighter():
  def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound, is_ai=False, character_type="WARRIOR"):
    self.player = player
    self.size = data[0] #
    self.image_scale = data[1]
    self.offset = data[2]
    self.flip = flip
    self.animation_list = self.load_images(sprite_sheet, animation_steps)
    self.action = 0#0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
    self.frame_index = 0
    self.image = self.animation_list[self.action][self.frame_index]
    self.update_time = pygame.time.get_ticks()
    self.rect = pygame.Rect((x, y, 80, 180))
    self.vel_y = 0
    self.running = False
    self.jump = False
    self.attacking = False
    self.attack_type = 0
    self.attack_cooldown = 0
    self.attack_sound = sound
    self.hit = False
    self.health = 100
    self.alive = True
    
    # Optimized AI attributes
    self.is_ai = is_ai
    self.character_type = character_type
    self.ai_last_decision = pygame.time.get_ticks()
    self.ai_reaction_time = 500  # Increased for better performance
    self.ai_current_action = "idle"
    self.ai_decision_cache = {"move": 0, "jump": False, "attack": 0}
    self.ai_cache_valid = False
    
    # Optimized AI behavior parameters
    self.set_ai_personality()

  def set_ai_personality(self):
    """Optimized AI behavior based on character type"""
    if not self.is_ai:
      return
      
    if self.character_type == "WARRIOR":
      self.ai_aggression = 0.7
      self.ai_preferred_range = 120
      self.ai_attack_frequency = 0.6
      
    elif self.character_type == "WIZARD":
      self.ai_aggression = 0.5
      self.ai_preferred_range = 200
      self.ai_attack_frequency = 0.4
      
    elif self.character_type == "HUNTRESS":
      self.ai_aggression = 0.8
      self.ai_preferred_range = 150
      self.ai_attack_frequency = 0.7
      
    elif self.character_type == "KING":
      self.ai_aggression = 0.6
      self.ai_preferred_range = 140
      self.ai_attack_frequency = 0.5
      
    elif self.character_type == "HERO_KNIGHT":
      self.ai_aggression = 0.7
      self.ai_preferred_range = 130
      self.ai_attack_frequency = 0.6
      
    else:  # MARTIAL_HERO
      self.ai_aggression = 0.9
      self.ai_preferred_range = 110
      self.ai_attack_frequency = 0.8

  def ai_make_decision(self, target, screen_width):
    """Optimized AI decision making - reduced lag"""
    if not self.is_ai or not self.alive or self.attacking:
      return {"move": 0, "jump": False, "attack": 0}
    
    current_time = pygame.time.get_ticks()
    
    # Use cached decision if still valid (major performance improvement)
    if self.ai_cache_valid and current_time - self.ai_last_decision < self.ai_reaction_time:
      return self.ai_decision_cache
    
    # Make new decision
    self.ai_last_decision = current_time
    self.ai_cache_valid = True
    
    # Fast distance calculation
    distance = abs(self.rect.centerx - target.rect.centerx)
    
    # Initialize decision
    decision = {"move": 0, "jump": False, "attack": 0}
    
    # Health-based aggression modifier (simple calculation)
    health_ratio = self.health / 100.0
    current_aggression = self.ai_aggression * health_ratio
    
    # Simple movement logic
    if distance > self.ai_preferred_range + 50:
      # Move closer
      decision["move"] = 1 if target.rect.centerx > self.rect.centerx else -1
      self.ai_current_action = "approach"
      
    elif distance < self.ai_preferred_range - 30:
      # Attack or back away
      if current_aggression > 0.5 and self.attack_cooldown == 0:
        import random
        decision["attack"] = random.choice([1, 2])
        self.ai_current_action = "attack"
      else:
        decision["move"] = -1 if target.rect.centerx > self.rect.centerx else 1
        self.ai_current_action = "retreat"
        
    else:
      # In range - attack or circle
      if self.attack_cooldown == 0:
        import random
        if random.random() < self.ai_attack_frequency:
          decision["attack"] = random.choice([1, 2])
          self.ai_current_action = "attack"
        else:
          decision["move"] = random.choice([-1, 0, 1])
          self.ai_current_action = "circle"
    
    # Simple defensive jump
    if target.attacking and distance < 150:
      import random
      if random.random() < 0.4:
        decision["jump"] = True
        decision["move"] = -1 if target.rect.centerx > self.rect.centerx else 1
    
    # Avoid screen edges
    if self.rect.centerx < 100:
      decision["move"] = 1
    elif self.rect.centerx > screen_width - 100:
      decision["move"] = -1
    
    # Cache the decision
    self.ai_decision_cache = decision
    return decision

  def ai_continue_current_action(self):
    """Simple action continuation"""
    if self.ai_cache_valid:
      return self.ai_decision_cache
    return {"move": 0, "jump": False, "attack": 0}

  def ai_get_debug_info(self):
    """Simplified debug info"""
    if not self.is_ai:
      return {}
    
    return {
      "aggression": f"{self.ai_aggression:.2f}",
      "range": self.ai_preferred_range,
      "action": self.ai_current_action,
      "health": self.health
    }



  def ai_get_debug_info(self):
    """Get AI debug information for development"""
    if not self.is_ai:
      return {}
    
    return {
      "state": self.ai_state_machine,
      "adaptation": f"{self.ai_adaptation_level:.2f}",
      "prediction": f"{self.ai_prediction_accuracy:.2f}",
      "risk": f"{self.ai_risk_assessment:.2f}",
      "stamina": f"{self.ai_stamina_management:.1f}",
      "combo_count": self.ai_combo_counter,
      "pattern_history_size": len(self.ai_player_pattern_history),
      "current_action": self.ai_current_action
    }

  def load_images(self, sprite_sheet, animation_steps):
    animation_list = []
    for y, animation in enumerate(animation_steps):
      temp_img_list = []
      for x in range(animation):
        temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
        temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
      animation_list.append(temp_img_list)
    return animation_list

  def move(self, screen_width, screen_height, surface, target, round_over):
    SPEED = 10
    GRAVITY = 2
    dx = 0
    dy = 0
    self.running = False
    self.attack_type = 0

    #can only perform other actions if not currently attacking
    if self.attacking == False and self.alive == True and round_over == False:
      
      if self.is_ai:
        # Optimized AI decision making with caching
        ai_decision = self.ai_make_decision(target, screen_width)
        
        # Apply AI movement
        if ai_decision["move"] == -1:
          dx = -SPEED
          self.running = True
        elif ai_decision["move"] == 1:
          dx = SPEED
          self.running = True
        
        # Apply AI jump
        if ai_decision["jump"] and self.jump == False:
          self.vel_y = -30
          self.jump = True
        
        # Apply AI attack
        if ai_decision["attack"] > 0:
          self.attack(target)
          self.attack_type = ai_decision["attack"]
          # Invalidate cache after attack
          self.ai_cache_valid = False
      
      else:
        # Human player controls
        key = pygame.key.get_pressed()
        
        #check player 1 controls
        if self.player == 1:
          #movement
          if key[pygame.K_a]:
            dx = -SPEED
            self.running = True
          if key[pygame.K_d]:
            dx = SPEED
            self.running = True
          #jump
          if key[pygame.K_w] and self.jump == False:
            self.vel_y = -30
            self.jump = True
          #attack
          if key[pygame.K_r] or key[pygame.K_t]:
            self.attack(target)
            #determine which attack type was used
            if key[pygame.K_r]:
              self.attack_type = 1
            elif key[pygame.K_t]:
              self.attack_type = 2

        #check player 2 controls
        if self.player == 2:
          #movement
          if key[pygame.K_LEFT]:
            dx = -SPEED
            self.running = True
          if key[pygame.K_RIGHT]:
            dx = SPEED
            self.running = True
          #jump
          if key[pygame.K_UP] and self.jump == False:
            self.vel_y = -30
            self.jump = True
          #attack
          if key[pygame.K_KP1] or key[pygame.K_KP2]:
            self.attack(target)
            #determine which attack type was used
            if key[pygame.K_KP1]:
              self.attack_type = 1
            elif key[pygame.K_KP2]:
              self.attack_type = 2

    #apply gravity
    self.vel_y += GRAVITY
    dy += self.vel_y

    #ensure player stays on screen
    if self.rect.left + dx < 0:
      dx = -self.rect.left
    if self.rect.right + dx > screen_width:
      dx = screen_width - self.rect.right
    if self.rect.bottom + dy > screen_height - 110:
      self.vel_y = 0
      self.jump = False
      dy = screen_height - 110 - self.rect.bottom

    #ensure players face each other
    if target.rect.centerx > self.rect.centerx:
      self.flip = False
    else:
      self.flip = True

    #apply attack cooldown
    if self.attack_cooldown > 0:
      self.attack_cooldown -= 1

    #update player position
    self.rect.x += dx
    self.rect.y += dy

  def attack(self, target):
    if self.attack_cooldown == 0:
      self.attacking = True
      self.attack_sound.play()
      
      # Different attack ranges for each character
      if self.attack_sound == pygame.mixer.Sound("assets/audio/sword.wav"):
        if self.size == 162:  # Warrior
          # Shorter range for melee attacks
          attack_width = 1.5 * self.rect.width
          attack_height = self.rect.height
          attack_y_offset = 0
          damage = 12  # More damage for melee
        else:  # Samurai
          # Fast, precise attacks
          attack_width = 2.0 * self.rect.width
          attack_height = self.rect.height * 1.1
          attack_y_offset = -10
          damage = 15  # Highest damage but shorter range than Wizard
      else:  # Wizard
        # Longer range for magic attacks
        attack_width = 2.5 * self.rect.width
        attack_height = self.rect.height * 1.2
        attack_y_offset = -20  # Slightly higher hit area for magic
        damage = 8  # Less damage for ranged attacks
      
      # Create attack rectangle based on character facing direction
      if self.flip:
        attack_rect = pygame.Rect(
          self.rect.centerx - attack_width,
          self.rect.y + attack_y_offset,
          attack_width,
          attack_height
        )
      else:
        attack_rect = pygame.Rect(
          self.rect.centerx,
          self.rect.y + attack_y_offset,
          attack_width,
          attack_height
        )
      
      # Check for collision and apply damage
      if attack_rect.colliderect(target.rect):
        target.health -= damage
        target.hit = True

  def update(self):
    #check what action the player is performing
    if self.health <= 0:
      self.health = 0
      self.alive = False
      self.update_action(6)#6:death
    elif self.hit == True:
      self.update_action(5)#5:hit
    elif self.attacking == True:
      if self.attack_type == 1:
        self.update_action(3)#3:attack1
      elif self.attack_type == 2:
        self.update_action(4)#4:attack2
    elif self.jump == True:
      self.update_action(2)#2:jump
    elif self.running == True:
      self.update_action(1)#1:run
    else:
      self.update_action(0)#0:idle

    animation_cooldown = 50
    #update image
    self.image = self.animation_list[self.action][self.frame_index]
    #check if enough time has passed since the last update
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    #check if the animation has finished
    if self.frame_index >= len(self.animation_list[self.action]):
      #if the player is dead then end the animation
      if self.alive == False:
        self.frame_index = len(self.animation_list[self.action]) - 1
      else:
        self.frame_index = 0
        #check if an attack was executed
        if self.action in [3, 4]:
          self.attacking = False
          self.attack_cooldown = 20
        #check if damage was taken
        if self.action == 5:
          self.hit = False
          #if the player was in the middle of an attack, then the attack is stopped
          self.attacking = False
          self.attack_cooldown = 20

  def update_action(self, new_action):
    #check if the new action is different to the previous one
    if new_action != self.action:
      self.action = new_action
      #update the animation settings
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def draw(self, surface):
    img = pygame.transform.flip(self.image, self.flip, False)
    surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))