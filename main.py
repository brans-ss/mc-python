import sys
print(sys.version)

import pygame
import random
import inventory_mod
import time

pygame.init()

#ensure values are divisble by 50
screen_width = 1200
screen_height = 800
characters_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
characters_list.extend(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"])
characters_list.extend(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ",", ";", ":", "$", "#", "'", "!", '"', "/", "?", "%", "&", "(", ")", "@" ])


screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Minecraft')
clock = pygame.time.Clock()
running = True 
 
class Sprite(pygame.sprite.Sprite):
	def __init__(self, pos, size, img, rect_colour, surface = None, remarks = None):
		pygame.sprite.Sprite.__init__(self)
		if img:
			self.filename = img
			img = pygame.image.load(img).convert_alpha()
			self.image = pygame.transform.scale(img, size)

		elif rect_colour: 
			self.image = pygame.Surface(size)
			self.image.fill(rect_colour)

		elif surface:
			self.image = pygame.transform.scale(surface, size)
		else: raise ValueError("You must provide either an 'img', a 'rect' or a 'surface'.")
		
		self.rect = self.image.get_rect()
		self.rect.center = pos	
		self.clicked = False
		self.remarks = remarks

	def update_pos(self, pos):
		self.rect.center = pos

	def button_click(self, alpha, hover_alpha):
			action = False

			if self.rect.collidepoint(pygame.mouse.get_pos()):
				self.image.set_alpha(hover_alpha)
				if pygame.mouse.get_pressed(3)[0] == True and self.clicked == False:
					self.clicked = True
					action = True

			else: self.image.set_alpha(alpha)

			if pygame.mouse.get_pressed(3)[0] == False:
				self.clicked = False
			
			return action

	def add_remarks(self, remarks):
		self.remarks = remarks

	def get_remarks(self):
		return self.remarks

	def change_image(self, new_surface):
		if isinstance(new_surface, pygame.sprite.Sprite):
			img = new_surface.image
		else: 
			img = pygame.image.load(new_surface).convert_alpha()
			self.filename = new_surface
		self.image = img

	def change_size(self, new_size, scale = None):
		if scale:
			new_size = self.image.get_width() * scale, self.image.get_height() * scale
		self.image = pygame.transform.scale(self.image, new_size)	

	def convert_colour(self, old_col, new_col):
		pixel_array = pygame.PixelArray(self.image)
		pixel_array.replace(old_col, new_col)
		del pixel_array

		return self

class Spritesheet(pygame.sprite.Sprite):
	def __init__(self, sheet, size):
		pygame.sprite.Sprite.__init__(self)
		self.sheet = pygame.image.load(sheet).convert_alpha()
		self.sheet = pygame.transform.scale(self.sheet, size)

	def get_image(self, sprite_pos, sprite_size, pos, size):
		image = pygame.Surface(sprite_size, pygame.SRCALPHA).convert_alpha()
		image.blit(self.sheet, (0,0), (sprite_pos[0], sprite_pos[1], sprite_size[0], sprite_size[1]))
		image = Sprite(pos, size, None, None, image)

		return image

	def combine_images(sources_grp, pos, scale, gap):
		combined_height = 0
		combined_width = 0
		for source in sources_grp:
			combined_width += source.image.get_width() + gap
			if combined_height < source.image.get_height():
				combined_height = source.image.get_height()

		combined_image = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA).convert_alpha()
		offset = 0
		for surf in sources_grp:
			combined_image.blit(surf.image, (offset, 0))
			offset += surf.image.get_width() + gap
		
		offset -= gap
		size = (offset*scale, combined_height*scale)
		combined_image = Sprite(pos, size, None, None, combined_image)
		return combined_image



player = Sprite((550, 400), (50,50), "img/alexmc.png", None)

#generate terrain
gen_blocks_left = random.randint(1,8)
steepness = 1
gen_y = 425

