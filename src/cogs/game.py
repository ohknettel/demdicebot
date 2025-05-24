from ..main import CustomBot;
from ..utils.embeds import TimestampedEmbed;
from ..utils import fairness, encryption, logging;
from ..models.account import User, Account;
from discord.ext.commands import Cog;
import discord, json, typing;

class FairnessView(discord.ui.View):
	def __init__(self, server_seed, client_seed, nonce):
		super().__init__();
		self.server_seed = server_seed;
		self.client_seed = client_seed;
		self.server_hash = fairness.hashseed(server_seed);
		self.nonce = nonce;

	@discord.ui.button(label="Fairness", emoji="⚖", style=discord.ButtonStyle.gray)
	async def _fairness(self, interaction: discord.Interaction, _):
		await interaction.response.defer(ephemeral=True);
		embed = TimestampedEmbed(
			colour=discord.Colour.dark_grey(),
			title=":scales:"
		).add_field(name="Server seed hash", value=self.server_hash, inline=False) \
		.add_field(name="Client seed", value=self.client_seed, inline=False) \
		.add_field(name="Nonce", value=str(self.nonce), inline=False)
		await interaction.followup.send(embed=embed, ephemeral=True);

class GameCog(Cog):
	def __init__(self, bot: CustomBot, name: str, min_wager: int, max_wager: int):
		self.bot = bot;
		self.name = name;
		self.min_wager = min_wager;
		self.max_wager = max_wager;

		self.nonce = {}
		self.nonce[self.name] = {}

	async def background_checks(self, interaction: discord.Interaction, wager: int):
		if not interaction.response.is_done():
			await interaction.response.defer(thinking=True);

		user_db, _ = User.get_or_create(uid=encryption.encrypt_id(interaction.user.id));
		acc = Account.get_or_none(user=user_db);

		if not acc:
			embed = TimestampedEmbed(
			    colour=discord.Colour.red(),
			    title=":x:",
			    description=f"You do not have an account."
			)
			await interaction.followup.send(embed=embed);
			return (None, None);
		elif acc.balance < wager:
			embed = TimestampedEmbed(
			    colour=discord.Colour.red(),
			    title=":x:",
			    description=f"Insufficient balance. Please top-up with chips."
			)
			await interaction.followup.send(embed=embed);
			return (None, None);
		elif self.min_wager > wager:
			embed = TimestampedEmbed(
			    colour=discord.Colour.red(),
			    title=":x:",
			    description=f"Minimum wager is `{self.min_wager}` chips. Please increase your wager."
			)
			await interaction.followup.send(embed=embed);
			return (None, None);
		elif wager > self.max_wager:
			embed = TimestampedEmbed(
			    colour=discord.Colour.red(),
			    title=":x:",
			    description=f"Maximum wager is `{self.max_wager}` chips. Please decrease your wager."
			)
			await interaction.followup.send(embed=embed);
			return (None, None);

		logging.logger.info(f"User [{user_db.uid}] is playing a game of {self.name} on a wager of {wager} chips")
		user_db.games_played += 1;
		user_db.save();
		return (user_db, acc);

	def log_win(self, user: User):
		user.games_won += 1;
		user.save();
		logging.logger.info(f"User [{user.uid}] has won a game of {self.name}");

	def log_loss(self, user: User):
		user.games_lost += 1;
		user.save();
		logging.logger.info(f"User [{user.uid}] has lost a game of {self.name}");

	def fair_random(self, user: typing.Union[discord.User, discord.Member]):
		self.client_seed = fairness.genseed(8);
		self.server_seed = fairness.genseed();
		self.server_hash = fairness.hashseed(self.server_seed);

		nonce = self.nonce[self.name].get(user.id, 0);
		result = fairness.genrandom(self.server_seed, self.client_seed, str(nonce));

		self.fairness_view = FairnessView(self.server_seed, self.client_seed, nonce)
		self.nonce[self.name][user.id] = nonce + 1;
		return result;

	def weighted_random(self, hashed: str, weight_variable):
		try:
			weights_d = json.load(open("./src/cogs/weights.json"))
			weights = weights_d.get(weight_variable, []);
		except json.JSONDecodeError:
			return int(fairness.genrandom(self.server_seed, self.client_seed, "0"), 16) % 1; # fallback

		if len(weights) > 0:
			_float = int(hashed, 16) / (2**256 - 1);
			total_weight = sum(weights);
			threshold = _float * total_weight;
			cumulative = 0;
			for i, weight in enumerate(weights):
				cumulative += weight
				if threshold < cumulative:
					return i 
			return len(weights) - 1; # fallback
		else:
			return int(fairness.genrandom(self.server_seed, self.client_seed, "0"), 16) % 1; # fallback

async def setup(_):
    pass;