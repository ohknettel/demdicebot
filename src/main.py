import sys, dotenv, asyncio, os, time;
dotenv.load_dotenv();
if sys.platform == "win32":
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy());

import discord, traceback;
from pathlib import Path;
from discord.ext.commands import Bot, ExtensionError;

from .models.base import database;
from .models.account import User, Account;
from .models.codes import Code, CodeUsage;

class CustomBot(Bot):
	watcher: asyncio.Task

	async def setup_hook(self):
		cogs_path = Path("./src/cogs").resolve();
		for cogs_file in cogs_path.glob("*.py"):
			if cogs_file.stem == "__init__":
				continue;

			try:
				await self.load_extension(f"src.{cogs_path.stem}.{cogs_file.stem}", package="src.cogs");
				print(f"[CLIENT] Loaded cog {cogs_file.stem}")
			except Exception as e:
				print(f"[CLIENT] Could not load cog {cogs_file.stem}: {e}");
				traceback.print_exc();

		guild = discord.Object(id=os.getenv("TESTING_GUILD_ID", 0))
		self.tree.copy_global_to(guild=guild);
		await self.tree.sync(guild=guild);
		print("[CLIENT] Loaded all cogs")

		database.connect();
		database.create_tables([User, Account, Code, CodeUsage]);
		print("[DATABASE] Loaded database");

		self.watcher = asyncio.create_task(self.cog_watcher())

	async def cog_watcher(self):
		print("[WATCHER] Watching for changes...")
		last = time.time()
		while True:
			reloads = {
				name for name, module in self.extensions.items()
				if module.__file__ and os.stat(module.__file__).st_mtime > last
			}
			for ext in reloads:
				try:
					await self.reload_extension(ext)
					print(f"[WATCHER] Hot reloaded {ext}")
				except ExtensionError as e:
					print(f"[WATCHER] Could not hot reload {ext}: {e}")
			last = time.time()
			await asyncio.sleep(1)

	async def on_ready(self):
		print(f"[CLIENT] Connected as {self.user}");

	async def on_close(self):
		database.close();
		print("[DATABASE] Closed database");

async def main():
	bot = CustomBot("", 
		intents=discord.Intents.all(),
		activity=discord.Activity(name="the casino", type=discord.ActivityType.competing),
		status=discord.Status.idle
	);

	async with bot:
		await bot.start(os.getenv("TOKEN", ""));

if __name__ == '__main__':
	try:
		asyncio.run(main());
	except (KeyboardInterrupt, asyncio.CancelledError):
		pass;
