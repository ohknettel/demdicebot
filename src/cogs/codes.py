from ..main import CustomBot;
from ..utils.embeds import TimestampedEmbed;
from ..models.codes import Code;
from discord.ext.commands import Cog;
from dateparser import parse;
from datetime import datetime;
import discord, typing;

class CodesCog(Cog):
	def __init__(self, bot: CustomBot):
		self.bot = bot;

	group = discord.app_commands.Group(name="codes", description="Manage and display gift codes.")

	@discord.app_commands.describe(code_content="The code itself.",
		code_value="How many chips are to be added when the code is used.",
		code_valid_from="Duration at which from when the code is valid for use.",
		code_valid_to="Duration at the code will expire.",
		code_max_uses="How many uses the code supplies. Use -1 to indicate infinite uses.")
	@discord.app_commands.checks.has_permissions(administrator=True)
	@group.command(description="Creates a new code.")
	async def new(self, interaction: discord.Interaction,
		code_content: str,
		code_value: int,
		code_valid_from: str,
		code_valid_to: typing.Optional[str],
		code_max_uses: typing.Optional[int] = -1):
		await interaction.response.defer(thinking=True);

		code = Code.get_or_none(content=code_content);
		if code:
			embed = TimestampedEmbed(
				colour=discord.Colour.red(),
				title=":x:",
				description=f"Code `{code_content}` already exists."
			)
			await interaction.followup.send(embed=embed);
			return;
		else:
			valid_from = parse(code_valid_from);
			if not valid_from:
				embed = TimestampedEmbed(
					colour=discord.Colour.red(),
					title=":x:",
					description=f"Invalid duration for `code_valid_from`. Please input a valid duration such as `2025-01-01 03:00 PM` or a relative duration such as `in 4 hours`."
				)
				await interaction.followup.send(embed=embed);
				return;
			valid_from_fmt = valid_from.strftime("%A, %d %B, %Y at %H:%M:%S %p")

			valid_to = None;
			if code_valid_to:
				valid_to = parse(code_valid_from);
				if not valid_to:
					embed = TimestampedEmbed(
						colour=discord.Colour.red(),
						title=":x:",
						description=f"Invalid duration for `code_valid_from`. Please input a valid duration such as `2025-01-01 03:00 PM` or a relative duration such as `in 4 hours`."
					)
					await interaction.followup.send(embed=embed);
					return;
			valid_to_fmt = valid_to.strftime("%A, %d %B, %Y at %H:%M:%S %p") if valid_to else None;

			code = Code.create(
				content=code_content,
				valid_from=valid_from,
				valid_until=valid_to,
				value=code_value,
				max_uses=code_max_uses
			);

			embed = TimestampedEmbed(
				colour=discord.Colour.green(),
				title=":white_check_mark:",
				description=f"Created new code successfully.\n## Details"
			) \
			.add_field(name="Code", value=f"||`{code_content}`||", inline=False) \
			.add_field(name="Valid from", value=valid_from_fmt, inline=False) \
			.add_field(name="Value", value=f"`{code_value}` chips", inline=False) \
			.add_field(name="Max uses", value="Infinite" if code_max_uses == -1 else f"{code_max_uses} use(s)", inline=False);

			if valid_to_fmt:
				embed.insert_field_at(2, name="Valid until", value=valid_to_fmt, inline=False);

			await interaction.followup.send(embed=embed);

	@discord.app_commands.describe(show_invalid_codes="Whether to show invalid codes in the listings.")
	@discord.app_commands.checks.has_permissions(administrator=True)
	@group.command(description="List all valid codes.")
	async def list(self, interaction: discord.Interaction, show_invalid_codes: typing.Optional[bool] = False):
		await interaction.response.defer(thinking=True);

		codes = Code.select()
		if not show_invalid_codes:
			codes = list(codes.where((datetime.now() < Code.valid_until) | (Code.valid_until >> None)));
		else:
			codes = list(codes)

		for code in codes:
			print(code.content, code.uses.count());

async def setup(bot: CustomBot):
	await bot.add_cog(CodesCog(bot));