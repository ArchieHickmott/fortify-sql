"""
This script handles the interaction between python and the database
"""
import sqlite3
import os
import time
import random
import json
from typing import Callable, Iterable, List, Any

import sqlparse

from .utils import is_drop_query, is_dangerous_delete
from .database_map import Table
from .query_builder import QueryBuilder
from .errors import FortifySQLError, DatabaseConfigError, SecurityError

class Database(QueryBuilder):
    # initialise connection to database
    def __init__(self, path: str, check_same_thread: bool=False, name: str = "") -> None:
        """Create a connection to a database, checks if the database exists

        Args:
            path (str): path to the database
            check_same_thread (bool, optional): used to check if a query is made on the same thread as the __main__ thread. Defaults to False.
            name (str, optional): used to give the database a custom name. Defaults to "".

        Raises:
            FortifySQLError: when the database doesn't exist
        """
        if os.path.isfile(path):
            if name == "":
                if "/" in path:
                    self.name = path.rsplit('/', 1)[1]
                else:
                    self.name = path
            else:
                self.name = name
        elif path == ":memory:":
            self.name = "memory"
        else:
            raise FortifySQLError(f"SQL error - Database does not exist on path: {path}.")

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
        
        self.reload_tables()

    # to safely close database
    def __del__(self) -> None:
        """
        Rolls back any uncommited transactions on garbage collection
        """
        if self.conn is not None:
            self.conn.rollback()
            self.conn.close()
    
    def reload_tables(self):
        self.tables = {}
        raw_tables = self.query("SELECT name, sql, tbl_name FROM sqlite_master WHERE type='table'")
        for table in raw_tables:
            table_class = Table(self, table[0], table[1], table[2])
            self.tables[table_class.name] = table_class
        
        for table, table_class in self.tables.items():
            exec(f"self.{table} = table_class")

    def import_configuration(self, path: str = "", json_string: str = ""):
        """Imports a database configuration from a JSON file or a JSON string \n
        For infromation on how to format the JSON go to: https://archiehickmott.github.io/fortify-sql/

        Args (either path or json not none not both):
            path (str, optional): path to the json config file. Defaults to "".
            json_string (str, optional): JSON formated string. Defaults to "".

        Raises:
            DatabaseConfigError: both a path and JSON string provided
            DatabaseConfigError: neither a path or JSON provided
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
            raise DatabaseConfigError("Can't have import configuration from file and string at the same time")
        else:
            raise DatabaseConfigError("No arguments given to import_configuration()")

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
        """used to log queries

        Args:
            statement (str): SQL statement
        """
        print(f"[{self.name}] {statement}")

    # DATABASE CONNECTION CONFIGURATION
    # allow drop
    def allow_drop(self, allow: bool) -> None:
        """allows or bans DROP like statements

        Args:
            allow (bool): wether DROP is banned
        """
        self.allow_dropping = allow

    # enable error catching on queries
    def error_catch(self, enable: bool, logging: bool = False) -> None:
        """enables wether errors are caught on queries

        Args:
            enable (bool): True if errors should be caught False if they should be raised
            logging (bool, optional): True if errors are logged to console False if not. Defaults to False.
        """
        self.error = enable
        self.logging = logging

    def query_logging(self, enable: bool, func: Callable | None = None) -> None:
        """Enables or disables all queries executed on database being logged to console

        Args:
            enable (bool): True if query logging otherwise False
            func (Callable | None, optional): function used to log queries. Defaults to None.
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
        """sets the row factory of the connection \n refer to SQLite3 documentation@https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory for more info

        Args:
            factory (sqlite3.Row | Callable, optional): function or sqlite3.Row class used for a row factory Defaults to sqlite3.Row.
        """
        self.conn.row_factory = factory

    def delete_checking(self, enable: bool = True) -> None:
        """Delete checking creates a temporary copy of a table before executing a delete statement, it will check that the table still exists after the delete statement \n
        This can be computationally expensive for very large tables.s

        Args:
            enable (bool, optional): True if every DELETE statement is checked for danger otherwise False. Defaults to True.
        """
        self.check_delete_statements = enable

    # add a banned statement
    def add_banned_statement(self, statement: str | Iterable[str]) -> None:
        """If a statement is added it means it cannot be run on the database unless it is removed with remove_banned_statement()

        Args:
            statement (str | Iterable[str]): statement type that is banned
        """
        if isinstance(statement, list) or isinstance(statement, tuple):
            for x in statement:
                print(x)
                self.banned_statements.append(x.upper())
        elif isinstance(statement, str):
            self.banned_statements.append(statement.upper())

    # remove banned statement
    def remove_banned_statement(self, statement: str | Iterable[str]) -> None:
        """Allows a once banned statement to be executed on the database

        Args:
            statement (str | Iterable[str]): statement type to un-ban
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
        """If some syntax is added it means it cannot be run on the database unless it is removed with remove_banned_syntax()

        Args:
            syntax (str | Iterable[str]): syntax to ban
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
        """Allows a once banned SQL syntax to be executed on the database

        Args:
            syntax (str | Iterable[str]): syntax to unban
        """
        if isinstance(syntax, list) or isinstance(syntax, tuple):
            for x in syntax:
                if x in self.banned_syntax:
                    self.banned_syntax.remove(x)
        elif isinstance(syntax, str):
            if syntax in self.banned_syntax:
                self.banned_syntax.remove(syntax)

    def backup(self, path: str = "", extension: str = "db") -> str:
        """Creates a backup of the database as path/time.extension ("/time.db" by default) where time us the time of the backup

        Args:
            path (str, optional): path to save to. Defaults to "".
            extension (str, optional): file extension formated as "extension" NOT ".extension". Defaults to "db".

        Returns:
            str: path it was saved to
        """
        path = path + "/" + str(time.asctime().replace(":", "-") + "." + extension)
        with open(self.path, "rb") as src_file:
            with open(path, "wb") as dst_file:
                dst_file.write(src_file.read())
        return path

    def is_dangerous_delete(self, request: str, parameters=()) -> bool:
        """used to check if a DELETE statement is dangerous (wether it deletes the whole table)

        Args:
            request (str): request to check
            parameters (tuple, optional): request parameters. Defaults to ()

        Returns:
            bool: wether it is dangerous or not
        """
        parsed = sqlparse.parse(request)[0]
        if is_dangerous_delete(request):
            return True

        if not ((parsed.get_type() == "DELETE") and (not self.allow_dropping) and self.check_delete_statements):
            return False
        token_list = sqlparse.sql.TokenList(parsed.tokens)
        for token in token_list:
            if token.value == "FROM":
                from_id = token_list.token_index(token)
                table = token_list.token_next(from_id)[1].value

        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        if cur.fetchall() != []:
            cur.close()
            self.conn.commit()
            cur = self.conn.cursor()
            key = random.randint(0, 100)
            temp_table = f"check{key}"
            cur.execute(f"CREATE TEMP TABLE {temp_table} AS SELECT * FROM {table}")
            cur.execute(f"INSERT INTO {temp_table} SELECT * FROM {table}")
            query = request.replace(table, temp_table)
            cur.execute(query, parameters)
            cur.execute(f"SELECT * FROM {temp_table}")
            if cur.fetchall == []:
                cur.execute(f"DROP TABLE {temp_table}")
                self.conn.commit()
                cur.close()
                return True
            else:
                cur.execute(f"DROP TABLE {temp_table}")
                self.conn.commit()
                cur.close()
                return False
        else:
            self.conn.commit()
            cur.close()
            return False

    # Excecutes a single query on the database
    def query(self, request: str, parameters: tuple=(), save_data=True) -> List[List[Any]] | None:
        """Handles querying a database, includes paramaterisation for safe user inputing. \n
        SECURITY NOTE: this allows a single statement to be excecuted no more

        Args:
            request (str): SQL request to execute
            parameters (tuple, optional): paramaters to insert into request. Defaults to ().
            save_data (bool, optional): can be used to ignore data returned by SQL. Defaults to True.

        Raises:
            SecurityError: if more than one statement is provided e.g: SELECT * FROM table; SELECT * FROM table2
            SecurityError: if a DROP statement is provided and they're banned
            SecurityError: if a banned statement was provided
            SecurityError: if a banned syntax was provided
            SecurityError: if a dangerous DELETE was provided

        Returns:
            List[List[Any]] | None: None if no data was returned by SQL, returns a table if not
        """
        try:
            parsed = sqlparse.parse(request)
            if not len(parsed) == 1:
                raise SecurityError("Multiple statements not allowed in a single query")

            if (not self.allow_dropping) and is_drop_query(request):
                raise SecurityError(f"Dropping is disabled on this database")

            if self.banned_statements != []:
                if parsed[0].get_type().upper() in self.banned_statements:
                    raise SecurityError(f"Attempted to execute banned statement: {request}")

            if self.banned_syntax != []:
                for banned in self.banned_syntax:
                    if banned in request:
                        raise SecurityError(f"Attempted to execute banned syntax: {request}")

            if self.is_dangerous_delete(request, parameters):
                raise SecurityError(f"Attempted to execute dangerous statement: {request}")

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
    def multi_query(self, request: str, parameters: tuple=(), save_data=True) -> List[List[Any]]:
        """Handles querying a database, includes paramaterisation for safe user inputing. \n
        SECURITY NOTE: this allows a multiple statements to be executed, only use if necessery

        Args:
            request (str): SQL request to execute
            parameters (tuple, optional): paramaters to insert into request. Defaults to ().
            save_data (bool, optional): can be used to ignore data returned by SQL. Defaults to True.

        Raises:
            SecurityError: if a DROP statement is provided and they're banned
            SecurityError: if a banned statement was provided
            SecurityError: if a banned syntax was provided
            SecurityError: if a dangerous DELETE was provided

        Returns:
            List[List[Any]] | None: None if no data was returned by SQL, returns a table if not
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