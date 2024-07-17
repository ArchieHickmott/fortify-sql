__version__ = "0.4.1"
__author__ = 'Archie Hickmott'
import sqlite3

from .database import Database
from .utils import is_always_true_where, is_drop_query, is_delete_without_where, is_dangerous_delete
from .sql_data_types import Null, Integer, Real, Text, Blob, ALL_SQL_DATA_TYPE_NAMES, ALL_SQL_DATA_TYPES
from .database_map import Table

import sqlparse

print(f"\033[93mWARNING FortifySQL is in BETA {__version__}, do not use in a production environment until full release \033[0m")

__all__ = ['Database', "Table", "column",
           "is_always_true_where", "is_drop_query",
           "is_delete_without_where", "is_dangerous_delete",
           "sqlite3", "Null", "Integer", "Real", "Text", "Blob"]
