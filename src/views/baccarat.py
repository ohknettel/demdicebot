from ..utils.embeds import TimestampedEmbed;
import discord;

class BaccaratView(discord.ui.View):
    message: discord.Message;

    def __init__(self, user, game):
        super().__init__(timeout=30);
        self.user = user;
        self.game = game;
        
        self.add_item(BetButton(label="Player", bet="player", style=discord.ButtonStyle.red));
        self.add_item(BetButton(label="Tie", bet="tie", style=discord.ButtonStyle.green));
        self.add_item(BetButton(label="Banker", bet="banker", style=discord.ButtonStyle.blurple));

class BetButton(discord.ui.Button):
    def __init__(self, label, bet, style):
        super().__init__(label=label, style=style);
        self.bet = bet;

    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True);
        assert(self.view);

        if interaction.user != self.view.user:
            embed = TimestampedEmbed(
                title=":x:",
                description=f"This is not your game."
            );
            await interaction.followup.send(embed=embed, ephemeral=True);
            return;

        for child in self.view.children:
            if isinstance(child, discord.ui.Button) or issubclass(child, discord.ui.Button):
                child.disabled = True;
        self.view.timeout = None;

        await self.view.message.edit(view=self.view);

        self.view.game.bet = self.bet;
        await self.view.game.start(self.view.message);

class PlayerDecisionView(discord.ui.View):
    message: discord.Message

    def __init__(self, game):
        super().__init__(timeout=30);
        self.game = game;

        self.add_item(PlayerActionButton(label="Draw", action="draw", style=discord.ButtonStyle.success));
        self.add_item(PlayerActionButton(label="Stand", action="stand", style=discord.ButtonStyle.secondary));

class PlayerActionButton(discord.ui.Button):
    def __init__(self, label, action, style):
        super().__init__(label=label, style=style);
        self.action = action;

    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True);
        assert(self.view);

        if interaction.user != self.view.game.player:
            embed = TimestampedEmbed(
                title=":x:",
                description=f"This is not your game.",
            );
            await interaction.followup.send(embed=embed, ephemeral=True);
            return;
        await self.view.message.delete();
        
        if self.action == "draw":
            await self.view.game.player_draw();
        else:
            await self.view.game.player_stand();