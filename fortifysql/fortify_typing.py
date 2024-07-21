from typing import List, Self, Iterable, Callable, Any
from sqlite3 import Row
from .sql_data_types import LogicalString

class TypeTable:
    def __init__(self, db, name: str, sql, tbl_name=""):
        """Used by FortifySQL ORM to represent a table

        Args:
            db (Database): what database the table is on
            name (str): name of the table
            sql (str): sql statement that creates the table
            tbl_name (str, optional): SQLite tbl_name variable Defaults to "".
        """
            
    def select(self, *args):
        """used to select data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
    
    def select_distinct(self, *args) -> Self:
        """used to select DISTINCT data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
    
    def insert(self, *cols, abort: bool=False, fail: bool=False, ignore: bool=False, replace: bool=False, rollback: bool=False):
        """ used to insert data into the database, give table and columns to the table and columns insert into, use insert().values() for the values to insert

        Args:
            table (Table): table to insert into
            cols (List[Column  |  str], optional): columns to insert into
            abort (bool, optional): SQL OR ABORT clause. Defaults to False.
            fail (bool, optional): SQL OR FAIL clause. Defaults to False.
            ignore (bool, optional): SQL OR IGNORE clause. Defaults to False.
            replace (bool, optional): SQL OR REPLACE clause. Defaults to False.
            rollback (bool, optional): SQL OR ROLLBACK clause. Defaults to False.
        """
    
    def update(self, abort: bool=False, fail: bool=False, ignore: bool=False, replace: bool=False, rollback: bool=False):
        """ used to update data into the database, give table to update, use update().values(col==value,...) for the values to update

        Args:
            table (Table): table to update
            abort (bool, optional): SQL OR ABORT clause. Defaults to False.
            fail (bool, optional): SQL OR FAIL clause. Defaults to False.
            ignore (bool, optional): SQL OR IGNORE clause. Defaults to False.
            replace (bool, optional): SQL OR REPLACE clause. Defaults to False.
            rollback (bool, optional): SQL OR ROLLBACK clause. Defaults to False.
        """

    def delete(self, expr: str = False):
        """deletes data from a table where the row fufils the expression

        Args:
            table (Table): table to delete from
            expr (str, optional): WHERE expression to filter the data to be deleted. Defaults to False.

        Raises:
            SecurityError: if there is no WHERE clause and DROPPING is banned on database
        """

class TypeColumn:
    def __init__(self, name: str, dtype, table: TypeTable):
        """Used to represent a column in the FortifySQL ORM

        Args:
            name (str): name of the column
            dtype (SQLite data type): data type of the column
            table (Table): FortifySQL Table class
        """
        
    def __str__(self) -> LogicalString:
        """used for str(Column())

        Returns:
            str: name of the column
        """
    
    def __eq__(self, value: object) -> str:
        """used for query formatting i.e: table.where(column1 == column2)

        Args:
            value (object): what to test a column equals

        Returns:
            str: returns SQL expression
        """
        
    def __le__(self, value: object):
        """used for query formatting i.e: table.where(column1 <= column2)

        Args:
            value (object): what to test a column <=

        Returns:
            str: returns SQL expression
        """

    def __ge__(self, value: object):
        """used for query formatting i.e: table.where(column1 >= column2)

        Args:
            value (object): what to test a column >=

        Returns:
            str: returns SQL expression
        """

    def __gt__(self, value: object):
        """used for query formatting i.e: table.where(column1 > column2)

        Args:
            value (object): what to test a column >

        Returns:
            str: returns SQL expression
        """

    def __lt__(self, value: object):
        """used for query formatting i.e: table.where(column1 < column2)

        Args:
            value (object): what to test a column <

        Returns:
            str: returns SQL expression
        """

    def __ne__(self, value: object):
        """used for query formatting i.e: table.where(column1 != column2)

        Args:
            value (object): what to test a column !=

        Returns:
            str: returns SQL expression
        """
        
    def literal_name(self):
        """returns the literal name of the column, name instead of table.name"""

