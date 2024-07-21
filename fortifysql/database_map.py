"""
Used to map a database in python
"""
from typing import List
import sqlite3

from .sql_data_types import get_dtype, LogicalString, primitives
from .fortify_typing import TypeDatabase, TypeInsert, TypeDistinctSelect, TypeSelect, TypeUpdate, TypeDelete

import sqlparse     

class Column: ... # first defined here for typechecking

class Table:
    def __init__(self, db: TypeDatabase, name: str, sql, tbl_name=""):
        """Used by FortifySQL ORM to represent a table

        Args:
            db (Database): what database the table is on
            name (str): name of the table
            sql (str): sql statement that creates the table
            tbl_name (str, optional): SQLite tbl_name variable Defaults to "".
        """
        self.name = name
        self.sql = sql
        self.tbl_name = tbl_name
        
        if db:
            self.db = db
        
        self.columns = self.__import_columns()
        for column in self.columns:
            exec(f"self.{column.name} = column")
         
    def __str__(self) -> str:
        """to convert to str datatype

        Returns:
            (str): SQL statement to create the table
        """
        return self.name
    
    def __call__(self, *args):
        if args == ():
            args = "*"
        else:
            args = "".join(f"{arg}, " for arg in args).strip(", ")
        query = f"SELECT {args} FROM {self.name}"
        return self.db.query(query)
    
    def select(self, *args) -> TypeSelect:
        """used to select data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        return self.db.select(self, *args)
    
    def select_distinct(self, *args) -> TypeDistinctSelect:
        """used to select DISTINCT data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        return self.db.select(self, *args)        
    
    def insert(self, *cols, abort: bool=False, fail: bool=False, ignore: bool=False, replace: bool=False, rollback: bool=False) -> TypeInsert:
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
        if cols == ():
            cols = self.columns
        return self.db.insert(self, *cols, abort=abort, fail=fail, ignore=ignore, replace=replace, rollback=rollback)
    
    def update(self, abort: bool=False, fail: bool=False, ignore: bool=False, replace: bool=False, rollback: bool=False) -> TypeUpdate:
        """ used to update data into the database, give table to update, use update().values(col==value,...) for the values to update

        Args:
            table (Table): table to update
            abort (bool, optional): SQL OR ABORT clause. Defaults to False.
            fail (bool, optional): SQL OR FAIL clause. Defaults to False.
            ignore (bool, optional): SQL OR IGNORE clause. Defaults to False.
            replace (bool, optional): SQL OR REPLACE clause. Defaults to False.
            rollback (bool, optional): SQL OR ROLLBACK clause. Defaults to False.
        """
        return self.db.update(self, abort=abort, fail=fail, ignore=ignore, replace=replace, rollback=rollback)

    def delete(self, expr: str = False) -> TypeDelete:
        """deletes data from a table where the row fufils the expression

        Args:
            table (Table): table to delete from
            expr (str, optional): WHERE expression to filter the data to be deleted. Defaults to False.

        Raises:
            SecurityError: if there is no WHERE clause and DROPPING is banned on database
        """
        print(expr)
        return self.db.delete(self, expr)
    
    # TODO: create docstring
    def __import_columns(self) -> List[Column]:
        cursor = self.db.conn.execute(f'PRAGMA table_info({self.name})')
        data = cursor.fetchall()
        column_info = [[row[1], row[2]] for row in data]
        column_info = [(column_info[n][0], get_dtype(column_info[n][1])) for n, column in enumerate(column_info)]

        columns = []
        for column in column_info:
            columns.append(Column(column[0], column[1], self))  
        return columns          

class Column:
    def __init__(self, name: str, dtype, table: Table):
        """Used to represent a column in the FortifySQL ORM

        Args:
            name (str): name of the column
            dtype (SQLite data type): data type of the column
            table (Table): FortifySQL Table class
        """
        self.name = name
        self.dtype = dtype
        self.table = table
    
    def __call__(self):
        data = self.table.db.select(self.table, self).run()
        data = [row[0] for row in data]
        return data
            
    
    def __str__(self) -> LogicalString:
        """used for str(Column())

        Returns:
            str: name of the column
        """
        return LogicalString(f"{self.table.name}.{self.name}")
    
    def __eq__(self, value: object) -> str:
        """used for query formatting i.e: table.where(column1 == column2)

        Args:
            value (object): what to test a column equals

        Returns:
            str: returns SQL expression
        """

        if isinstance(value, Column):
            return LogicalString(f"{self} = {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} = {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} = ?")

    def __le__(self, value: object):
        """used for query formatting i.e: table.where(column1 <= column2)

        Args:
            value (object): what to test a column <=

        Returns:
            str: returns SQL expression
        """
        if isinstance(value, Column):
            return LogicalString(f"{self} <= {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} <= {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} <= ?")

    def __ge__(self, value: object):
        """used for query formatting i.e: table.where(column1 >= column2)

        Args:
            value (object): what to test a column >=

        Returns:
            str: returns SQL expression
        """
        if isinstance(value, Column):
            return LogicalString(f"{self} >= {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} >= {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} >= ?")

    def __gt__(self, value: object):
        """used for query formatting i.e: table.where(column1 > column2)

        Args:
            value (object): what to test a column >

        Returns:
            str: returns SQL expression
        """

        if isinstance(value, Column):
            return LogicalString(f"{self} > {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} >= {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} > ?")

    def __lt__(self, value: object):
        """used for query formatting i.e: table.where(column1 < column2)

        Args:
            value (object): what to test a column <

        Returns:
            str: returns SQL expression
        """

        if isinstance(value, Column):
            return LogicalString(f"{self} < {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} < {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} < ?")

    def __ne__(self, value: object):
        """used for query formatting i.e: table.where(column1 != column2)

        Args:
            value (object): what to test a column !=

        Returns:
            str: returns SQL expression
        """
        if isinstance(value, Column):
            return LogicalString(f"{self} != {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} != {self.dtype(value)}")        
        if value == "?":
            return LogicalString(f"{self} != ?")
    
    def literal_name(self):
        return LogicalString(self.name)