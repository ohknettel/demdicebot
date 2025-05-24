from peewee import Model, SqliteDatabase;

database = SqliteDatabase("data.db")
class BaseModel(Model):
	class Meta:
		database = database