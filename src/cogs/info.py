from ..main import CustomBot;
from ..utils.embeds import TimestampedEmbed;
from discord.ext.commands import Cog;
import discord;

class InfoCog(Cog):
	def __init__(self, bot: CustomBot):
		self.bot = bot;

	@discord.app_commands.command(description="Displays information about the bot.")
	async def about(self, interaction: discord.Interaction):
		await interaction.response.defer(thinking=True);
		
		embed = TimestampedEmbed(
			title=":information_source: | About",
		)
		await interaction.followup.send(embed=embed);

async def setup(bot: CustomBot):
	await bot.add_cog(InfoCog(bot));