terrain_grp = pygame.sprite.Group()
for x in range(2000//50):
	terrain = Sprite((x*50-475, gen_y), (50,50), "img/Grass_Block.png", None)
	terrain_grp.add(terrain)
 
	dirt_range = random.randint(1,2)
	for y in range(10):
		if y <= dirt_range:
			terrain = Sprite((x*50-475, y*50+gen_y+50), (50,50), "img/Dirt.png", None)
		else: terrain = Sprite((x*50- 475, y*50+gen_y+50),  (50,50), "img/Stone.png", None)
		terrain_grp.add(terrain) 
	gen_blocks_left -= 1
	if gen_blocks_left == 0:
		gen_y += random.randint(-1,1)*50
		gen_blocks_left = random.randint(2,8)

jump_force = 4.5
velocity_x = 0
velocity_y = 0
player_force = 3
g_field_strength = 0.1
resistance = 0
falling = 0

def player_movement():
	global accel
	global velocity_x
	global velocity_y
	global resistance
	global jump_force
	global g_field_strength
	global falling

	left_click = pygame.mouse.get_pressed(3)[0]
	key = pygame.key.get_pressed()
	if key[pygame.K_d] == True:
		direction = 1
	elif key[pygame.K_a] == True:
		direction = -1
	else: direction = 0

	accel = (player_force * direction) - resistance
	velocity_x +=accel
	resistance = 0.75 * velocity_x
	if abs(velocity_x) < 0.001:
		velocity_x = 0

	if key[pygame.K_SPACE] == True:
		if falling < 3:
			velocity_y = jump_force

	if pygame.sprite.spritecollide(player,terrain_grp, False) == []:
		velocity_y -=g_field_strength
		falling +=3

	for sprite in terrain_grp:
		sprite.rect.move_ip(-velocity_x, 0)
		sprite.rect.move_ip(0,velocity_y)
		
	if not pygame.sprite.spritecollide(player,terrain_grp, False) == []:
		if falling > 0:
			falling = 0
			velocity_y = 0

		for sprite in terrain_grp:
			sprite.rect.move_ip(0,1)
	
	if not pygame.sprite.spritecollide(player,terrain_grp, False) == []:
		for sprite in terrain_grp:
			sprite.rect.move_ip(velocity_x,0)

#start up inventory & relevant buttons 
inventory_grp = pygame.sprite.Group()
inventory = Sprite((600, 400), (704,756), "img/Inventory.png", None)
inventory_grp.add(inventory)

inv_but = pygame.sprite.Group()
inv_but_close = Sprite((897, 73), (55,55), None, (160,160,160))
inv_but_howtoplay = Sprite((839, 73), (59,59), None, (160,160,160))
inv_hover_cover = Sprite((-100,-100), (72,72), "img/hover_inv.png", None)
inv_but.add(inv_but_close, inv_but_howtoplay, inv_hover_cover)

inv_items_grp = pygame.sprite.Group()
inv_items_move = pygame.sprite.Group()
combine = pygame.sprite.Group()

textsheet = Spritesheet("img/Text.png", (610,701))

def generate_message(message, pos, scale, gap, special_flags = None):
	if special_flags == "inv.man.digit":
		if not int(message) >= 10:
			message = " " + message 
			
	for character in message:
		if character == " ":
			inv_items = pygame.Surface((24,58), pygame.SRCALPHA)
			inv_items = Sprite((0,0), (24,58), None, None, inv_items)
		else:
			character_list_pos = characters_list.index(character)
			if character_list_pos <= 25:
				group = 0
			elif character_list_pos <= 51:
				group = 1
			else: group = 2

			column = (character_list_pos - group * 26 + 1)%9
			row = (character_list_pos - group *26 + 1)//9 + 1
			if column == 0:
				column = 9
				row -= 1

			inv_items = Spritesheet.get_image(textsheet, (14+ 67*(column - 1), 8+ 235*group + 73*(row - 1)), (39, 58), (0, 0), (39,58))
		combine.add(inv_items)
	
	inv_items = Spritesheet.combine_images(combine, pos, scale, gap)
	inv_items = Sprite.convert_colour(inv_items, (0,0,0), (255,255,255))
	combine.empty()
	return inv_items

clicked = False
key_name = ""
long_click = 0
def inventory_def():
	global clicked
	global long_click
	mouse_pos = pygame.mouse.get_pos() 
	inventory_no, slot_info = inventory_mod.inv.inventory_def(key_name, mouse_pos)
	if inventory_no == 1:

		if not (slot_info[1:3]) == mouse_pos:
			inv_hover_cover.update_pos((slot_info[1], slot_info[2]))

		if not inventory_mod.update_slots == []:
			for update_count in inventory_mod.update_slots:
				existing_sprite = None
				slot = update_count[0]
				slot_coordinates = inventory_mod.inventory_list_slots[slot-1][0], inventory_mod.inventory_list_slots[slot-1][1]

				if update_count[0] == 0:
					if update_count[3] == 1:
						for items in inv_items_move:
							if items.get_remarks() == "slot0_block":
								inv_items_move.sprites()[0].update_pos(mouse_pos)
							if items.get_remarks() == "slot0_count":
								inv_items_move.sprites()[1].update_pos((mouse_pos[0] + 9, mouse_pos[1] + 17))
							
				if update_count[1] == 1:
					if not slot == 0:
						for items in inv_items_grp:
							if items.rect.center == (slot_coordinates):
								items.kill()
					else:
						for items in inv_items_move:
							if items.get_remarks() == "slot0_block":
								items.kill()

					if not inventory_mod.inventory_items[slot][0] == None:
						if slot == 0:
							inv_items = Sprite(mouse_pos, (70,70), "img/inv/" + inventory_mod.inventory_items[0][0] + ".png", None, None, "slot0_block")		
							inv_items_move.add(inv_items)
						else:
							inv_items = Sprite(slot_coordinates, (62,62), "img/inv/" + inventory_mod.inventory_items[slot][0] + ".png" , None)
							inv_items_grp.add(inv_items)
							
					
				if update_count[2] == 1:
					if not slot == 0:
						for items in inv_items_grp:
							if items.rect.center == (slot_coordinates[0] + 9, slot_coordinates[1] + 17):
								items.kill()
					else:
						for items in inv_items_move:
							if items.get_remarks() == "slot0_count":
								items.kill()

					if inventory_mod.inventory_items[slot][1] >= 2:
						inv_items = generate_message(str(inventory_mod.inventory_items[slot][1]), (slot_coordinates[0] + 9, slot_coordinates[1] + 17), 0.55, 0, "inv.man.digit")
						if slot == 0:
							inv_items.change_size(None, 1.12)
							inv_items.update_pos((mouse_pos[0] + 9, mouse_pos[1] + 17))
							inv_items.add_remarks("slot0_count")
							inv_items_move.add(inv_items)

						else: inv_items_grp.add(inv_items)
		
		inventory_mod.update_slots = []
		if pygame.mouse.get_pressed(3)[0] == True:
			if clicked == False:
				if pygame.key.get_pressed()[pygame.K_LSHIFT] == True:
					inventory_mod.inv.shift_click(None, slot_info[0])
				else:
					inventory_mod.inv.left_click(None, slot_info[0])
				clicked = True	
				print(slot_info, inventory_mod.search_results)
			else: long_click += 1	

		if pygame.mouse.get_pressed(3)[2] == True:
			if clicked == False:
				if pygame.key.get_pressed()[pygame.K_LSHIFT] == True:
					inventory_mod.inv.shift_click(None, slot_info[0])
				else:
					inventory_mod.inv.right_click(None, slot_info[0])
				clicked = True
			else: long_click += 1

		if clicked == False: long_click = 0
		if long_click > 0:
			inventory_mod.inv.long_click_item(pygame.mouse.get_pressed(3), long_click)

		if not inventory_mod.inventory_items[0] == [None, 0]:
			if len(inv_items_move) == 0:
				inventory_mod.update_slots.append([0,1,1,0])
			inventory_mod.update_slots.append([0,0,0,1])
			
		elif not len(inv_items_move) == 0:
			for item in inv_items_move:
				item.kill()

		if pygame.mouse.get_pressed(3) == (False, False, False):
			clicked = False

		layered_group.add(inventory, layer= 2)
		layered_group.add(inv_but, layer = 3)
		layered_group.add(inv_items_grp, layer = 4) 
		layered_group.add(inv_items_move, layer = 5)

	else: 
		layered_group.remove(inventory, inv_but, inv_items_grp, inv_items_move)
		
	action = Sprite.button_click(inv_but.sprites()[0], 0, 120)
	if action  == True:
		inventory_mod.inventory_no = 0
	Sprite.button_click(inv_but.sprites()[1], 0, 120)
	Sprite.button_click(inv_but.sprites()[2], 0, 220)

layered_group = pygame.sprite.LayeredUpdates()
layered_group.add(terrain_grp, layer=1)  
layered_group.add(player, layer=0)

while running:
	#print(pygame.mouse.get_pos())
	key = pygame.key.get_pressed()

	screen.fill((135,206,240))
	player_movement()
	inventory_def()

	layered_group.draw(screen)

	key_name = ""
	for event in pygame.event.get():
		if key[pygame.K_e] == True:
			key_name = "e"

		if event.type == pygame.QUIT:
			running = False


	pygame.display.flip()
	clock.tick(160)

pygame.quit()


