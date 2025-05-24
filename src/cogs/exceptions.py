from ..main import CustomBot;
from ..utils.embeds import TimestampedEmbed;
from discord.ext.commands import Cog;
import discord, traceback;

class ExceptionsCog(Cog):
	def __init__(self, bot: CustomBot):
		self.bot = bot
		self.bot.tree.error(self.__dispatch_to_app_command_handler)

	async def __dispatch_to_app_command_handler(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
		self.bot.dispatch("app_command_error", interaction, error)

	@Cog.listener("on_app_command_error")
	async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
		if isinstance(error, discord.app_commands.MissingPermissions):
			embed = TimestampedEmbed(
				colour=discord.Colour.red(),
				title=":x:",
				description=f"You are not authorized to run this command."
			)

			await interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			if not interaction.response.is_done():
				await interaction.response.defer()

			embed = TimestampedEmbed(
				colour=discord.Colour.red(),
				title=":x:",
				description=f"```{error}```"
			)

			await interaction.followup.send(embed=embed)
			traceback.print_exception(None, error, None)

async def setup(bot: CustomBot):
	await bot.add_cog(ExceptionsCog(bot));