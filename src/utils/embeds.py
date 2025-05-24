from datetime import datetime, timezone;
import discord;

PURPLE = 0xab52c5;

class TimestampedEmbed(discord.Embed):
	def __init__(self, **kwargs):
		super().__init__(**kwargs);
		if not kwargs.get("colour"):
			self.colour = PURPLE;

		dt = datetime.now(timezone.utc);
		self.set_footer(text=dt.strftime("%I:%M %p UTC").lstrip("0"));

class EmbedDescriptionResolver(discord.Embed):
	@staticmethod
	def from_embed(embed: discord.Embed):
		return EmbedDescriptionResolver(*embed.to_dict());

	def set_description(self, description: str):
		self.description = (self.description or "") + description;
		return self;