from ..main import CustomBot;
from ..utils.embeds import TimestampedEmbed;
from ..utils import encryption, economy;

from ..models.account import User, Account;
from ..models.codes import Code, CodeUsage;

from discord.ext.commands import Cog;
from datetime import datetime;
import discord, typing;

class AccountsCog(Cog):
	def __init__(self, bot: CustomBot):
		self.bot = bot;

	group = discord.app_commands.Group(name="accounts", description="Manage your casino accounts.")

	@discord.app_commands.describe(
		code="Gift code."
	)
	@group.command(description="Opens your account at the casino.")
	async def open(self, interaction: discord.Interaction, code: typing.Optional[str]):
		await interaction.response.defer(thinking=True);
		user, _ = User.get_or_create(uid=encryption.encrypt_id(interaction.user.id));

		account = Account.get_or_none(user=user);
		if account:
			embed = TimestampedEmbed(
				colour=discord.Colour.red(),
				title=":x:",
				description=f"You already have an account."
			)
			await interaction.followup.send(embed=embed);
			return;
		else:
			account = Account.create(user=user);
			msg = ""
			if code:
				if (code_obj := Code.get_or_none(content=code)):
					if CodeUsage.get_or_none(code=code_obj, user=user):
						msg += f"You have already used code `{code}`."
					else:
						if code_obj.max_uses and code_obj.max_uses != -1 \
						   and code_obj.uses.count() >= code_obj.max_uses:
							msg += f"Code `{code}` is no longer applicable for use."
						elif code_obj.valid_until and datetime.now() > code_obj.valid_until:
							msg += f"Code `{code}` has expired."
						else:
							economy.EconomyHelper(account).add_chips(60, f"Code used: {code}")
							CodeUsage.create(code=code_obj, user=user).save();
							msg += f"Successfully redeemed code `{code}` for `{code_obj.value}` chips."
				else:
					msg += f"Code `{code}` does not exist."

			account.save();

			embed = TimestampedEmbed(
				colour=discord.Colour.green(),
				title=":white_check_mark:",
				description=f"Created new account successfully. Welcome to the casino!"
			)
			if len(msg) > 0:
				embed.add_field(name="Additional Notes", value=msg, inline=False);

			await interaction.followup.send(embed=embed);

	@group.command(description="Close your account at the casino.")
	async def close(self, interaction: discord.Interaction):
		await interaction.response.defer(thinking=True);

		class ConfirmationView(discord.ui.View):
			message: discord.Message

			def __init__(self, user: typing.Union[discord.User, discord.Member]):
				super().__init__();
				self.user = user;

			@discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
			async def yes(self, interaction: discord.Interaction, _):
				await interaction.response.defer();

				user, _ = User.get_or_create(uid=encryption.encrypt_id(interaction.user.id));
				account = Account.get_or_none(user=user);

				if not account:
					embed = TimestampedEmbed(
						colour=discord.Colour.red(),
						title=":x:",
						description=f"You do not have an account."
					)
					await msg.edit(embed=embed, view=None);
					return;
				else:
					account.delete_instance();
					embed = TimestampedEmbed(
						colour=discord.Colour.green(),
						title=":white_check_mark:",
						description=f"Successfully deleted account. Thank you for playing at the casino!"
					)
					await msg.edit(embed=embed, view=None);

		embed = TimestampedEmbed(
			colour=discord.Colour.yellow(),
			title=":warning:",
			description=f"Are you sure you want to close your account?\nBy closing your account you acknowledge that:\n- you will **not** be able to play any games\n- you **can not** redeem your chips balance in the case you open an account again, as the account will be deleted and consequently,\n- **you will permanently lose all multipliers, chips and stats you have earned**"
		)

		confirm = ConfirmationView(interaction.user);
		msg = await interaction.followup.send(embed=embed, view=confirm, wait=True);
		confirm.message = msg;

	@discord.app_commands.command(description="View your statistics at the casino.")
	async def stats(self, interaction: discord.Interaction):
		await interaction.response.defer(thinking=True);
		user, _ = User.get_or_create(uid=encryption.encrypt_id(interaction.user.id));

		embed = TimestampedEmbed(
			title=":bar_chart:"
		) \
		.add_field(name="Total games played", value=f"{user.games_played} game{'s' if user.games_played != 1 else ''}", inline=False) \
		.add_field(name="Games won", value=f"{user.games_won} game{'s' if user.games_won != 1 else ''}", inline=False) \
		.add_field(name="Games lost", value=f"{user.games_lost} game{'s' if user.games_lost != 1 else ''}", inline=False) \
		.add_field(name="Total chips bet", value=f"{user.total_bet} chip{'s' if user.total_bet != 1 else ''}", inline=False) \
		.add_field(name="Total chips won", value=f"{user.total_won} chip{'s' if user.total_won != 1 else ''}", inline=False)

		earnings = max(user.total_won - user.total_bet, 0);
		embed.add_field(name="Chips earned", value=f"{earnings} chip{'s' if earnings != 1 else ''}", inline=False);
		embed.set_thumbnail(url=interaction.user.display_avatar.url);

		await interaction.followup.send(embed=embed);

async def setup(bot: CustomBot):
	await bot.add_cog(AccountsCog(bot));