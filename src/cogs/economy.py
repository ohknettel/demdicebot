from ..main import CustomBot;
from ..models.account import Account, User;
from ..utils.embeds import TimestampedEmbed;
from ..utils import encryption, economy;
from discord.ext.commands import Cog;
import discord, typing;

class EconomyCog(Cog):
	def __init__(self, bot: CustomBot):
		self.bot = bot;

	@discord.app_commands.describe(
	    new_balance="The new balance to set.",
	    user="The user to set the balance for."
	)
	@discord.app_commands.checks.has_permissions(administrator=True)
	@discord.app_commands.command(description="Sets a user\'s chips balance.")
	async def set_balance(self, interaction: discord.Interaction, new_balance: int, user: typing.Optional[discord.User] = None):
		if not interaction.guild:
			await interaction.response.defer(ephemeral=True, thinking=True);
			await interaction.followup.send("This command only functions inside a guild.", ephemeral=True);
			return;
		
		await interaction.response.defer(thinking=True);
		_user = await interaction.guild.fetch_member((user or interaction.user).id);

		user_db, _ = User.get_or_create(uid=encryption.encrypt_id(_user.id));
		acc = Account.get_or_none(user=user_db);


		if not acc:
			embed = TimestampedEmbed(
				colour=discord.Colour.red(),
				title=":x:",
				description=f"User {_user.mention} does not have an account."
			)
			await interaction.followup.send(embed=embed);
			return;

		econ = economy.EconomyHelper(acc);
		econ.set_balance(new_balance);

		embed = TimestampedEmbed(
			title=":white_check_mark:",
			colour=discord.Colour.green(),
			description=f"Set {_user.mention}'s balance to {new_balance} chips."
		)
		await interaction.followup.send(embed=embed);

	@discord.app_commands.describe(user="The user you wish to view balance for.")
	@discord.app_commands.command(description="Display your or a user\'s balance.")
	async def balance(self, interaction: discord.Interaction, user: typing.Optional[discord.User] = None):
		await interaction.response.defer(thinking=True);
		_user = user or interaction.user;

		user_db, _ = User.get_or_create(uid=encryption.encrypt_id(_user.id));
		acc = Account.get_or_none(user=user_db);

		if not acc:
			subject = "You do" if _user == interaction.user else f"{_user.mention} does"
			embed = TimestampedEmbed(
				colour=discord.Colour.red(),
				title=":x:",
				description=f"{subject} not have an account."
			)
			await interaction.followup.send(embed=embed);
			return;
		else:
			owner = "Your" if _user == interaction.user else f"{_user.mention}'s"
			embed = TimestampedEmbed(
				title=":moneybag:",
				description=f"{owner} balance is `{acc.balance}` chips."
			).set_thumbnail(url=_user.display_avatar.url)
			await interaction.followup.send(embed=embed);


async def setup(bot: CustomBot):
	await bot.add_cog(EconomyCog(bot));

