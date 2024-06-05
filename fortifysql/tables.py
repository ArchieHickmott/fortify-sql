"""
Contains functions and classes required to create a table using SQL, designed to pick up on basic errors such as multiple
primary keys existing on a single table
"""

def column(name, type=False, primary=False, unique=False, not_null=False, default=False, check=False):
    """
    returns the definition of a column with inputed constraints
    """
    VALID_TYPES =  ["INTEGER", "REAL", "NUMERIC", "BOOLEAN",
                    "TEXT", "VARCHAR", "CHAR",
                    "DATE", "TIME", "DATETIME", "TIMESTAMP",
                    "BLOB", "NULL"]
    constraints = []
    if type in VALID_TYPES:
        constraints.append(type)
    if primary:
        constraints.append("PRIMARY KEY")
    if unique and not primary:
        constraints.append("UNIQUE")
    if not_null:
        constraints.append("NOT NULL")
    if default:
        constraints.append(f"DEFAULT {default}")
    if check:
        constraints.append(f"CHECK ({check})")
    
    return f"{name} {' '.join(constraint for constraint in constraints)}"

class Table:
    """
    Class for configuring a SQL table
    """
    constraints = []
    skeleton = []

    # Creating a new table
    def __init__(self, columns: list) -> None:
        """
        Columns are made with the fortifysql.column() function
        """
        for column in columns:
            self.skeleton.append(column)
    
    def add_primary(self, column, conflict: str=False) -> None:
        """
        Adds primary key constraint
        """
        for constraint in self.constraints:
            if "PRIMARY KEY" in constraint:
                raise Exception("FortifySQL error - Table can only have one Primary key")
        if conflict:
            self.constraints.append(f"PRIMARY KEY ({column}) ON CONFLICT {conflict}")
        else:
            self.constraints.append(f"PRIMARY KEY ({column})")
    
    def add_unique(self, column, conflict=False) -> None:
        """
        Adds unique key constraint
        """
        if conflict:
            self.constraints.append(f"UNIQUE ({column}) ON CONFLICT {conflict}")
        else:
            self.constraints.append(f"UNIQUE ({column})")
    
    def add_check(self, check: str) -> None:
        """
        Adds a check constraint
        """
        self.constraints.append(f"CHECK ({check})")
    
    def add_foreign_key(self, child_column, parent_column, external_table, clause="") -> None:
        """
        Adds a foreign key constraint
        """
        self.constraints.append(f"FOREIGN KEY ({child_column}) REFERENCES {external_table}({parent_column}) {clause}")

    def create_query(self, name: str, temp=False) -> str:
        """
        Returns a string that is the query needed to create the configured table
        """
        arguments = ""
        for column in self.skeleton:
            arguments += f'{column}, '
        for constraint in self.constraints:
            arguments += f'{constraint}, '
        arguments = arguments[:-2]

        if arguments.count("PRIMARY KEY") > 1:
            raise Exception("fortifysql error - Table can only have one Primary key")
        
        if temp:
            q = f"CREATE TEMP TABLE IF NOT EXISTS {name} ({arguments});"
        else:
            q =f"CREATE TABLE IF NOT EXISTS {name} ({arguments});"
        return q