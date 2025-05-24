from PIL import Image, ImageDraw, ImageFont;
from ..utils.enums import ModeEnum;
import math;

class WheelDrawHelper:
	@staticmethod
	def get_values(mode: ModeEnum):
		if mode == ModeEnum.Easy:
			return ["x2.0", "x0.0", "x1.5", "x0.0", "x2.5", "x0.0", "x1.5", "x0.0", "x2.0", "x0.0", "x1.5", "x0.0", "x3.0", "x0.0", "x1.5", "x0.0"];
		elif mode == ModeEnum.Medium:
			return ["x0.0", "x1.5", "x0.0", "x1.5", "x0.0", "x1.5", "x0.0", "x1.5", "x0.0", "x5.0", "x0.0", "x1.5", "x0.0", "x1.5", "x0.0", "x1.5"];
		else:
			return ["x0.0", "x1.5", "x0.0", "x1.0", "x0.0", "x1.5", "x0.0", "x1.0", "x0.0", "x7.0", "x0.0", "x1.0", "x0.0", "x1.5", "x0.0", "x1.0"];

	@staticmethod
	def get_edge_colour(mode: ModeEnum):
		if mode == ModeEnum.Easy:
			return "#5AFF91";
		elif mode == ModeEnum.Medium:
			return "#0096FF";
		else:
			return "#FA5F55";

def draw_wheel(angle: float, size: int = 400, mode: ModeEnum = ModeEnum.Easy):
	image = Image.new("RGBA", (size, size), (255, 255, 255, 0));
	draw = ImageDraw.Draw(image);

	center = (size // 2, size // 2);

	radius_outer = size // 2 - 40;

	labels = WheelDrawHelper.get_values(mode);
	edge_colour = WheelDrawHelper.get_edge_colour(mode);

	segments = len(labels);
	segment_angle = 360 / segments;

	for i in range(segments):
		start_angle = segment_angle * i + angle;
		end_angle = start_angle + segment_angle;

		predicate = (i % 2 == 0) if mode == ModeEnum.Easy else ((i + 1) % 2 == 0);
		draw.pieslice([10, 10, size - 10, size - 10], start_angle, end_angle, fill=edge_colour if predicate else "#FFFFFF", outline="#314641", width=4);
		draw.pieslice([25, 25, size - 25, size - 25], start_angle, end_angle, fill="#4b665e", outline="#314641", width=2);

		mid_angle = (start_angle + end_angle) / 2;
		theta = math.radians(mid_angle);
		label_radius = radius_outer - 40;
		label_x = center[0] + label_radius * math.cos(theta);
		label_y = center[1] + label_radius * math.sin(theta);

		try:
			font = ImageFont.truetype("BRITANIC.TTF", size=18);
		except:
			font = ImageFont.load_default();

		text = labels[i];
		text_img = Image.new("RGBA", (200, 100), (0, 0, 0, 0));
		text_draw = ImageDraw.Draw(text_img);
		text_size = text_draw.textbbox((0, 0), text, font=font);
		text_draw.text((0, 0), text, font=font);

		cropped = text_img.crop(text_size);
		rotated = cropped.rotate(-mid_angle+180, resample=Image.Resampling.BICUBIC, expand=True);

		pos = (
			int(label_x - rotated.width / 2),
			int(label_y - rotated.height / 2)
		)

		image.alpha_composite(rotated, dest=pos);

	draw.ellipse([center[0] - 35, center[1] - 35, center[0] + 35, center[1] + 35], fill="#314641");
	draw.ellipse([center[0] - 30, center[1] - 30, center[0] + 30, center[1] + 30], fill="#4b665e");
	draw.ellipse([center[0] - 20, center[1] - 20, center[0] + 20, center[1] + 20], fill="#abd883");

	draw.polygon([
		(30, center[1]),
		(0, center[1] - 10),
		(0, center[1] + 10)
	], fill="#ffb300", outline="#d32f2f", width=4);

	return image;

def draw_wheel_gif(frames=30):
	images = []

	for i in range(frames):
		angle = (360 / frames) * i * 4;
		img = draw_wheel(angle);
		images.append(img);

	return images;