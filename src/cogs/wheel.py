from ..main import CustomBot;
from ..utils.embeds import TimestampedEmbed;
from ..utils.economy import EconomyHelper;
from ..utils.enums import ModeEnum;
from ..draw import draw_wheel, to_bytes, WheelDrawHelper;
from .game import GameCog;
import discord, asyncio;

class WheelCog(GameCog):
	def __init__(self, bot: CustomBot):
		super().__init__(bot, "wheel", 20, 100);

	@discord.app_commands.describe(wager="The amount of chips you are wagering.", mode="The difficulty of the wheel.")
	@discord.app_commands.command(description="Spin the wheel and win chips.")
	@discord.app_commands.choices()
	async def wheel(self, interaction: discord.Interaction, wager: int, mode: ModeEnum = ModeEnum.Easy):
		await interaction.response.defer(thinking=True);
		user, account = await self.background_checks(interaction, wager);

		if user and account:
			user.total_bet += wager;
			user.save();
			econ = EconomyHelper(account);
			econ.remove_chips(wager, "WAGER");

			_hex = self.fair_random(interaction.user);
			segment = self.weighted_random(_hex, mode.value);
			segment_angle = 360 / 16;
			center_angle = segment_angle * segment + segment_angle / 2;
			rotated = -(center_angle - 180) % 360;

			mult = WheelDrawHelper.get_values(mode)[segment]
			value = float(mult.lstrip("x"));

			gif = discord.File(f"./src/assets/wheels/wheel_{mode.name.lower()}.gif", "wheel.gif")
			embed = TimestampedEmbed(
				title=":wheel:"
			).set_image(url="attachment://wheel.gif");

			msg = await interaction.followup.send(embed=embed, file=gif, view=self.fairness_view, wait=True);
			await asyncio.sleep(8);

			winning = int(wager * value);
			if winning > 0:
				embed.description = f"You landed on `{mult}`, earning you `{winning}` chips!"
				embed.colour = discord.Colour.dark_green();

				econ.user.total_won += winning;
				self.log_win(econ.user);
				econ.add_chips(winning);
			else:
				embed.description = f"You landed on `x0.0`, thus losing your wager."
				embed.colour = discord.Colour.dark_red();
				self.log_loss(econ.user);
			econ.user.save();

			static = draw_wheel(rotated, 400, mode);
			staticb = to_bytes(static);
			staticf = discord.File(staticb, "wheel.png");

			embed.set_image(url="attachment://wheel.png");
			await msg.edit(embed=embed, attachments=[staticf]);

async def setup(bot: CustomBot):
	await bot.add_cog(WheelCog(bot));