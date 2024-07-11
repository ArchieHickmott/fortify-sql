"""
This script handles the interaction between python and the database
"""
import sqlparse

import sqlite3
import os
import time
import random
import json
from typing import Callable, Iterable

from .utils import is_drop_query, is_dangerous_delete
from .orm import Select

class Database(Select):
    """
    This class handles the interaction between python and the self.
    """
    # initialise connection to database
    def __init__(self, path: str, check_same_thread: bool=False, name: str = "") -> None:
        """
        Create a connection to a database, checks if the database exists
        """
        if os.path.isfile(path):
            if name != "":
                if "/" in path:
                    self.name = path.rsplit('/', 1)[1]
                else:
                    self.name = path
            else:
                self.name = name
        elif path == ":memory:":
            self.name = "memory"
        else:
            raise Exception(f"SQL error - Database does not exist on path: {path}.")

        self.error = False
        self.allow_dropping = False
        self.check_delete_statements = True
        self.error_logging = False
        self.banned_statements = []
        self.banned_syntax = []

        self.cur = None
        self.path = path
        self.conn = sqlite3.connect(path, check_same_thread=check_same_thread)
        self.recent_data = None

    # to safely close database
    def __del__(self) -> None:
        """
        Rolls back any uncommited transactions on garbage collection
        """
        if self.conn is not None:
            self.conn.rollback()
            self.conn.close()

    def import_configuration(self, path: str = "", json_string: str = ""):
        """
        Imports a database configuration from a JSON file or a JSON string \n
        For infromation on how to format the JSON go to: https://archiehickmott.github.io/fortify-sql/
        """
        is_path = path != ""
        is_json = json_string != ""
        config = None
        if is_path and not is_json:
            with open(path, 'r') as file:
                config = json.load(file)
        elif is_json and not is_path:
            config = json.loads(json_string)
        elif is_path and is_json:
            raise Exception("Can't have import configuration from file and string at the same time")
        else:
            raise Exception("No arguments given to import_configuration()")

        self.error = config["error_catching"]
        self.allow_dropping = config["allow_dropping"]
        self.check_delete_statements = config["check_delete_statements"]
        self.error_logging = config["error_logging"]
        self.banned_statements = config["banned_statements"]
        self.banned_syntax = config["banned_syntax"]

        if config["default_query_logger"]:
            self.query_logging(True)
        if config["default_row_factory"]:
            self.row_factory(sqlite3.Row)

    def logger(self, statement: str) -> None:
        print(f"[{self.name}] {statement}")

    # DATABASE CONNECTION CONFIGURATION
    # allow drop
    def allow_drop(self, allow: bool) -> None:
        """
        Enables methods that drop aspects of a database
        """
        self.allow_dropping = allow

    # enable error catching on queries
    def error_catch(self, enable: bool, logging: bool = False) -> None:
        """
        Enables error catching on queries made to database
        """
        self.error = enable
        self.logging = logging

    def query_logging(self, enable: bool, func: Callable | None = None) -> None:
        """
        Enables query logging, prints form [database name] query
        """
        if not enable:
            self.conn.set_trace_callback(None)
            return None
        if func is None:
            self.conn.set_trace_callback(self.logger)
        else:
            self.conn.set_trace_callback(func)

    #allows dev to set the row factory
    def row_factory(self, factory: sqlite3.Row | Callable = sqlite3.Row) -> None:
        """
        sets the row factory of the connection \n refer to SQLite3 documentation@https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory for more info
        """
        self.conn.row_factory = factory

    def delete_checking(self, enable: bool = True) -> None:
        """
        Delete checking creates a temporary copy of a table before executing a delete statement, it will check that the table still exists after the delete statement \n
        This can be computationally expensive for very large tables.
        """
        self.check_delete_statements = enable

    # add a banned statement
    def add_banned_statement(self, statement: str | Iterable[str]) -> None:
        """
        If a statement is added it means it cannot be run on the database unless it is removed with remove_banned_statement()
        """
        if isinstance(statement, list) or isinstance(statement, tuple):
            for x in statement:
                print(x)
                self.banned_statements.append(x.upper())
        elif isinstance(statement, str):
            self.banned_statements.append(statement.upper())
        else:
            return None

    # remove banned statement
    def remove_banned_statement(self, statement: str | Iterable[str]) -> None:
        """
        Allows a once banned statement to be executed on the database
        """
        if isinstance(statement, list) or isinstance(statement, tuple):
            for x in statement:
                if x in self.banned_statements:
                    self.banned_statements.remove(x)
        elif isinstance(statement, str):
            if statement in self.banned_statements:
                self.banned_statements.remove(statement)

    # add a banned syntax
    def add_banned_syntax(self, syntax: str | Iterable[str]) -> None:
        """
        If some syntax is added it means it cannot be run on the database unless it is removed with remove_banned_syntax()
        """
        if isinstance(syntax, list) or isinstance(syntax, tuple):
            for x in syntax:
                if x in self.banned_syntax:
                    self.banned_syntax.append(x)
        elif isinstance(syntax, str):
            if syntax in self.banned_syntax:
                self.banned_syntax.append(syntax)

    # remove banned syntax
    def remove_banned_syntax(self, syntax: str | Iterable[str]) -> None:
        """
        Allows a once banned SQL syntax to be executed on the database
        """
        if isinstance(syntax, list) or isinstance(syntax, tuple):
            for x in syntax:
                if x in self.banned_syntax:
                    self.banned_syntax.remove(x)
        elif isinstance(syntax, str):
            if syntax in self.banned_syntax:
                self.banned_syntax.remove(syntax)

    def backup(self, path: str = "", extension: str = "db") -> None:
        """
        Creates a backup of the database as path/time.extension ("/time.db" by default) where time us the time of the backup
        """
        path = path + "/" + str(time.asctime().replace(":", "-") + "." + extension)
        with open(self.path, "rb") as src_file:
            with open(path, "wb") as dst_file:
                dst_file.write(src_file.read())
        return path

    def is_dangerous_request(self, request, parameters) -> bool:
        parsed = sqlparse.parse(request)[0]
        if is_dangerous_delete(request):
            return True

        if parsed.get_type() == "DELETE" and not self.allow_dropping:
            token_list = sqlparse.sql.TokenList(parsed.tokens)
            for token in token_list:
                if token.value == "FROM":
                    from_id = token_list.token_index(token)
                    table = token_list.token_next(from_id)[1].value

            cur = self.conn.cursor()
            cur.execute(f"SELECT * FROM {table}")
            if cur.fetchall() == []:
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
                    return False
                else:
                    cur.execute(f"DROP TABLE {temp_table}")
                    self.conn.commit()
                    cur.close()
            else:
                self.conn.commit()
                cur.close()
                return True

    # Excecutes a single query on the database
    def query(self, request: str, parameters: tuple=(), save_data=True) -> list | None:
        """
        Handles querying a database, includes paramaterisation for safe user inputing. \n
        SECURITY NOTE: this allows a single statement to be excecuted
        """
        try:
            parsed = sqlparse.parse(request)
            if not len(parsed) == 1:
                raise Exception("Multiple statements not allowed in a single query")

            if (not self.allow_dropping) and is_drop_query(request):
                raise Exception(f"Dropping is disabled on this database")

            if self.banned_statements != []:
                if parsed[0].get_type().upper() in self.banned_statements:
                    raise Exception("Attempted to execute banned statement")

            if self.banned_syntax != []:
                for banned in self.banned_syntax:
                    if banned in request:
                        raise Exception("Attempted to execute banned syntax")

            if self.is_dangerous_request(request, parameters):
                raise Exception(f"Attempted to execute dangerous statement: {request}")

            self.cur = self.conn.cursor()
            self.cur.execute(request, parameters)
            data = self.cur.fetchall()
            self.conn.commit()
            self.cur.close()
            self.cur = None
            if save_data:
                self.recent_data = data
                return data

        except Exception as e:
            if self.error:
                if self.logging:
                    print(f"SQL DATABASE ERROR, database: {self.path}, error: {e}")
            else:
                raise Exception(e)

    # Excecutes multiple queries on the database
    def multi_query(self, request: str, parameters: tuple=(), save_data=True):
        """
        Handles querying a database, includes paramaterisation for safe user inputing. will only return first statements data \n
        SECURITY NOTE: this allows multiple statements to be exceucuted at once, use query() if only one statement will be run
        """
        try:
            statements = sqlparse.split(request)
            for statement in statements:
                self.query(statement, parameters, save_data)
            return self.recent_data
        except Exception as e:
            if self.error:
                if self.logging:
                    print(f"SQL DATABASE ERROR, database: {self.path}, error: {e}")
            else:
                raise Exception(e)
    
    def commit(self):   
        if self.join_template[0]: # if there is a table join
            query = self.header + self.join_template[1] + " "
        else:
            query = self.header
        query += self.where_clause + self.footer + ";"
        print(query)
        query = self.query(query, self.parameters if self.parameters is not None else ())
        self.reset()
        return query