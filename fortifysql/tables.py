def column(name, type=False, primary=False, unique=False, not_null=False, default=False, check=False):
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
    constraints = []
    skeleton = []

    # Creating a new table
    def __init__(self, columns: list):
        for column in columns:
            self.skeleton.append(column)
    
    def add_primary(self, column, conflict: str=False):
        for constraint in self.constraints:
            if "PRIMARY KEY" in constraint:
                raise Exception("FortifySQL error - Table can only have one Primary key")
        if conflict:
            self.constraints.append(f"PRIMARY KEY ({column}) ON CONFLICT {conflict}")
        else:
            self.constraints.append(f"PRIMARY KEY ({column})")
    
    def add_unique(self, column, conflict=False):
        if conflict:
            self.constraints.append(f"UNIQUE ({column}) ON CONFLICT {conflict}")
        else:
            self.constraints.append(f"UNIQUE ({column})")
    
    def add_check(self, check: str):
        self.constraints.append(f"CHECK ({check})")
    
    def add_foreign_key(self, child_column, parent_column, external_table, clause=""):
        self.constraints.append(f"FOREIGN KEY ({child_column}) REFERENCES {external_table}({parent_column}) {clause}")