# query_builder.py
class TypeQueryBuilder:
    def select(self, table: TypeTable, *args: TypeTable | TypeColumn | str):
        """used to select data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
    
    def select_distinct(self, table: TypeTable, *args: TypeTable | TypeColumn | str):
        """used to select DISTINCT data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
    
    def insert(self, table: TypeTable, *cols: List[TypeColumn | str], abort: bool=False, fail: bool=False, ignore: bool=False, replace: bool=False, rollback: bool=False):
        """ used to insert data into the database, give table and columns to the table and columns insert into, use insert().values() for the values to insert

        Args:
            table (Table): table to insert into
            cols (List[Column  |  str], optional): columns to insert into
            abort (bool, optional): SQL OR ABORT clause. Defaults to False.
            fail (bool, optional): SQL OR FAIL clause. Defaults to False.
            ignore (bool, optional): SQL OR IGNORE clause. Defaults to False.
            replace (bool, optional): SQL OR REPLACE clause. Defaults to False.
            rollback (bool, optional): SQL OR ROLLBACK clause. Defaults to False.
        """
    
    def update(self, table: TypeTable, abort: bool=False, fail: bool=False, ignore: bool=False, replace: bool=False, rollback: bool=False):
        """ used to update data into the database, give table to update, use update().values(col==value,...) for the values to update

        Args:
            table (Table): table to update
            abort (bool, optional): SQL OR ABORT clause. Defaults to False.
            fail (bool, optional): SQL OR FAIL clause. Defaults to False.
            ignore (bool, optional): SQL OR IGNORE clause. Defaults to False.
            replace (bool, optional): SQL OR REPLACE clause. Defaults to False.
            rollback (bool, optional): SQL OR ROLLBACK clause. Defaults to False.
        """

    def delete(self, table: TypeTable, expr: str = False):
        """deletes data from a table

        Args:
            table (Table): table to delete from
            expr (str, optional): WHERE expression to filter the data to be deleted. Defaults to False.

        Raises:
            SecurityError: if there is no WHERE clause and DROPPING is banned on database
        """
    
class TypeStatementType:
    def __init__(self, db):
        """create the statement

        Args:
            db (Database): FortiftSQL Database Class
        """
        
    def parameters(self, *args):
        """runs the query with parameters"""
    
    def run(self):
        """runs the query
        """
        
class TypeSelect(TypeStatementType):        
    def select(self, table: TypeTable, args: List[TypeTable | TypeColumn | str]):
        """used to select data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """

    def __join(self, tables: List[TypeTable], distinct: bool, args: List[TypeColumn | str]):
        """used to create a join query

        Args:
            tables (List[Table]): tables to join
            distinct (bool): whether it is DISTINCT or not
            *args: columns to SELECT
        """
        
    def where(self, expr: str):
        """used to add a WHERE clause to a statement

        Args:
            expr (str): expression for where clause

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """

    def _and(self, expr: str):
        """used to add a AND operator to a statement

        Args:
            expr (str): expression for AND clause

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
    
    def _or(self, expr: str):
        """used to add a OR operator to a statement

        Args:
            expr (str): expression for OR clause

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
    
    def groupby(self, *args, having=""):
        """used to group data from a SQL statistical funtion

        Args:
            args (str): columns/aliases to group by
        """
    
    def order(self, *args):
        """used to determine the order that data is returned"""
        
    def limit(self, limit: str | int):
        """used to limit the amount of data returned
        
        Args:
            args (str, int): the maximum amount of rows that can be returned 
        """
        
    def build(self) -> str:
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """

class TypeDistinctSelect(TypeSelect):    
    def build(self):
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """  

class TypeInsert(TypeStatementType):  
    def insert(self, 
               table: TypeTable, 
               cols: List[TypeColumn | str] = False,
               abort: bool=False,
               fail: bool=False,
               ignore: bool=False,
               replace: bool=False,
               rollback: bool=False
               ):
        """ used to insert data into the database, give table and columns to the table and columns insert into, use insert().values() for the values to insert

        Args:
            table (Table): table to insert into
            cols (List[Column  |  str], optional): columns to insert into
            abort (bool, optional): SQL OR ABORT clause. Defaults to False.
            fail (bool, optional): SQL OR FAIL clause. Defaults to False.
            ignore (bool, optional): SQL OR IGNORE clause. Defaults to False.
            replace (bool, optional): SQL OR REPLACE clause. Defaults to False.
            rollback (bool, optional): SQL OR ROLLBACK clause. Defaults to False.
        """
    
    def values(self, *args):
        """values to insert use like: \n
        .values(value,...)
        """
    
    def conflict(self, conflict):
        """define what to do on a conflict"""
    
    def build(self):
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """

class TypeUpdate(TypeStatementType):    
    def update(self, 
               table: TypeTable, 
               abort: bool=False,
               fail: bool=False,
               ignore: bool=False,
               replace: bool=False,
               rollback: bool=False
               ):
        """ used to update data into the database, give table to update, use update().values(col==value,...) for the values to update

        Args:
            table (Table): table to update
            abort (bool, optional): SQL OR ABORT clause. Defaults to False.
            fail (bool, optional): SQL OR FAIL clause. Defaults to False.
            ignore (bool, optional): SQL OR IGNORE clause. Defaults to False.
            replace (bool, optional): SQL OR REPLACE clause. Defaults to False.
            rollback (bool, optional): SQL OR ROLLBACK clause. Defaults to False.
        """
    
    def values(self, *args):
        """what columns to update and the values to set them to, use like this:\n
        .values(table.col == 2, table.col2 == 3)

        Args:
            expressions (str): formatted like: column = value
        """
    
    def where(self, expr: str):
        """UPDATE WHERE clause

        Args:
            expr (str): expression
        """
    
    def _from(self, expr: str):
        """UPDATE FROM clause

        Args:
            expr (str): expression
        """
        
    def build(self):
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """

