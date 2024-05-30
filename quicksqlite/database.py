"""
This script handles the interaction between python and the database
"""

import sqlite3
import os
import time

class Database:
    error_catch = True
    allow_dropping = False

    # initialise connection to database
    def __init__(self, path: str) -> None:
        if os.path.isfile(path):
            if "/" in path:
                self.name = path.rsplit('/', 1)[1]
            else:
                self.name = path
            self.path = path
            self.conn = sqlite3.connect(path)
            self.cur = None
            self.recent_data = None
        else:
            raise Exception("QuickSQLite error - Database does not exist.")

    # to safely close database
    def __del__(self) -> None:
        if self.cur is not None:
            self.cur.close()
        self.conn.close()

    # DATABASE CONNECTION CONFIGURATION
    #
    # allow drop
    def allow_drop(self, allow: bool) -> None:
        Database.allow_dropping = allow
    
    # allow drop
    def error_catching(self, allow: bool) -> None:
        Database.error_catch = allow

    # Excecutes a query on the database
    def query(self, request: str, save_data=False) -> list:
        self.cur = self.conn.cursor()
        self.cur.execute(request)
        self.conn.commit()
        data = self.cur.fetchall()
        self.cur.close()
        self.cur = None
        if save_data:
            self.recent_data = data
            return data

    
    def _conditional_error_catch(condition):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if condition:
                    try:
                        return func(self, *args, **kwargs)
                    except Exception as error:
                        print(f"QUICKSQLITE DATABASE ERROR, database: {self.path}, error: {error}")
                else:
                    return func(self, *args, **kwargs)
            return wrapper
        return decorator

    #wrapper to make a request that doesnt return data
    
    def _no_data(func):
        def wrapper(self, *args):
            query: str = func(self, *args)

            self.cur = self.conn.cursor()
            self.cur.execute(query)
            self.conn.commit()
            self.cur.close()
            self.cur = None
        return wrapper
    
    #wrapper to make a DROP request
    
    def _drop(func):
        def wrapper(self, *args):
            if self.allow_dropping:
                query: str = func(self, *args)
            else:
                query = "SELECT * WHERE 0;"

            self.cur = self.conn.cursor()
            self.cur.execute(query)
            self.conn.commit()
            self.cur.close()
            self.cur = None
        return wrapper

    # wrapper to make a request that returns data
    
    def _data(func):
        def wrapper(self, *args) -> list:
            query: str = func(self, *args)

            self.cur = self.conn.cursor()
            self.cur.execute(query)
            data = self.cur.fetchall()
            self.conn.commit()
            self.cur.close()
            self.cur = None
            self.recent_data = data
            return data
        return wrapper

    # C - create
    # r
    # u
    # d
    #
    # CREATE like statements
    # ----------------------
    #   
    # CREATE X INDEX X ON X(X)
    @_conditional_error_catch(error_catch)
    @_no_data
    def new_index(self, name: str, table: str, columns, unique: bool=True) -> str:
        if type(columns) is not str:
            columns = f"{', '.join(column for column in columns)}"
        return f"CREATE {'UNIQUE' if unique else ''} INDEX {name} ON {table} {columns};"
    
    # CREATE TABLE
    @_conditional_error_catch(error_catch)
    @_no_data
    def new_table(self, name: str, table, temp=False):
        arguments = ""
        for column in table.skeleton:
            arguments += f'{column}, '
        for constraint in table.constraints:
            arguments += f'{constraint}, '
        arguments = arguments[:-2]

        if arguments.count("PRIMARY KEY") > 1:
            raise Exception("QuickSqLite error - Table can only have one Primary key")
        
        if temp:
            q = f"CREATE TEMP TABLE IF NOT EXISTS {name} ({arguments});"
        else:
            q =f"CREATE TABLE IF NOT EXISTS {name} ({arguments});"
        print(q)
        return q
    
    @_conditional_error_catch(error_catch)
    @_no_data
    def new_trigger(self, name: str, trigger: str, table: str, action: str, temporary: bool=False):
        if temporary:
            return  f"""CREATE TEMPORARY TRIGGER IF NOT EXISTS {name}
                        {trigger} ON {table} BEGIN {action} END;"""
        return  f"""CREATE TRIGGER IF NOT EXISTS {name}
                    {trigger} ON {table} BEGIN {action} END;"""

    #insert like statements
    @_conditional_error_catch(error_catch)
    @_no_data
    def insert(self, table: str, columns, data):
        if type(columns) is not str:
            columns = f"{', '.join(column for column in columns)}" # format to string
        if type(data) is not str:
            data = f"{', '.join(x for x in data)}" # format to string
        return f"INSERT INTO {table} ({columns}) VALUES ({data});"
    
    @_conditional_error_catch(error_catch)
    @_data
    def insert_return(self, table: str, columns: str, data: str):
        if type(columns) is not str:
            columns = f"{', '.join(column for column in columns)}" # format to string
        if type(data) is not str:
            data = f"{', '.join(x for x in data)}" # format to string
        return f"INSERT INTO {table} ({columns}) VALUES ({data}) RETURNING * ;"

    # c
    # R - read
    # u
    # d
    #
    # SELECT like statements
    # SELECT X X FROM X WHERE X
    @_conditional_error_catch(error_catch)
    @_data
    def select(self, columns, table: str, where: str="1=1", keyword: str=None) -> str:
        # formating inputs
        if columns is not str: # if list/tuple used for columns then convert to string
            columns = f"{', '.join(column for column in columns).strip()}"
        else:
            columns = columns.strip()
        if keyword is str:
            keyword = keyword.strip()
        elif keyword is None:
            pass
        else:
            keyword_type = type(keyword)
            raise Exception(f"QuickSqLite error - keyword should be of type string, or Nonetype not {keyword_type}")
        
        # format and return  query
        return f"SELECT {keyword + ' ' if keyword is not None else ''}{columns} FROM {table} WHERE {where};"

    # SELECT X X FROM X WHERE X ORDER BY X
    @_conditional_error_catch(error_catch)
    @_data
    def select_orderby(self, columns, table, order: str, where: str="1=1", keyword: str=None) -> str:
        return (f"SELECT {keyword + ' ' if keyword is not None else ''}{columns} "
                f"FROM {table} WHERE {where} ORDER BY {order};")

    # SELECT X X FROM X WHERE X
    @_conditional_error_catch(error_catch)
    @_data
    def select_join(self, columns, tables, where: str="1=1", group=False, having=False, keyword=None) -> str:
        request_from = ""
        request_data = ""
        if not isinstance(columns, str):
            for column in columns:
                request_data += f"{column}, "
        if not isinstance(tables, str):
            for table in tables:
                request_from += f"{table}, "
        request_from = request_from[:-2]
        request_data = request_data[:-2]
        if not group and not having:  # SELECT FROM WHERE
            request = (f"SELECT {keyword + ' ' if keyword is not None else ''}{request_data} "
                       f"FROM {request_from} WHERE {where}")
        elif not having:  # SELECT FROM WHERE GROUP BY
            request = (f"SELECT {keyword + ' 'if keyword is not None else ''}{request_data} "
                       f"FROM {request_from} where {where} GROUP BY {group}")
        else:  # SELECT FROM WHERE GROUP BY HAVING
            request = (f"SELECT {keyword + ' ' if keyword is not None else ''}{request_data} "
                       f"FROM {request_from} WHERE {where} GROUP BY {group} HAVING {having};")
        return request

    # c
    # r
    # U - update
    # d
    #
    # UPDATE like statements
    @_conditional_error_catch(error_catch)
    @_no_data
    def update(self, columns: list, values: list, table: str, where: str="1=1") -> None:
        arguments = ""
        for column, data in zip(columns, values):
            arguments += f"{column}={data}, "
        arguments = arguments[:-2]
        return f"UPDATE {table} SET {arguments} WHERE {where};"
    
    @_conditional_error_catch(error_catch)
    @_data
    def update_return(self, columns: list, values: list, table: str, where: str="1=1") -> str:
        arguments = ""
        for column, data in zip(columns, values):
            arguments += f"{column}={data}, "
        arguments = arguments[:-2]
        return f"UPDATE {table} SET {arguments} WHERE {where} RETURNING *;"
    
    # c
    # r
    # u
    # D - delete
    #
    # DROP like statements
    @_conditional_error_catch(error_catch)
    @_drop
    def drop_table(self, table):
        return f"DROP TABLE IF EXISTS {table}"

    @_conditional_error_catch(error_catch)
    @_drop
    def drop_triger(self, trigger):
        return f"DROP TRIGGER IF EXISTS {trigger}"
    
    @_conditional_error_catch(error_catch)
    @_drop
    def drop_index(self, index):
        return f"DROP INDEX IF EXISTS {index}"
    
    # DELETE like statements
    @_conditional_error_catch(error_catch)
    @_no_data
    def delete(self, table, where="1=1"):
        return f"DELETE FROM {table} WHERE {where};"
    
    @_conditional_error_catch(error_catch)
    @_data
    def delete_return(self, table, where="1=1"):
        return f"DELETE FROM {table} WHERE {where} RETURNING *;"

    # non-crud methods
    #
    # database backups
    @_conditional_error_catch(error_catch)
    def backup(self, path):
        path = path + str(time.asctime().replace(":", "-") + ".db")
        print(path)
        with open(self.path, "rb") as src_file:
            with open(path, "wb") as dst_file:
                dst_file.write(src_file.read())