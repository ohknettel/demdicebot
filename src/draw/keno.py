from PIL import Image, ImageDraw, ImageFont;
import typing;

def draw_keno_grid(highlighted: typing.List[int], loss: typing.List[int], win: typing.List[int]):
	rows, cols = 5, 5;
	cell_height = 80;
	cell_width = 120;
	cell_padding = 6;

	width = cols * cell_width + (cols + 1) * cell_padding;
	height = rows * cell_height + (rows + 1) * cell_padding;

	img = Image.new("RGB", (width, height), color=(40, 60, 50));
	draw = ImageDraw.Draw(img);

	try:
		font = ImageFont.truetype("BRITANIC.TTF", size=24);
	except:
		font = ImageFont.load_default();

	gem = Image.open("./src/assets/icons/keno_gem.png").convert("RGBA");
	gem_size = 58;
	gem = gem.resize((gem_size, gem_size), Image.Resampling.LANCZOS);

	for row in range(rows):
		for col in range(cols):
			num = row * cols + col + 1;
			x = cell_padding + col * (cell_width + cell_padding);
			y = cell_padding + row * (cell_height + cell_padding);

			is_highlighted = num in highlighted;
			is_loss = num in loss;
			is_win = num in win;

			cell_radius = 8;

			if not is_loss and not is_win:
				cell_colour = (193, 235, 142) if is_highlighted else (67, 89, 83);
				draw.rounded_rectangle([x, y, x + cell_width, y + cell_height], radius=cell_radius, fill=cell_colour);

			if not (is_loss or is_win):
				border_colour = (139, 173, 133) if is_highlighted else (55, 75, 76);
				draw.rounded_rectangle([x, y, x + cell_width, y + cell_height], radius=cell_radius, outline=border_colour);
			else:
				border_colour = (79, 102, 95) if not is_win else (84, 107, 100);
				draw.rounded_rectangle([x, y, x + cell_width, y + cell_height], radius=cell_radius, outline=border_colour, width=3 if is_win else 2);

			cx = x + cell_width // 2;
			cy = y + cell_height // 2;
			if not is_win:
				r = 22;

				circle_colour = (165, 219, 102) if is_highlighted else ((236, 79, 91) if is_loss else (62, 81, 74));
				draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=circle_colour);
			else:
				gem_x = cx - gem_size // 2;
				gem_y = cy - gem_size // 2;
				img.paste(gem, (gem_x, gem_y), gem);

			text = str(num);
			bbox = draw.textbbox((0, 0), text, font=font);

			tw = bbox[2] - bbox[0];
			th = bbox[3] - bbox[1];

			fill = (49, 70, 65) if is_highlighted or is_win else (102, 121, 117);
			if is_loss:
				fill = (238, 238, 238);
			draw.text((cx - tw // 2, cy - th // 2 - 3), text, font=font, fill=fill);

	return img;