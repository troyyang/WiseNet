from datetime import datetime
from typing import Dict, Any

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.inspection import inspect
from core.database import DBBase

class BaseModel(DBBase):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.now())
    update_time = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    def __repr__(self):
        return f"id={self.id}, create_time={self.create_time}, \
                update_time={self.update_time}"

    @classmethod
    def _to_dict_list(self, items, item_class, filter=None):
        if items and isinstance(items, list):
            return [item.to_dict(filter) if isinstance(item, item_class) else item for item in items]
        return []

    def to_dict(self, filter=None) -> Dict[str, Any]:
        # get all column names
        columns = inspect(self).mapper.column_attrs.keys()
        if filter:
            columns = [c for c in columns if c in filter]

        result = {}
        for column in columns:
            value = getattr(self, column)
            # Check if the value is an instance of DateTime and format it accordingly.
            if isinstance(value, datetime):
                # Convert datetime object to ISO 8601 string.
                result[column] = value.isoformat()
            else:
                result[column] = value
        
        return result


    