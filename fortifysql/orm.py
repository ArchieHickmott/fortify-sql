from typing import Iterable

from sqlvalidator import format_sql

class OrmError(Exception):
    def __init__(self, msg):
        super().__init__(f"Error with FortifySQL ORM: {msg}")

class SelectError(OrmError):
    def __init__(self, msg):
        super().__init__(f"Error with Select statement: '{msg}'")

class Join:
    join_template = [False, ""]

    def __init__(
            self, 
            table: str, 
            expression: str="", 
            inner: bool=True, 
            left: bool=False, 
            right: bool=False, 
            outer: bool=False, 
            cross: bool=False, 
            natural: bool=False
        ):
        return self.join(table, expression, inner, left, right, outer, cross, natural)

    def join(
            self, 
            table: str, 
            expression: str="", 
            inner: bool=True, 
            left: bool=False, 
            right: bool=False, 
            outer: bool=False, 
            cross: bool=False, 
            natural: Iterable[str] | str=None
        ):
        if left or right or outer or cross or natural:
            inner = False

        if inner:
            self.__inner_join()
        if left:
            self.__left_join()
        if right:
            self.__right_join()
        if outer:
            self.__outer_join()
        if cross:
            self.__cross_join()
        if natural:
            self.__natural(table)
        
        if sum([inner, left, outer, right, cross, True if natural else False]) != 1: # checks if there is not only 1 type of join given
            raise SelectError(f""".join() method should have 1 type of join, no more, no less
                                .join('table2', 'table1.c1 = table2.c2') is valid (inner join by default)
                                .join('table2', 'table1.c1 = table2.c2', outer=True) is valid
                                .join('table2', 'table1.c1 = table2.c2', inner=True, left = True) is invalid
                                you provided these joins: ({"inner, " if inner else ""}{"left, " if left else ""}
                                {"right, " if right else ""}{"outer, " if outer else ""}{"cross, " if cross else ""}{"natural, " if natural else ""}""".rstrip(", "))

        if inner or left or right or outer or cross:
            self.__on(table, expression)
        return self

    def __inner_join(self):
        self.join_template[0] = True
        self.join_template[1] += "INNER JOIN "
        return self

    def __left_join(self):
        self.join_template[0] = True
        self.join_template[1] += "LEFT JOIN "
        return self

    def __right_join(self):
        self.join_template[0] = True
        self.join_template[1] += "RIGHT JOIN "
        return self

    def __outer_join(self):
        self.join_template[0] = True
        self.join_template[1] += "FULL OUTER JOIN "
        return self

    def __natural(self, table):
        self.join_template[0] = True
        self.join_template[1] += f"NATURAL JOIN {table}"
        return self

    def __cross_join(self):
        self.join_template[0] = True
        self.join_template[1] += "CROSS JOIN "
        return self

    def __on(self, table, expr: str):
        self.join_template[1] += " " + table + " ON " + expr + " "
        return self

class Select(Join):
    """
    used by the ORM class used to build SQLite SELECT queries 
    """
    header = ""
    table = ""
    where_clause = ""
    footer = ""

    #declarations

    def __init__(self):
        return None

    parameters: None | tuple | dict = None

    def select(self, table: str = "", *args):
        if args == ():
            args = "*"
        cols = []
        for arg in args:
            if isinstance(arg, Iterable) and not isinstance(arg, str):
                for x in arg:
                    cols.append(x)
            else:
                cols.append(arg)
        if isinstance(cols, Iterable) and not isinstance(cols, str):
            cols = ''.join(f"{col}, " for col in cols).rstrip(", ")
        self.header += f"SELECT {cols} FROM {table} "
        return self
    
    def select_distinct(self, table: str = "", *args):
        if args == ():
            args = "*"
        if args is None:
            args = "*"
        cols = []
        for arg in args:
            if isinstance(arg, Iterable) and not isinstance(arg, str):
                for x in arg:
                    cols.append(x)
            else:
                cols.append(arg)
        if isinstance(cols, Iterable) and not isinstance(cols, str):
            cols = ''.join(f"{col}, " for col in cols).rstrip(", ")
        self.header += f"SELECT DISTINCT {cols} FROM {table} "
        return self

    def where(self, expr: str = ""):
        self.where_clause += f"WHERE {expr}"
        return self

    def and_(self, expr: str = ""):
        self.where_clause += f"AND {expr} "
        return self
    
    def or_(self, expr: str = ""):
        self.where_clause += f"AND {expr} "
        return self

    def params(self, *args, **kwargs):
        if args != ():
            self.parameters = args
        elif kwargs != {}:
            self.parameters = kwargs
        else:
            raise SelectError(f""".params() method cannot have keyword arguments and positional arguments 
                                .params(1, 2, 3) is valid
                                .params(age=1, name="John") is valid
                                .params(1, 2, name="John) is invalid
                                
                                the positional arguments passed {'(' + ''.join(f'{arg}, ' for arg in args).rstrip(', ') + ')'}
                                the keyword arguments passed {'(' + ''.join(f'{kwarg[0]}={kwarg[1]}, ' for kwarg in kwargs.items()).rstrip(', ') + ')'}""")
        return self

    def append(self, text: str):
        self.footer += text + " "
        return self

    def order_by(self, cols: str | Iterable[str], ascending=True):
        if isinstance(cols, Iterable) and not isinstance(cols, str):
            cols = ''.join(f"{col}, " for col in cols).rstrip(", ")
        order = " ASC " if ascending else " DESC "
        self.footer += " ORDER BY " + cols + order
        return self

    def having(self, expression):
        self.where_clause += "HAVING " + expression + " "
        return self

    def group(self, *args):
        cols = ""
        for arg in args:
            cols += arg + ", "
        cols = cols.rstrip(", ") + " "
        self.where_clause
        return self

    def reset(self):
        self.header = ""
        self.table = ""
        self.where_clause = ""
        self.footer = ""
        self.parameters = None
        self.join_template = [False, ""]
    
# print(Orm().select('table', "mycolumn", "supercolumn", ('c1', 'c2'))
#             .join('table2', 'table.c1 = table2.c2')
#             .order_by("table.c1")
#             .where("tablec1 = 'true'"))