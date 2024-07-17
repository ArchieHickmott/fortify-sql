__version__ = "0.2.0"
__author__ = 'Archie Hickmott'

from .database import Database
from .utils import is_always_true_where, is_drop_query, is_delete_without_where, is_dangerous_delete
# from .query_build import Select
from .sql_data_types import Null, Integer, Real, Text, Blob, ALL_SQL_DATA_TYPE_NAMES, ALL_SQL_DATA_TYPES
from .database_map import Table
import sqlite3

__all__ = ['Database', "Table", "column",
           "is_always_true_where", "is_drop_query",
           "is_delete_without_where", "is_dangerous_delete",
           "sqlite3", "Null", "Integer", "Real", "Text", "Blob"]
