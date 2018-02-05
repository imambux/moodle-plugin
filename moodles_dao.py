from peewee import *
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import model_to_dict

import settings

db = PooledMySQLDatabase(
    database=settings.DATABASE_NAME,
    user=settings.DATABASE_USER,
    passwd=settings.DATABASE_PASS,
    host=settings.DATABASE_HOST,
    max_connections=None
)


class Moodle(Model):
    moodle_id = IntegerField(primary_key=True)
    host = CharField()
    display_name = CharField()
    token = CharField()

    class Meta:
        database = db


class MoodlesBorg:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.moodles = self.__fetch_moodles()

    def __fetch_moodles(self):
        moodles_dict = dict()

        if not db.get_conn():
            db.connect()

        for moodle in Moodle.select():
            aDict = model_to_dict(moodle)
            moodles_dict[moodle.moodle_id] = aDict

        if not db.is_closed():
            db.close()

        return moodles_dict

    def get_moodles(self):
        return self.moodles

    def refresh_moodles(self):
        self.moodles = self.__fetch_moodles()
