from ..main import CustomBot;
from ..utils.embeds import TimestampedEmbed, EmbedDescriptionResolver;
from ..utils.economy import EconomyHelper;
from ..views.baccarat import PlayerDecisionView, BaccaratView;
from ..draw import draw_baccarat_grid, to_bytes;
from .game import GameCog;
import discord, typing, random, itertools;

class BaccaratGame:
    def __init__(self, cog: GameCog, player: typing.Union[discord.User, discord.Member], wager: int, econ: EconomyHelper):
        self.cog = cog;
        self.player = player;
        self.econ = econ;
        self.bet = None;

        self.wager = wager;
        self.turns = 0;

        self.deck = self.generate_deck();
        self.player_hand, self.banker_hand = [self.deck[0], self.deck[1]], [self.deck[2], self.deck[3]];
        self.next_index = 4;
    
    def generate_deck(self):
        categories = ["D", "H", "S", "C"]; # D-iamonds, H-earts, S-pades and C-lubs
        values = ["A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K"];
        rand = random.Random(self.cog.fair_random(self.player));
        deck = [(x, y) for x, y in itertools.product(values, categories)];
        rand.shuffle(deck);
        return deck;

    def classify_card(self, card: "tuple[typing.Union[str, int], str]"):
        categories = {
            "D": "Diamonds",
            "H": "Hearts",
            "S": "Spades",
            "C": "Clubs"
        }

        face_cards = {
            "A": "Ace",
            "J": "Jack",
            "K": "King",
            "Q": "Queen"
        }
        
        value = face_cards[card[0]] if type(card[0]) == str else str(card[0]);
        category = categories[card[1]];
        return f"{value} of {category}"

    def calculate_hand(self, hand):
        accum = 0
        for card in hand:
            if card[0] not in [10, "J", "Q", "K"]:
                accum += 1 if card[0] == "A" else card[0];
        return accum % 10; 

    def display_grid(self):
        pcnames = [f"{t[0]}{t[1]}" for t in self.player_hand];
        bcnames = [f"{t[0]}{t[1]}" for t in self.banker_hand];

        grid = draw_baccarat_grid(pcnames, bcnames);
        return to_bytes(grid);

    async def start(self, message: discord.Message):
        self.player_total = self.calculate_hand(self.player_hand);
        self.banker_total = self.calculate_hand(self.banker_hand);
        self.turns += 1;

        self.econ.remove_chips(self.wager).add_bet(self.wager);

        file = discord.File(self.display_grid(), "grid.png");
        embed = TimestampedEmbed(
            title=":game_die:",
            description=""
        ).set_image(url="attachment://grid.png");

        self.message = await message.edit(embed=embed, attachments=[file], view=self.cog.fairness_view);

        if self.player_total >= 6:
            await self.player_stand();
        else:
            embed = TimestampedEmbed(
                title=":question_mark:",
                description=f"Do you wish to draw or stand for the player?",
            );

            decision_view = PlayerDecisionView(self);
            decision_msg = await self.message.reply(embed=embed, view=decision_view);
            decision_view.message = decision_msg;

    async def player_draw(self):
        self.turns += 1;
        card = self.deck[self.next_index];
        self.player_hand.append(card);
        self.next_index += 1;

        file = discord.File(self.display_grid(), "grid.png");

        embed = EmbedDescriptionResolver.from_embed(self.message.embeds[0]);
        embed.set_description(f"\n:red_circle: Player draws: `{self.classify_card(card)}`!");
        embed.set_image(url="attachment://grid.png")
        self.message = await self.message.edit(embed=embed, attachments=[file]);

        await self.player_stand();

    async def player_stand(self):
        self.player_total = self.calculate_hand(self.player_hand);
        self.banker_total = self.calculate_hand(self.banker_hand);

        banker_draws = False;
        if self.banker_total <= 2:
            banker_draws = True;
        elif self.banker_total == 3 and self.player_total != 8:
            banker_draws = True;
        elif self.banker_total == 4 and self.player_total in range(2,8):
            banker_draws = True;
        elif self.banker_total == 5 and self.player_total in range(4,8):
            banker_draws = True;
        elif self.banker_total == 6 and self.player_total in range(6,8):
            banker_draws = True;

        if banker_draws:
            self.turns += 1;
            card = self.deck[self.next_index];
            self.banker_hand.append(card);

            file = discord.File(self.display_grid(), "grid.png");

            embed = EmbedDescriptionResolver.from_embed(self.message.embeds[0]);
            embed.set_description(f"\n:blue_circle: Banker draws: `{self.classify_card(card)}`!");
            embed.set_image(url="attachment://grid.png")
            self.message = await self.message.edit(embed=embed, attachments=[file]);

        await self.finish_game();
    
    def determine_payout(self, won: bool) -> int:
        if won:
            if self.bet == "player":
                return self.wager;
            elif self.bet == "banker":
                return int(self.wager * 0.95);
            else:
                return int(self.wager * 8);
        else:
            return self.wager * -1;

    async def finish_game(self):
        file = discord.File(self.display_grid(), "grid.png");
        embed = EmbedDescriptionResolver.from_embed(self.message.embeds[0]);

        self.player_total = self.calculate_hand(self.player_hand);
        self.banker_total = self.calculate_hand(self.banker_hand);

        if self.player_total > self.banker_total:
            winner = "player"
        elif self.player_total < self.banker_total:
            winner = "banker"
        else:
            winner = "tie"

        if winner == self.bet:
            payout = self.determine_payout(True);
            self.cog.log_win(self.econ.user);
            self.econ.user.total_won += payout;

            embed.colour = discord.Colour.dark_green();
            if winner == "tie":
                embed.set_description(f"\n**It's a tie!** You bet on tie and won `{payout}` chips!");
            else:
                total = self.player_total if winner == "player" else self.banker_total;
                embed.set_description(f"\n**{winner.capitalize()} wins with a total of `{total}`!** You bet on {winner} and won `{payout}` chips!");
        else:
            self.cog.log_loss(self.econ.user);
            payout = self.determine_payout(False);

            embed.colour = discord.Colour.dark_red();
            if winner == "tie":
                embed.set_description(f"\n**It's a tie!** You bet on {self.bet} and lost.");
            else:
                total = self.player_total if winner == "player" else self.banker_total;
                embed.set_description(f"\n**{winner.capitalize()} wins with a total of `{total}`!** You bet on {self.bet} and lost.");
        
        if payout > 0:
            self.econ.add_chips(payout);

        embed.set_footer(text=f"Played in {self.turns} {'turns' if self.turns > 1 else 'turn'} | {embed.footer.text}");
        embed.set_image(url="attachment://grid.png");
        self.message = await self.message.edit(embed=embed, attachments=[file]);

class BaccaratCog(GameCog):
    def __init__(self, bot: CustomBot):
        super().__init__(bot, "baccarat", 50, 500);

    @discord.app_commands.describe(wager="The amount of chips you are wagering.")
    @discord.app_commands.command(description="Play a game of Baccarat.")
    async def baccarat(self, interaction: discord.Interaction, wager: int):
        await interaction.response.defer(thinking=True);
        user, account = await self.background_checks(interaction, wager);

        if user and account:
            econ = EconomyHelper(account);
            embed = TimestampedEmbed(
                title=":video_game:",
                description=f"You are playing Baccarat with a wager of `{wager}` chips.\nPlease select your bet.",
            )

            game = BaccaratGame(self, interaction.user, wager, econ);
            view = BaccaratView(interaction.user, game);

            msg = await interaction.followup.send(embed=embed, view=view, wait=True);
            view.message = msg;

async def setup(bot: CustomBot):
    await bot.add_cog(BaccaratCog(bot));