class TypeDelete(TypeStatementType):   
    def delete(self, table: TypeTable, expr: str = False):
        """deletes data from a table

        Args:
            table (Table): table to delete from
            expr (str, optional): WHERE expression to filter the data to be deleted. Defaults to False.

        Raises:
            SecurityError: if there is no WHERE clause and DROPPING is banned on database
        """
    
    def build(self):
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """

class TypeDatabase(TypeQueryBuilder):
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
        
    # to safely close database
    def __del__(self) -> None:
        """
        Rolls back any uncommited transactions on garbage collection
        """
    
    def reload_tables(self):
        """reloads the tables in the database"""

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
        
    def logger(self, statement: str) -> None:
        """used to log queries

        Args:
            statement (str): SQL statement
        """

    # DATABASE CONNECTION CONFIGURATION
    # allow drop
    def allow_drop(self, allow: bool) -> None:
        """allows or bans DROP like statements

        Args:
            allow (bool): wether DROP is banned
        """

    # enable error catching on queries
    def error_catch(self, enable: bool, logging: bool = False) -> None:
        """enables wether errors are caught on queries

        Args:
            enable (bool): True if errors should be caught False if they should be raised
            logging (bool, optional): True if errors are logged to console False if not. Defaults to False.
        """

    def query_logging(self, enable: bool, func: Callable | None = None) -> None:
        """Enables or disables all queries executed on database being logged to console

        Args:
            enable (bool): True if query logging otherwise False
            func (Callable | None, optional): function used to log queries. Defaults to None.
        """

    #allows dev to set the row factory
    def row_factory(self, factory: Row | Callable = Row) -> None:
        """sets the row factory of the connection \n refer to SQLite3 documentation@https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory for more info

        Args:
            factory (sqlite3.Row | Callable, optional): function or sqlite3.Row class used for a row factory Defaults to sqlite3.Row.
        """

    def delete_checking(self, enable: bool = True) -> None:
        """Delete checking creates a temporary copy of a table before executing a delete statement, it will check that the table still exists after the delete statement \n
        This can be computationally expensive for very large tables.s

        Args:
            enable (bool, optional): True if every DELETE statement is checked for danger otherwise False. Defaults to True.
        """

    # add a banned statement
    def add_banned_statement(self, statement: str | Iterable[str]) -> None:
        """If a statement is added it means it cannot be run on the database unless it is removed with remove_banned_statement()

        Args:
            statement (str | Iterable[str]): statement type that is banned
        """

    # remove banned statement
    def remove_banned_statement(self, statement: str | Iterable[str]) -> None:
        """Allows a once banned statement to be executed on the database

        Args:
            statement (str | Iterable[str]): statement type to un-ban
        """

    # add a banned syntax
    def add_banned_syntax(self, syntax: str | Iterable[str]) -> None:
        """If some syntax is added it means it cannot be run on the database unless it is removed with remove_banned_syntax()

        Args:
            syntax (str | Iterable[str]): syntax to ban
        """
        
    # remove banned syntax
    def remove_banned_syntax(self, syntax: str | Iterable[str]) -> None:
        """Allows a once banned SQL syntax to be executed on the database

        Args:
            syntax (str | Iterable[str]): syntax to unban
        """

    def backup(self, path: str = "", extension: str = "db") -> str:
        """Creates a backup of the database as path/time.extension ("/time.db" by default) where time us the time of the backup

        Args:
            path (str, optional): path to save to. Defaults to "".
            extension (str, optional): file extension formated as "extension" NOT ".extension". Defaults to "db".

        Returns:
            str: path it was saved to
        """

    def is_dangerous_delete(self, request: str, parameters=()) -> bool:
        """used to check if a DELETE statement is dangerous (wether it deletes the whole table)

        Args:
            request (str): request to check
            parameters (tuple, optional): request parameters. Defaults to ()

        Returns:
            bool: wether it is dangerous or not
        """
        
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