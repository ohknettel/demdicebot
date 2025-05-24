from .base import BaseModel;
from peewee import IntegerField, ForeignKeyField

class User(BaseModel):
	uid = IntegerField(unique=True, null=False, primary_key=True)
	games_played = IntegerField(null=False, default=0)
	games_won = IntegerField(null=False, default=0)
	games_lost = IntegerField(null=False, default=0)
	total_bet = IntegerField(null=False, default=0)
	total_won = IntegerField(null=False, default=0)

class Account(BaseModel):
	user = ForeignKeyField(User, backref="account", on_delete="CASCADE")
	balance = IntegerField(null=False, default=0)
	gifted_balance = IntegerField(null=False, default=0)