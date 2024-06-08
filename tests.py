"""
Tests the features of FortifySQL:
•	Connect and executes queries on database
•	Allows devs to configure if DROP is allowed on database
•	Allows devs to configure if queries are error caught and printed to console
•	Includes secure features:
    o	Basic injection proof
    o	Can’t use DELETE FROM table WHERE 1=1; as an alternative to drop if DROP is not allowed on database
    o	Can’t run more than one statement on a query that is labelled as single statement
•	One line of code to execute a query

"""
import fortifysql as sql

passed_tests = 0
total_tests = 0

database = sql.Database("test_database.db")
database.error_catch(False)

# Connect and executes queries on database
total_tests += 1
try:
    if isinstance(database.query("SELECT * FROM people", save_data=True), list):
        print(f"TEST {total_tests} passed ✅")
        passed_tests += 1
    else:
        raise Exception("") 
except:
    print(f"TEST {total_tests} failed ❌")

# Allows devs to configure if DROP is allowed on database
total_tests += 1
try:
    database.allow_drop(False)
    database.query("CREATE TABLE IF NOT EXISTS toDrop (id, value)")
    initial_table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)

    try:
        database.query("DROP TABLE toDrop")
    except:
        pass
    table_exists1 = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)

    database.allow_drop(True)
    database.query("DROP TABLE toDrop")
    table_exists2 = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)

    if initial_table_exists != [] and table_exists1 != [] and table_exists2 == []:
        print(f"TEST {total_tests} passed ✅")
        passed_tests += 1
    else:
        raise Exception("") 
except:
    print(f"TEST {total_tests} failed ❌")

# Allows devs to configure if queries are error caught and printed to console
total_tests += 1
try:
    database.allow_drop(False)
    database.error_catch(True)
    database.query("DROP TABLE iuwhefiuw")

    database.error_catch(False)
    try:
        database.query("DROP TABLE iuwhefiuw")
        bad_no_error = True
    except:
        bad_no_error = False
    
    if not bad_no_error:
        print(f"TEST {total_tests} passed ✅")
        passed_tests += 1
    else:
        raise Exception("") 
except:
    print(f"TEST {total_tests} failed ❌")

# Basic injection proof
total_tests += 1
try:
    database.allow_drop(True)
    database.query("CREATE TABLE IF NOT EXISTS toDrop (id, value)")
    initial_table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)

    try:
        database.query("SELECT * FROM id WHERE id=?", ("1; DROP TABLE toDrop;"))
    except:
        pass
    table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)
    if initial_table_exists and table_exists:
        print(f"TEST {total_tests} passed ✅")
        passed_tests += 1
    else:
        raise Exception("") 
except:
    print(f"TEST {total_tests} failed ❌")

# Can’t use DELETE FROM table WHERE 1=1; as an alternative to drop if DROP is not allowed on database
total_tests += 1
try:
    database.allow_drop(False)
    database.error_catch(True, False)
    database.query("CREATE TABLE IF NOT EXISTS toDrop (id, value)")
    initial_table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)

    database.query("INSERT INTO toDrop (id, value) VALUES (1, 2)", save_data=False)
    database.query("INSERT INTO toDrop (id, value) VALUES (2, 3)", save_data=False)

    database.query("DELETE FROM toDrop")

    database.query("DELETE FROM toDrop WHERE true")

    database.query("DELETE FROM toDrop WHERE 2=2")

    table_exists = database.query("SELECT * FROM toDrop")
    if initial_table_exists and table_exists != []:
        print(f"TEST {total_tests} passed ✅")
        passed_tests += 1
    else:
        raise Exception("") 
except:
    print(f"TEST {total_tests} failed ❌")

# Can’t run more than one statement on a query that is labelled as single statement
total_tests += 1
try:
    database.error_catch(False)
    try:
        database.query("SELECT * FROM table2; SELECT * FROM table1")
    except:
        test_pass = True
    database.multi_query("SELECT * FROM table2; SELECT * FROM table1")
    if test_pass:
        print(f"TEST {total_tests} passed ✅")
        passed_tests += 1
    else:
        raise Exception("") 
except:
    print(f"TEST {total_tests} failed ❌")

# Configure banned statements
total_tests += 1
try:
    database.add_banned_statement("SELECT")
    data = database.query("SELECT * FROM people")

    
    if test_pass:
        print(f"TEST {total_tests} passed ✅")
        passed_tests += 1
    else:
        raise Exception("") 
except:
    print(f"TEST {total_tests} failed ❌")

database.allow_drop(True)
database.query("DROP TABLE IF EXISTS toDrop")
print(f"\nTESTING DONE \n{passed_tests}/{total_tests} passed {round((passed_tests/total_tests) * 100, 2)}%")