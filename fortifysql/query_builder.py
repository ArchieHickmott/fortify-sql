from typing import List, Self

from .database_map import Table, Column
from .sql_data_types import LogicalString, cast_sql_dtype
from .errors import SecurityError

class QueryBuilder:
    def select(self, table: Table, *args: Table | Column | str):
        """used to select data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        return Select(self).select(table, *args)
    
    def select_distinct(self, table: Table, *args: Table | Column | str):
        """used to select DISTINCT data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        return DistinctSelect(self).select(table, *args)        
    
    def insert(self, table: Table, *cols: List[Column | str], abort: bool=False, fail: bool=False, ignore: bool=False, replace: bool=False, rollback: bool=False):
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
        return Insert(self).insert(table, *cols, abort=abort, fail=fail, ignore=ignore, replace=replace, rollback=rollback)
    
    def update(self, table: Table, abort: bool=False, fail: bool=False, ignore: bool=False, replace: bool=False, rollback: bool=False):
        """ used to update data into the database, give table to update, use update().values(col==value,...) for the values to update

        Args:
            table (Table): table to update
            abort (bool, optional): SQL OR ABORT clause. Defaults to False.
            fail (bool, optional): SQL OR FAIL clause. Defaults to False.
            ignore (bool, optional): SQL OR IGNORE clause. Defaults to False.
            replace (bool, optional): SQL OR REPLACE clause. Defaults to False.
            rollback (bool, optional): SQL OR ROLLBACK clause. Defaults to False.
        """
        return Update(self).update(table, abort=abort, fail=fail, ignore=ignore, replace=replace, rollback=rollback)

    def delete(self, table: Table, expr: str = False):
        """deletes data from a table

        Args:
            table (Table): table to delete from
            expr (str, optional): WHERE expression to filter the data to be deleted. Defaults to False.

        Raises:
            SecurityError: if there is no WHERE clause and DROPPING is banned on database
        """
        return Delete(self).delete(table, expr)
    
class StatementType:
    def __init__(self, db):
        """create the statement

        Args:
            db (Database): FortiftSQL Database Class
        """
        self.db = db
        
    def __str__(self):
        return f'({self.build()})'

    def parameters(self, *args):
        return self.db.query(self.build(), args)
    
    def run(self):
        return self.db.query(self.build())
        
class Select(StatementType):
    __str_query: LogicalString = LogicalString("")
    __result_columns: LogicalString = LogicalString("")
    __result_tables: LogicalString = LogicalString("")
    __where_expr: LogicalString = LogicalString("")
    __group_expr: LogicalString = LogicalString("")
    __having_expr: LogicalString = LogicalString("")  
    __ordering_terms: LogicalString = LogicalString("")
    __limit_expr: int | LogicalString = None
        
    def select(self, table: Table, *args: List[Table | Column | str]):
        """used to select data from a table, can be combined with methods such as .where() \n
        e.g: select(table, table.c1, table.c2)

        Args:
            table (Table): table to select from
            *args (Column | str): columns to select from

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        tables_to_join = [table]
        join = list(args)
        for arg in args:
            if isinstance(arg, Table):
                tables_to_join.append(arg)
                join.remove(arg)
        if len(tables_to_join) == 1:
            join = False
        if args == ():
            args = "*"
        if join:
            self.__join(tables_to_join, False, join)
            return self
        self.__result_columns = LogicalString(", ".join(str(arg) for arg in args))
        self.__result_tables = table.name
        return self
    
    def __join(self, tables: List[Table], distinct: bool, args: List[Column | str]):
        """used to create a join query

        Args:
            tables (List[Table]): tables to join
            distinct (bool): whether it is DISTINCT or not
            *args: columns to SELECT
        """
        self.__result_columns = ", ".join(str(arg) for arg in args)
        self.__result_tables = ", ".join(table.name for table in tables)
        
    def where(self, expr: str):
        """used to add a WHERE clause to a statement

        Args:
            expr (str): expression for where clause

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        if self.__where_expr == LogicalString(""):
            self.__where_expr = expr    
        else:
            self.__where_expr += " AND " + expr
        return self    
    
    def _and(self, expr: str):
        """used to add a AND operator to a statement

        Args:
            expr (str): expression for AND clause

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        self.__where_expr += LogicalString(" ") & expr    
        return self  
    
    def _or(self, expr: str):
        """used to add a OR operator to a statement

        Args:
            expr (str): expression for OR clause

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        self.__where_expr += LogicalString(" ") | expr        
        return self
    
    def groupby(self, *args, having=""):
        """used to group data from a SQL statistical funtion

        Args:
            args (str): columns/aliases to group by
        """
        self.__group_expr = ", ".join(args)
        if having != "":
            self.__having_expr = having
        return self
    
    def order(self, *args):
        """used to determine the order that data is returned"""
        self.__ordering_terms = ", ".join(args)
        return self
        
    def limit(self, limit: str | int):
        """used to limit the amount of data returned
        
        Args:
            args (str, int): the maximum amount of rows that can be returned 
        """
        self.__limit_expr = limit
        return self
        
    def build(self) -> str:
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """
        self.__str_query = "SELECT " + self.__result_columns + " FROM " + self.__result_tables
        if self.__where_expr:
            self.__str_query += " WHERE " + self.__where_expr
        if self.__group_expr:
            self.__str_query += " GROUP BY " + self.__group_expr
        if self.__having_expr:
            self.__str_query += " HAVING " + self.__having_expr
        if self.__ordering_terms:
            self.__str_query += " ORDER BY " + self.__ordering_terms
        if self.__limit_expr:
            self.__str_query += " LIMIT " + self.__ordering_terms
        return str(self.__str_query)

class DistinctSelect(Select):    
    def build(self):
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """
        self.__str_query = "SELECT DISTINCT " + self._Select__result_columns + " FROM " + self._Select__result_tables
        if self._Select__where_expr:
            self.__str_query += " WHERE " + self._Select__where_expr
        if self._Select__group_expr:
            self.__str_query += " GROUP BY " + self._Select__group_expr
        if self._Select__having_expr:
            self.__str_query += " HAVING " + self._Select__having_expr
        if self._Select__ordering_terms:
            self.__str_query += " ORDER BY " + self._Select__ordering_terms
        if self._Select__limit_expr:
            self.__str_query += " LIMIT " + self._Select__ordering_terms
        return self.__str_query     

