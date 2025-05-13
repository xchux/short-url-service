from typing import Optional

from peewee import SQL, DateTimeField

from app.peewee_models.enums import TimestampDefaultEnum


class MysqlTimestampField(DateTimeField):
    field_type = "TIMESTAMP"

    def __init__(
        self,
        default: Optional[TimestampDefaultEnum] = None,
        on_update_current_timestamp: bool = False,
        *args,
        **kwargs,
    ):
        constraints = kwargs.get("constraints", [])

        if default is not None:
            constraints.append(SQL(f"DEFAULT {default}"))
        if on_update_current_timestamp:
            constraints.append(SQL("ON UPDATE CURRENT_TIMESTAMP"))

        if constraints:
            kwargs["constraints"] = constraints

        super().__init__(*args, **kwargs)
