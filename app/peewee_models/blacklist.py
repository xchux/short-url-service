from peewee import CharField, DateTimeField, Model

from app.peewee_models import db


class Blacklist(Model):
    ip = CharField(max_length=12)
    reason = CharField(max_length=30)
    modified = DateTimeField(null=True)
    created = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = "blacklist"
        primary_key = False
        indexes = ((("ip", "reason"), True),)
