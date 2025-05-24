from ..main import CustomBot;
from ..utils.embeds import TimestampedEmbed;
from ..utils.economy import EconomyHelper;
from ..views.keno import KenoView;
from ..draw import draw_keno_grid, to_bytes;
from .game import GameCog;
import discord;

class KenoCog(GameCog):
    def __init__(self, bot: CustomBot):
        super().__init__(bot, "keno", 50, 200);

    @discord.app_commands.describe(wager="The amount of chips you are wagering.")
    @discord.app_commands.command(description="Play a game of Keno.")
    async def keno(self, interaction: discord.Interaction, wager: int):
        await interaction.response.defer(thinking=True);
        user, account = await self.background_checks(interaction, wager);
        grid = draw_keno_grid([], [], []);
        file = discord.File(to_bytes(grid), "grid.png");

        embed = TimestampedEmbed(
            title="<:keno_gem:1373312523117527041>",
        ).set_image(url="attachment://grid.png");

        if user and account:
            econ = EconomyHelper(account);
        
            view = KenoView(self, interaction.user, wager, econ);
            msg = await interaction.followup.send(embed=embed, view=view, files=[file], wait=True);
            view.message = msg;

async def setup(bot: CustomBot):
    await bot.add_cog(KenoCog(bot));
