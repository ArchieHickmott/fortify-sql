from quicksqlite import Database, Table, column

database = Database("test_database.db")

table = Table([
    column("Id", type="INTEGER", primary=True, check="Id > 0"),
    column("age", "INTEGER", check="age > 0"),
    column("name", type="TEXT", not_null=True, unique=True)
])

database.new_table("myTable", table)

