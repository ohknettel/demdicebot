from ..models.account import User, Account
from .logging import logger;
import typing;

class EconomyHelper:
	def __init__(self, account: Account):
		self.account = account;
		self.user = typing.cast(User, account.user);

	def set_balance(self, new_balance: int):
		current_balance: int = typing.cast(int, self.account.balance);
		self.account.balance = new_balance; # pyright: ignore
		self.account.save();
		logger.info(f"Updated [{self.user.uid}]'s balance from {current_balance} to {new_balance}");
		return self;

	def add_chips(self, amount: int, reason: typing.Optional[str] = None):
		self.account.balance += amount;
		self.account.save();
		logger.info(f"Added {amount} to [{self.user.uid}]'s balance - new balance: {self.account.balance}");
		if reason:
			logger.info(f"Reason: {reason}")
		return self;

	def remove_chips(self, amount: int, reason: typing.Optional[str] = None):
		if amount > self.account.balance:
			raise ValueError("Insufficient balance")
		
		self.account.balance -= amount;
		self.account.save();
		logger.info(f"Removed {amount} from [{self.user.uid}]'s balance - new balance: {self.account.balance}");
		if reason:
			logger.info(f"Reason: {reason}")
		return self;

	def add_bet(self, amount: int):
		self.user.total_bet += amount;
		self.user.save();
		return self;

	