class Insert(StatementType):
    __header: LogicalString = LogicalString("")
    __values: LogicalString = LogicalString("")
    __conflict: LogicalString = LogicalString("")
    
    def insert(self, 
               table: Table, 
               *cols: List[Column | str],
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
        if cols == ():
            self.cols = table.columns
        else: 
            self.cols = cols
        cols = ', '.join(str(col.literal_name()) if isinstance(col, Column) else str(col) for col in self.cols)
        table = table.name
        or_clause = ""
        if abort:
            or_clause = "OR abort "
        if fail:
            or_clause = "OR fail "
        if ignore:
            or_clause = "OR ignore "
        if replace:
            or_clause = "OR replace "
        if rollback:
            or_clause = "OR rollback "
        self.__header = f"INSERT {or_clause}INTO {table} ({cols}) "
        return self
    
    def values(self, *args):
        """values to insert use like: \n
        .values(value,...)
        """
        self.__values = ""
        for arg in args:
            print(arg)
            print(type(arg))
            if isinstance(arg, QUERY_TYPES):
                self.__values += str(arg) + ', '
            else:
                self.__values += str(cast_sql_dtype(arg)) + ', '
        self.__values = self.__values.strip(', ')
        return self
    
    def conflict(self, conflict):
        """define what to do on a conflict"""
        self.__conflict = conflict
        return self
    
    def build(self):
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """
        self.__str_query = self.__header + " VALUES (" + self.__values + ") " + self.__conflict
        print(self.__str_query)
        return self.__str_query

class Update(StatementType):   
    __header: LogicalString = LogicalString("")
    __values: LogicalString = LogicalString("")
    __from: LogicalString = LogicalString("")
    __where: LogicalString = LogicalString("")
    
    def update(self, 
               table: Table, 
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
        table = table.name
        or_clause = ""
        if abort:
            or_clause = "OR abort "
        if fail:
            or_clause = "OR fail "
        if ignore:
            or_clause = "OR ignore "
        if replace:
            or_clause = "OR replace "
        if rollback:
            or_clause = "OR rollback "
        self.__header = f"UPDATE {or_clause} {table} "
        return self
    
    def values(self, *args):
        """what columns to update and the values to set them to, use like this:\n
        .values(table.col == 2, table.col2 == 3)

        Args:
            expressions (str): formatted like: column = value
        """
        exprs = []
        for expr in args:
            if "." in expr:
                exprs.append(expr[expr.find('.') + 1:])
            else:
                exprs.append(expr)
                
        self.__values = "SET " + ", ".join(str(expr) for expr in exprs)
        return self
    
    def where(self, expr: str):
        """UPDATE WHERE clause

        Args:
            expr (str): expression
        """
        if "." in expr:
            expr = expr[expr.find('.') + 1:]
        self.__where = expr
        return self
    
    def _from(self, expr: str):
        """UPDATE FROM clause

        Args:
            expr (str): expression
        """
        self.__from = expr
        
    def build(self):
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """
        from_ = " FROM " if self.__from else ""
        where_ = " WHERE " if self.__where else ""
        return self.__header + self.__values + from_ + self.__from + where_ + self.__where

class Delete(StatementType):
    __query: LogicalString = LogicalString("")
    
    def delete(self, table: Table, expr: str = False):
        """deletes data from a table

        Args:
            table (Table): table to delete from
            expr (str, optional): WHERE expression to filter the data to be deleted. Defaults to False.

        Raises:
            SecurityError: if there is no WHERE clause and DROPPING is banned on database
        """
        if expr:
            self.__query = f"DELETE FROM {table} WHERE {expr}"
            return self
        if self.db.allow_dropping:
            self.__query = f"DELETE FROM {table}"
            return self
        raise SecurityError(f"Attempted to execute dangerous statement: DELETE FROM {table}")
    
    def build(self):
        """builds the query based on the past method chain

        Returns:
            str: SQL query
        """
        return self.__query
    
QUERY_TYPES = (Select, DistinctSelect, Insert, Update, Delete, QueryBuilder, StatementType)