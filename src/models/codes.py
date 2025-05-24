from .base import BaseModel;
from .account import User;
from peewee import CharField, DateTimeField, ForeignKeyField, IntegerField;

class Code(BaseModel):
	content = CharField(unique=True, primary_key=True)
	valid_from = DateTimeField()
	valid_until = DateTimeField(null=True)
	value = IntegerField()
	max_uses = IntegerField(null=True)

class CodeUsage(BaseModel):
	user = ForeignKeyField(User, backref="code_uses", primary_key=True)
	code = ForeignKeyField(Code, backref="uses")