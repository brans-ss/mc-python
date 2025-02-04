#generate a message based on a spritesheet (the spritesheet has all the letters, numbers & some special characters)

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
