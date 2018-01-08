from peewee import *
from playhouse.pool import PooledMySQLDatabase

import settings

db = PooledMySQLDatabase(
    database=settings.DATABASE_NAME,
    user=settings.DATABASE_USER,
    passwd=settings.DATABASE_PASS,
    host=settings.DATABASE_HOST
)


class Moodles(Model):
    moodle_id = IntegerField(primary_key=True)
    host = CharField()
    display_name = CharField()
    token = CharField()

    class Meta:
        database = db