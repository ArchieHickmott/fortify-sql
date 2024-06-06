"""
This script handles the interaction between python and the database
"""

import sqlite3
import os
import time
from .purify import is_always_true_where, is_drop_query, is_delete_without_where, is_dangerous_delete
import sqlparse
import random

class Database:
    """
    This class handles the interaction between python and the database.
    """
    error = True
    allow_dropping = False
    logging = False
    banned_statements = []

    # initialise connection to database
    def __init__(self, path: str, key="default", check_same_thread: bool=False) -> None:
        self.cur = None
        self.conn = None
        if os.path.isfile(path):
            self.key = key
            if "/" in path:
                self.name = path.rsplit('/', 1)[1]
            else:
                self.name = path
            self.path = path
            self.conn = sqlite3.connect(path, check_same_thread=check_same_thread)
            self.recent_data = None
        else:
            raise Exception(f"FortifySQL error - Database does not exist on path: {path}.")

    # to safely close database
    def __del__(self) -> None:
        if self.conn is not None:
            self.conn.rollback()
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
    
    # add a banned statement
    def add_banned_statement(self, statement: str | list | tuple) -> None:
        if isinstance(statement, list) or isinstance(statement, tuple):
            for x in statement:
                Database.banned_statements.append(x)
        elif isinstance(statement, str):
            Database.banned_statements.append(statement)
        else:
            return None

    # Excecutes a single query on the database
    def query(self, request: str, parameters: tuple=None, save_data=True) -> list | None:
        """
        Handles querying a database, includes paramaterisation for safe user inputing. \n
        SECURITY NOTE: this allows a single statement to be excecuted
        """
        try:
            parsed = sqlparse.parse(request)
            if len(parsed) == 1:
                if (not self.allow_dropping) and is_drop_query(request):
                    raise Exception(f"Dropping is disabled on this database")
                
                if parsed[0].get_type() in self.banned_statements():
                    return None

                # Protection for delete statements
                # won't commit a query that deletes a whole table
                if parsed[0].get_type() == "DELETE":
                    parsed = parsed[0]
                    token_list = sqlparse.sql.TokenList(parsed.tokens)
                    for token in token_list:
                        if token.value == "FROM":
                            from_id = token_list.token_index(token)
                            table = token_list.token_next(from_id)[1].value
                    
                    cur = self.conn.cursor()
                    cur.execute(f"SELECT * FROM {table}")
                    if not cur.fetchall() == []:
                        cur.close()
                        self.conn.commit()
                        cur = self.conn.cursor()
                        key = random.randint(0, 100)
                        temp_table = f"check{key}"
                        cur.execute(f"CREATE TEMP TABLE {temp_table} AS SELECT * FROM {table} WHERE 0")
                        cur.execute(f"INSERT INTO {temp_table} SELECT * FROM {table}")
                        query = request.replace(table, temp_table)
                        cur.execute(query, parameters)
                        cur.execute(f"SELECT * FROM {temp_table}")
                        if not cur.fetchall == []:
                            cur.execute(f"DROP TABLE {temp_table}")
                            self.conn.commit()
                            cur.close()
                            self.cur = self.conn.cursor()
                            self.cur.execute(request, parameters)
                            self.conn.commit()
                            self.cur.close()
                            self.cur = None
                            return None
                        else:
                            cur.execute(f"DROP TABLE {temp_table}")
                            self.conn.commit()
                            cur.close()
                    else:
                        self.conn.commit()
                        cur.close()

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
    def multi_query(self, request: str, parameters: tuple=None, save_data=True):
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
                
                if statement.get_type() in self.banned_statements():
                    return None

                if statement.get_type() == "DELETE":
                    parsed = parsed[0]
                    token_list = sqlparse.sql.TokenList(parsed.tokens)
                    for token in token_list:
                        if token.value == "FROM":
                            from_id = token_list.token_index(token)
                            table = token_list.token_next(from_id)[1].value
                    
                    cur = self.conn.cursor()
                    cur.execute(f"SELECT * FROM {table}")
                    if not cur.fetchall() == []:
                        cur.close()
                        self.conn.commit()
                        cur = self.conn.cursor()
                        key = random.randint(0, 100)
                        temp_table = f"check{key}"
                        cur.execute(f"CREATE TEMP TABLE {temp_table} AS SELECT * FROM {table} WHERE 0")
                        cur.execute(f"INSERT INTO {temp_table} SELECT * FROM {table}")
                        query = request.replace(table, temp_table)
                        cur.execute(query, parameters)
                        cur.execute(f"SELECT * FROM {temp_table}")
                        if not cur.fetchall == []:
                            cur.execute(f"DROP TABLE {temp_table}")
                            self.conn.commit()
                            cur.close()
                            self.cur = self.conn.cursor()
                            self.cur.execute(request, parameters)
                            self.conn.commit()
                            self.cur.close()
                            self.cur = None
                            return None
                        else:
                            cur.execute(f"DROP TABLE {temp_table}")
                            self.conn.commit()
                            cur.close()
                    else:
                        self.conn.commit()
                        cur.close()

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

