import sys
import pygame


inventory_list_slots = []
inventory_items = []
list_of_items = [] 

#(x, y, remarks)
for y in range(4):
	for x in range(9):
		if y == 0:
			inventory_list_slots.append([312 + x * 72, 722, None])
		elif not y == 0:
			inventory_list_slots.append([312 + x * 72, 422 + y * 72, None])

inventory_list_slots.extend([[312, 178, "armour_helmet"], [312, 250, "armour_chestplate"], [312, 322, "armour_leggings"], [312, 394, "armour_boots"]])
inventory_list_slots.append([600, 394, "offhand"])

for y in range(2):
	for x in range(2):
		inventory_list_slots.append([668 + x * 72, 222 + y * 72, "crafting_input"])

inventory_list_slots.append([892, 254, "crafting_output"])

for i in range(len(inventory_list_slots) + 1):
	inventory_items.append([None, 0])

inventory_cooldown = 0
inventory_no = 0
#(slot, change_costume, change_item_count)
#0(slot, change_costume, change_item_count, change_pos)
update_slots = []
crafting_slots = [] #[slot_no, crafting_slot_no]
search_results = []
crafting_mode = False

class inv():

	def mouse_get(pos):
		inv.mouse_x = pos[0]
		inv.mouse_y = pos[1]

	def hover_slot():
		slot_info = 0
		for slot in inventory_list_slots:

			slot_no = inventory_list_slots.index(slot) + 1
			item_name = inventory_items[slot_no][0]
			item_count = inventory_items[slot_no][1]
	
			if slot[0] - 35 < inv.mouse_x < slot[0] + 35 and slot[1] - 35 < inv.mouse_y < slot[1] + 35:
				slot_info = slot_no, slot[0], slot[1], item_name, item_count, slot[2]

		if slot_info == 0:
			return((0, inv.mouse_x, inv.mouse_y, None, 0, "out_of_bounds"))

		else: return(slot_info)

	def inventory_def(key, pos):
		global inventory_cooldown
		global inventory_no
		inv.mouse_get((0,0))
		if inventory_cooldown == 0:
			if key == "e":
				inventory_cooldown = 20
				if inventory_no == 0:
					inventory_no = 1

				elif inventory_no == 1:
					inventory_no = 0

		else: inventory_cooldown -= 1

		if inventory_no == 1:
			inv.mouse_get(pos)

		slot_info = inv.hover_slot()
		return inventory_no, slot_info

	def slot_find(item_name, item_count, type = None):
		if type == None:
			start, end, priority = 1, 36, None
		elif type == "shift_hotbar":
			start, end, priority = 10, 36, "armour"
		elif type == "shift_inventory":
			start, end, priority = 1, 9, "armour"

		found = False
		if priority == "armour":
			for slot, item in enumerate(inventory_items[37:42]):
				suitable = inv.suitable_slot(slot + 37, item[0])
				if suitable == True and item[0] in (item_name, None) and item[1] < 64:
					slot_dest = slot + 37
					found = True
					break

		if found == False:
			for slot, item in enumerate(inventory_items[start:end+1]):
				if item[0] == item_name and item[1] < 64:
					slot_dest = slot + start 
					found = True
					break

		if found == False:
			for slot, item in enumerate(inventory_items[start:end+1]):
				if item == [None, 0]:
					slot_dest = slot + start
					found = True
					break

		remaining = item_count
		if found == True:
			inventory_items[slot_dest][0] = item_name
			new_count = inventory_items[slot_dest][1] + item_count
			if new_count > 64:
				remaining = new_count - 64
				inventory_items[slot_dest][1] = 64
				found, remaining = inv.slot_find(item_name, remaining, type)
			else: 
				inventory_items[slot_dest][1] = new_count
				remaining = 0
			update_slots.append([slot_dest, 1, 1, 0])

		return found, remaining

	def pick_up_item(item, item_count, slot_no = None):
		if not slot_no == None and inventory_items[slot_no] == [None, 0]:
			inventory_items[slot_no] = [item, item_count]
			update_slots.append([slot_no, 1, 1, 0])
		else:
			found, remaining = inv.slot_find(item, item_count)

	def zero_check(slot_dest):
		if inventory_items[slot_dest][1] == 0:
			inventory_items[slot_dest][0] = None
			update_slots.append([slot_dest, 1, 0, 0])


	def left_click(mouse_pos, slot_dest):
		suitable = inv.suitable_slot(slot_dest, inventory_items[0][0])
		if suitable == True:
			if mouse_pos:
				inv.mouse_get(mouse_pos)
				slot_dest = inv.hover_slot()[0]
			
			if inventory_items[slot_dest][0] in (None, inventory_items[0][0]) and inventory_items[slot_dest][1] < 64:
				inventory_items[slot_dest][0] = inventory_items[0][0]
				inventory_items[slot_dest][1] += inventory_items[0][1]

				if inventory_items[slot_dest][1] > 64:
					inventory_items[0][1] = inventory_items[slot_dest][1] - 64
					inventory_items[slot_dest][1] = 64
				else: inventory_items[0] = [None, 0]

			else:
				swap_temp = inventory_items[slot_dest]
				inventory_items[slot_dest] = inventory_items[0]
				inventory_items[0] = swap_temp
				swap_temp = 0
			update_slots.extend([[slot_dest, 1, 1, 0], [0, 1, 1, 0]])

			if inventory_list_slots[slot_dest - 1][2] == "crafting_input":
				crafting.craft_mode()
				if crafting_mode == True:
					crafting.item_search()
					crafting.check_for_match([2,2])

		if not slot_dest == 0:
			if inventory_list_slots[slot_dest - 1][2] == "crafting_output":
				crafting.crafting_output()

				
	def right_click(mouse_pos, slot_dest):
		suitable = inv.suitable_slot(slot_dest, inventory_items[0][0])
		if suitable == True:

			if inventory_items[0] == [None, 0]:
				count = inventory_items[slot_dest][1]
				inventory_items[slot_dest][1] = count//2
				inventory_items[0] = [inventory_items[slot_dest][0], count - count//2]
				update_slots.extend([[slot_dest, 0, 1, 0], [0, 1, 1, 0]])

			elif inventory_items[slot_dest][0] in (None, inventory_items[0][0]) and inventory_items[slot_dest][1] < 64:
				if inventory_items[slot_dest] == [None, 0]:
					inventory_items[slot_dest][0] = inventory_items[0][0]

				inventory_items[slot_dest][1] += 1
				inventory_items[0][1] -= 1
				update_slots.extend([[slot_dest, 1, 1, 0],  [0, 1, 1, 0]])

			elif not inventory_items[slot_dest] == [None, 0] and not inventory_items[slot_dest][0] == inventory_items[0][0]:
				inv.left_click(None, slot_dest)
				
			inv.zero_check(slot_dest)
			inv.zero_check(0)

			if inventory_list_slots[slot_dest - 1][2] == "crafting_input":
				crafting.craft_mode()
				if crafting_mode == True:
					crafting.item_search()
					crafting.check_for_match([2,2])

		if not slot_dest == 0:
			if inventory_list_slots[slot_dest - 1][2] == "crafting_output":
				crafting.crafting_output()

	def shift_click(mouse_pos, init_slot):
		if init_slot < 10:
			found, remaining = inv.slot_find(*inventory_items[init_slot], "shift_hotbar")
		elif init_slot < 37:
			found, remaining = inv.slot_find(*inventory_items[init_slot], "shift_inventory")
		else:
			found, remaining = inv.slot_find(*inventory_items[init_slot])
		
		if remaining == 0:
			inventory_items[init_slot] = [None, 0]
		else: inventory_items[init_slot][1] = remaining

		update_slots.append([init_slot, 1, 1, 0])


	def update_slot(slot_no, new_item, new_item_count):
		if new_item:
			inventory_items[slot_no][0] = new_item
			update_slots.append([slot_no, 1, 0, 0])
		if new_item_count:
			inventory_items[slot_no][1] = new_item_count
			update_slots.append([slot_no, 0, 1, 0])


	def suitable_slot(slot_dest, item_name):
		if inventory_list_slots[slot_dest - 1][2] in (None, "crafting_input", "offhand"):
			return True
		else: return False


	def long_click_item(mouse_buttons, long_click):
		pass

class crafting():
	def define_slots():
		global crafting_slots
		for slot in inventory_list_slots:
			if slot[2] == "crafting_input":
				crafting_slots.append(inventory_list_slots.index(slot) + 1)
			elif slot[2] == "crafting_output":
				crafting_slots.insert(0, inventory_list_slots.index(slot) + 1)
		
	def craft_mode():
		global crafting_mode
		crafting_mode = False
		for item in crafting_slots:
			if not inventory_items[item] == [None, 0]:
				crafting_mode = True
				break
		if crafting_mode == False:
			global search_results
			search_results = []
		

	def item_search():
		global search_results
		search_results = []
		input_items = []
		for item in inventory_items[crafting_slots[1]: crafting_slots[-1]+1]:
			if not item == [None, 0] and not (item[0] in input_items):
				input_items.append(item[0])

		for item in input_items:
			for key, value in crafting_recipes.items():
				if item in value[0]:					
					search_results.append([key, value[1], value[2]])
					

	def check_for_match(crafting_area):
		input_pos_list = []
		for slot, input_item in enumerate(inventory_items[crafting_slots[1]: crafting_slots[-1]+1]):
			if not input_item == [None, 0]:
				input_pos_list.append([slot%2 + 1, slot//2 + 1, slot + crafting_slots[1]])

		if len(input_pos_list) > 0:
			min_x, min_y, max_x, max_y = 999, 999, 0, 0
			for pos in input_pos_list:
				if pos[0] < min_x: 
					min_x = pos[0]
				if pos[0] > max_x:
					max_x = pos[0]
				if pos[1] < min_y:
					min_y = pos[1]
				if pos[1] > max_y:
					max_y = pos[1]
			input_combi_area = [max_x - min_x +1, max_y - min_y + 1]
			input_combi_items = []
			input_combi_slots = []
			for y in range(input_combi_area[1]):
				for x in range(input_combi_area[0]):
					crafting_slot_no = x + min_x + (y + min_y - 1)*crafting_area[1]
					input_combi_items.append(inventory_items[crafting_slots[crafting_slot_no]][0])
					input_combi_slots.append(crafting_slot_no)

			for result in search_results:
				if result[1] <= crafting_area and input_combi_area == result[1]:

					output_item, recipe_area, output_item_count = result 
					if input_combi_items == crafting_recipes[output_item][0]:
						inventory_items[crafting_slots[0]] = [output_item, output_item_count]
						update_slots.append([crafting_slots[0], 1, 1, 0])
						print(input_combi_slots)


	def crafting_output():
		crafting.craft_mode()
		if crafting_mode == True:
			if inventory_items[0][0] in (None, inventory_items[crafting_slots[0]][0]):
				if inventory_items[0][1] + inventory_items[crafting_slots[0]][1] <= 64:

					inventory_items[0][0] = inventory_items[crafting_slots[0]][0]
					inventory_items[0][1] += inventory_items[crafting_slots[0]][1]

					for slot, item in enumerate(crafting_recipes["Sticks"][0]):
						if not item == None:
							inventory_items[crafting_slots[slot+1]][1] -= 1
							update_slots.append([crafting_slots[slot+1], 1, 1, 0])
							inv.zero_check(crafting_slots[slot+1])
							print(inventory_items[crafting_slots[slot+1]])

					update_slots.extend([[0, 1, 1, 0]])



class crafting_manage():
	def recipe_combi(recipe_area, crafting_area):
		if recipe_area[0] <= crafting_area[0] and recipe_area[1] <= crafting_area[1]:
	
			combi_x = crafting_area[0] - recipe_area[0] + 1
			combi_y = crafting_area[1] - recipe_area[1] + 1

			return combi_x, combi_y

	def check_combi():
		#[42, 43, 44]
		#[45, 46, 47]
		#[48, 49, 50]
		#crafting_slots = [51, 42, 43, 44, 45, 46, 47, 48, 49, 50]
		input_pos_list = []
		for slot, input_item in enumerate(inventory_items[crafting_slots[1]: crafting_slots[-1]+1]):
			#if not input_item == [None, 0]:
				input_pos = [slot%2 + 1, slot//2 + 1]
				input_pos_list.append(input_pos)
		if len(input_pos_list) > 0:
			
			min_x, min_y, max_x, max_y = 999, 999, 0, 0
			for pos in input_pos_list:
				if pos[0] < min_x: 
					min_x = pos[0]
				if pos[0] > max_x:
					max_x = pos[0]
				if pos[1] < min_y:
					min_y = pos[1]
				if pos[1] > max_y:
					max_y = pos[1]
		
			input_area = [max_x - min_x +1, max_y - min_y + 1]
			

combi_no = crafting_manage.recipe_combi([3,3], [107,3])

crafting.define_slots()
crafting_recipes = {} #recipe, dimensions, output_item_count
crafting_recipes["Sticks"] = [["Oak_Planks", "Oak_Planks"], [2,1], 4]
crafting_recipes["test"] = [["Stone", "Stone"], [2,1], 4]


crafting_manage.check_combi()


inv.pick_up_item("Stone", 32)
inv.pick_up_item("Grass_Block", 17)
inv.pick_up_item("Oak_Planks", 320)
inv.pick_up_item("Sticks", 64)
