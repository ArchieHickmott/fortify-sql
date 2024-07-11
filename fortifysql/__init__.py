__version__ = "0.2.0"
__author__ = 'Archie Hickmott'

from .database import Database
from .utils import is_always_true_where, is_drop_query, is_delete_without_where, is_dangerous_delete
from .tables import column, Table
from .orm import Select
import sqlite3

__all__ = ['Database', "Table", "column",
           "is_always_true_where", "is_drop_query",
           "is_delete_without_where", "is_dangerous_delete",
           "sqlite3", "Select"]
