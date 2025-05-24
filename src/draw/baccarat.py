from PIL import Image;
import os;

def draw_baccarat_grid(player_card_names, banker_card_names):
	scale = 1.15;
	card_gap = 10;
	card_default_height = 180;

	felt = Image.open("./src/assets/backgrounds/baccarat_bg.png").convert("RGBA");

	player_cards = [
		os.path.join("./src/assets/cards", f + ".png") for f in player_card_names
	];

	banker_cards = [
		os.path.join("./src/assets/cards", f + ".png") for f in banker_card_names
	];

	def outlined_alpha_composite(base, card, pos, outline_colour, outline_width):
		card = card.convert("RGBA");
		x, y = pos;

		for dx in range(-outline_width, outline_width + 1):
			for dy in range(-outline_width, outline_width + 1):
				if dx == 0 and dy == 0:
					continue;
				offset_pos = (x + dx, y + dy);
				tinted = Image.new("RGBA", card.size, outline_colour)
				tinted.putalpha(card.getchannel("A"));
				base.alpha_composite(tinted, dest=offset_pos)

		base.alpha_composite(card, dest=pos);

	def resize_card(path):
		card = Image.open(path).convert("RGBA");
		ratio = card_default_height * scale / card.height
		new_size = (int(card.width * ratio), int(card.height * ratio));
		card = card.resize(new_size, Image.Resampling.BOX);
		return card;

	def paste_cards(card_list, start_x, center_y):
		total_width = int(sum(card.width for card in card_list) + card_gap * scale * (len(card_list) - 1));
		current_x = start_x - total_width // 2
		for card in card_list:
			y = center_y - card.height // 2;
			outlined_alpha_composite(felt, card, (current_x, y), (193, 235, 142), 2);
			current_x += int(card.width + card_gap * scale);

	player_imgs = [resize_card(p) for p in player_cards]
	banker_imgs = [resize_card(p) for p in banker_cards]

	paste_cards(player_imgs, felt.width // 4, int(300 * scale))
	paste_cards(banker_imgs, 3 * felt.width // 4, int(300 * scale))

	return felt;