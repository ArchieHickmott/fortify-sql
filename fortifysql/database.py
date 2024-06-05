"""
This script handles the interaction between python and the database
"""

import sqlite3
import os
import time
from .purify import is_always_true_where, is_drop_query, is_delete_without_where, is_dangerous_delete
import sqlparse

class Database:
    """
    This class handles the interaction between python and the database, changing key is highly recomended
    for all methods classed as admin, the key is passed through as an argument, if the keys match then the method is
    ran, otherwise its not
    """
    error = True
    allow_dropping = False
    logging = False

    # initialise connection to database
    def __init__(self, path: str, key="default") -> None:
        if os.path.isfile(path):
            self.key = key
            if "/" in path:
                self.name = path.rsplit('/', 1)[1]
            else:
                self.name = path
            self.path = path
            self.conn = sqlite3.connect(path)
            self.cur = None
            self.recent_data = None
        else:
            raise Exception(f"FortifySQL error - Database does not exist on path: {path}.")

    # to safely close database
    def __del__(self) -> None:
        if self.cur is not None:
            self.cur.close()
        self.conn.close()

    # DATABASE CONNECTION CONFIGURATION
    # allow drop
    def allow_drop(self, allow: bool) -> None:
        """
        Enables methods that drop aspects of a database
        """
        Database.allow_dropping = allow
    # enable error catching on queries
    def error_catch(self, enable: bool, logging: bool = False) -> None:
        """
        Enables error catching on queries made to database
        """
        Database.error = enable
        Database.logging = logging
    
    # Excecutes a single query on the database
    def query(self, request: str, parameters: tuple=None, save_data=False) -> list:
        """
        Handles querying a database, includes paramaterisation for safe user inputing. \n
        SECURITY NOTE: this allows a single statement to be excecuted
        """
        try:
            parsed = sqlparse.parse(request)
            if len(parsed) == 1:
                if (not self.allow_dropping) and (is_drop_query(request) or is_dangerous_delete(request)):
                    raise Exception(f"Dropping is disabled on this database")
                self.cur = self.conn.cursor()
                if parameters:
                    self.cur.execute(request, parameters)
                else:
                    self.cur.execute(request)
                data = self.cur.fetchall()
                self.conn.commit()
                self.cur.close()
                self.cur = None
                if save_data:
                    self.recent_data = data
                    return data
            else:
                raise Exception("Multiple statements not allowed in query(), try using multi_query()")
        except Exception as e:
            if self.error:
                if self.logging:
                    print(f"FortifySQL DATABASE ERROR, database: {self.path}, error: {e}")
            else:
                raise Exception(e)

    # Excecutes multiple queries on the database
    def multi_query(self, request: str, parameters: tuple=None, save_data=False):
        """
        Handles querying a database, includes paramaterisation for safe user inputing. will only return first statements data \n
        SECURITY NOTE: this allows multiple statements to be exceucuted at once, use query() if only
        one statement will be run
        """
        try:
            data = None
            statements = sqlparse.split(request)
            for statement in statements:
                if (not self.allow_dropping) and (is_drop_query(statement) or is_dangerous_delete(statement)):
                    raise Exception(f"Dropping is disabled on this database")
                self.cur = self.conn.cursor()
                if parameters:
                    self.cur.execute(statement, parameters)
                else:
                    self.cur.execute(statement)
                temp_data = self.cur.fetchall()
                self.conn.commit()
                self.cur.close()
                self.cur = None
                if save_data and data is not None:
                    self.recent_data = data
                    data = temp_data
            return data
        
        except Exception as e:
            if self.error:
                if self.logging:
                    print(f"FortifySQL DATABASE ERROR, database: {self.path}, error: {e}")
            else:
                raise Exception(e)
