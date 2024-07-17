"""
Used to map a database in python
"""
from typing import List
import sqlite3

from .sql_data_types import get_dtype
from .sql_data_types import LogicalString

import sqlparse
        
primitives = (bool, str, int, float, type(None), complex)        

class Table:
    def __init__(self, db, name: str, sql, tbl_name=""):
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
    
    # TODO: create docstring
    def __import_columns(self):
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