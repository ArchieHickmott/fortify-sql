"""
Testing script to verify library works
"""
from fortifysql import Database, sqlite3

database = Database("pm_database.db")
database.error_catch(False, True)
database.allow_drop(False)
database.add_banned_statement(["DELETE", "INSERT"])
database.row_factory(sqlite3.Row)


# state = input("what state do you want? ")
# results = database.query("SELECT * FROM prime_minister WHERE state_rep = ? ORDER BY pm_name;", (state,))
# for row in results:
#     print(row["pm_name"], "represented", row["state_rep"])
s = input("Enter a string to search for in the name: ")
data = database.query("SELECT * FROM prime_minister WHERE pm_name LIKE ?", (f'%{s}%',))

if len(data) > 0:
    for row in data:
        print(row["pm_name"])
else:
    print("No Results Found")