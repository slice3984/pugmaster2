import enum
from datetime import datetime

from sqlalchemy import Enum, BigInteger, DateTime, MetaData
from sqlalchemy.orm import declarative_base, DeclarativeBase

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
    type_annotation_map = {
        enum.Enum: Enum(
            enum.Enum,
            values_callable=lambda e: [member.value for member in e],
            native_enum=False,
        ),
    }