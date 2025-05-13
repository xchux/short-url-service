from peewee import BlobField, CharField, Model, TextField

from app.peewee_models import db
from app.peewee_models.enums import TimestampDefaultEnum
from app.peewee_models.field import MysqlTimestampField


class Urls(Model):
    short_code = CharField(max_length=30, primary_key=True)
    original_url = TextField(...)
    url_hash = BlobField()
    expiration_date = MysqlTimestampField(default=TimestampDefaultEnum.ZERO)
    modified = MysqlTimestampField(
        default=TimestampDefaultEnum.CURRENT_TIMESTAMP, on_update_current_timestamp=True
    )
    created = MysqlTimestampField(default=TimestampDefaultEnum.CURRENT_TIMESTAMP)

    class Meta:
        database = db
        table_name = "urls"
