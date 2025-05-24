from ..utils.embeds import TimestampedEmbed;
from ..utils.economy import EconomyHelper;
from ..draw import draw_keno_grid, to_bytes;
import discord, typing, random, asyncio, time;

class ResettableTimer:
    def __init__(self, timeout: float): # timeout in seconds
        self.timeout = timeout;
        self._last_reset = time.monotonic();
        self._running = False;

    async def start(self, on_timeout):
        self._running = True;
        while self._running:
            now = time.monotonic();
            elapsed = now - self._last_reset;
            remaining = self.timeout - elapsed;
            if remaining <= 0:
                await on_timeout();
                break;

            await asyncio.sleep(min(remaining, 0.1));

    def reset(self):
        self._last_reset = time.monotonic();

    def stop(self):
        self._running = False;

    def is_running(self):
        return self.is_running;

class KenoView(discord.ui.View):
    message: discord.Message
    PAYOUT_TABLE = {
        1: {0: 0, 1: 8.75},
        2: {0: 0, 1: 1.52, 2: 3.48},
        3: {0: 0, 1: 1, 2: 2.10, 3: 20},
        4: {0: 0, 1: 0, 2: 2, 3: 9, 4: 81},
        5: {0: 0, 1: 0, 2: 1, 3: 3, 4: 35, 5: 310},
        6: {0: 0, 1: 0, 2: 1, 3: 2, 4: 10, 5: 60, 6: 700}
    }

    def __init__(self, cog, player: typing.Union[discord.User, discord.Member], wager: int, econ: EconomyHelper):
        super().__init__();
        self.cog = cog;
        self.player = player;
        self.wager = wager;
        self.econ = econ;

        self.chosen_squares = [];
        self.timer = ResettableTimer(3);
        self.timer_task = None;

    async def update_grid(self):
        values = [int(s) for s in self.chosen_squares];
        payouts = self.PAYOUT_TABLE.get(len(values));

        grid = draw_keno_grid(values, [], []);
        file = discord.File(to_bytes(grid), "grid.png");

        embed = TimestampedEmbed(
            title="<:keno_gem:1373312523117527041>",
        ).set_image(url="attachment://grid.png");
        
        if payouts:
            embed.add_field(name="Payout", value="\n".join(f"{k}<:keno_gem:1373312523117527041> - `x{v:.2f}`" for k, v in payouts.items()), inline=False);

        typing.cast(discord.ui.Select, self.children[0]).options = self.select_view.options;
        self.message = await self.message.edit(embed=embed, attachments=[file], view=self);

    @discord.ui.select(
        options=[discord.SelectOption(label=f"Slot {n}", value=str(n)) for n in range(1, 26)],
        placeholder="Choose your slots",
        min_values=1,
        max_values=6
    )
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer(ephemeral=True);

        if interaction.user != self.player:
            embed = TimestampedEmbed(
                title=":x:",
                description=f"This is not your game.",
            );
            await interaction.followup.send(embed=embed, ephemeral=True);
            return;

        self.chosen_squares = select.values;
        self.select_view = select;
        self.select_view.options = [discord.SelectOption(label=o.label, value=o.value, default=o.value in self.chosen_squares) for o in self.select_view.options];  

        if not self.timer_task or (self.timer_task and not self.timer_task.is_running()):
            self.timer_task = await self.timer.start(self.update_grid);
        else:
            self.timer.reset();

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green)
    async def submit(self, interaction: discord.Interaction, _):
        await interaction.response.defer(ephemeral=True);

        if interaction.user != self.player:
            embed = TimestampedEmbed(
                title=":x:",
                description=f"This is not your game.",
            );
            await interaction.followup.send(embed=embed, ephemeral=True);
            return;

        self.econ.remove_chips(self.wager, "WAGER");
        self.econ.user.total_bet += self.wager;
        self.econ.user.save();

        values = [int(s) for s in self.chosen_squares];
        _hash = self.cog.fair_random(self.player);
        rnd = random.Random(_hash); 

        winning_numbers = rnd.sample(range(1, 26), 6);
        svalues, swinning_numbers = set(values), set(winning_numbers);

        winnning_choosers = list(svalues & swinning_numbers);
        highlighted_choosers = list(svalues - swinning_numbers);
        lost_choosers = list(swinning_numbers - svalues);

        mult = PAYOUT_TABLE[len(values)][len(winnning_choosers)];

        embed = self.message.embeds[0];
        grid = draw_keno_grid(values, [], []);

        file = discord.File(to_bytes(grid), "grid.png");
        embed.description = "*Rolling...*";
        embed.set_image(url="attachment://grid.png");

        self.message = await self.message.edit(embed=embed, attachments=[file], view=self.cog.fairness_view);

        grid = draw_keno_grid(highlighted_choosers, lost_choosers, winnning_choosers);
        file = discord.File(to_bytes(grid), "grid.png");

        if mult > 0:
            winning = mult * self.wager;

            embed.description = f"You landed a `x{mult:.2f}` multiplier with {len(winnning_choosers)}<:keno_gem:1373312523117527041>!\nYou've earned `{winning}` chips.";
            embed.colour = discord.Colour.dark_green();

            self.cog.log_win(self.econ.user);
            self.econ.add_chips(winning);  
        else:
            embed.description = f"You landed a `x{mult:.2f}` multiplier with {len(winnning_choosers)}<:keno_gem:1373312523117527041>!\nYou lost.";
            embed.colour = discord.Colour.dark_red();
            self.cog.log_loss(self.econ.user); 

        embed.set_image(url="attachment://grid.png");
        await asyncio.sleep(6);
        self.message = await self.message.edit(embed=embed, attachments=[file]);