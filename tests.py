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
import os

passed_tests = 0
total_tests = 0

database = sql.Database(":memory:")
database.error_catch(False)

# Connect and executes queries on database
total_tests += 1
try:
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (1, 23, 'John')")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (2, 25, 'Jane')")
    if isinstance(database.query("SELECT * FROM people", save_data=True), list):
        print(f"TEST {total_tests}  passed ✅ can connect an execute queries")
        passed_tests += 1
    else:
        raise Exception("")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

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
        print(f"TEST {total_tests}  passed ✅ can configure if drop is enabled on database")
        passed_tests += 1
    else:
        raise Exception("")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

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
        print(f"TEST {total_tests}  passed ✅ can configure if queries are error caught")
        passed_tests += 1
    else:
        raise Exception("")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

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
    if initial_table_exists and table_exists != []:
        print(f"TEST {total_tests}  passed ✅ is basic injection proof")
        passed_tests += 1
    else:
        raise Exception("")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

# Can’t use DELETE FROM table WHERE 1=1; as an alternative to drop if DROP is not allowed on database
total_tests += 1
try:
    database.allow_drop(False)
    database.error_catch(True, True)
    database.query("CREATE TABLE IF NOT EXISTS toDrop (id, value)")
    initial_table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)

    database.query("INSERT INTO toDrop (id, value) VALUES (1, 2)", save_data=False)
    database.query("INSERT INTO toDrop (id, value) VALUES (2, 3)", save_data=False)
    table_exists = database.query("SELECT * FROM toDrop")
    print(table_exists)

    database.query("DELETE FROM toDrop")
    table_exists = database.query("SELECT * FROM toDrop")
    print(table_exists)

    database.query("DELETE FROM toDrop WHERE true")
    table_exists = database.query("SELECT * FROM toDrop")
    print(table_exists)

    database.query("DELETE FROM toDrop WHERE 2=2")
    table_exists = database.query("SELECT * FROM toDrop")
    print(table_exists)
    if initial_table_exists and table_exists != []:
        print(f"TEST {total_tests}  passed ✅ can't delete a whole table when DROP is disabled")
        passed_tests += 1
    else:
        raise Exception("")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

# Can’t run more than one statement on a query that is labelled as single statement
total_tests += 1
try:
    database.error_catch(False)
    try:
        database.query("SELECT * FROM people; SELECT * FROM people")
    except:
        test_pass = True
    database.multi_query("SELECT * FROM people; SELECT * FROM people")
    if test_pass:
        print(f"TEST {total_tests}  passed ✅ can't run more than one statement with query() method")
        passed_tests += 1
    else:
        raise Exception("")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

# Configure banned statements
total_tests += 1
try:
    database.add_banned_statement("SELECT")
    try:
        data = database.query("SELECT * FROM people")
    except:
        test_pass = True

    database.remove_banned_statement("SELECT")
    data = database.query("SELECT * FROM people")

    if test_pass:
        print(f"TEST {total_tests}  passed ✅ can set banned staements")
        passed_tests += 1
    else:
        raise Exception("")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

# row factory
total_tests += 1
try:
    database.row_factory(sql.sqlite3.Row)
    data = database.query("SELECT * FROM people")

    data[0]["id"]

    print(f"TEST {total_tests}  passed ✅ can set row factories")
    passed_tests += 1
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

# backup
total_tests += 1
try:
    if os.path.isfile('test.db'):
        os.remove('test.db')
    with open('test.db', 'x') as file:
        pass
    testdb = sql.Database('test.db')
    testdb.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    path = testdb.backup(os.path.dirname(os.path.abspath(__file__)))

    backupdb = sql.Database(path)
    backupdb.query("SELECT * FROM people")
    passed_tests += 1
    print(f"TEST {total_tests}  passed ✅ can create backups")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

# backup
total_tests += 1
try:
    CONFIG = \
    """
    {
        "allow_dropping": false,
        "check_delete_statements": true,
        "error_catching": false,
        "error_logging": false,
        "banned_statements": ["INSERT"],
        "banned_syntax": [],

        "default_query_logger": false,
        "default_row_factory": true
    }
    """
    database.import_configuration(json_string=CONFIG)

    database.query("CREATE TABLE IF NOT EXISTS toDrop (id, value)")

    try:
        database.query("DROP TABLE toDrop")
        test_passed = False
    except:
        test_passed = True

    try:
        database.query("INSERT INTO toDrop (id, value) VALUES (1, 'test')")
        test_passed = False
    except:
        pass

    if test_passed:
        passed_tests += 1
        print(f"TEST {total_tests} passed ✅ can import configuration")
    else:
        raise Exception("")
except Exception as e:
    print(f"TEST {total_tests} failed ❌: {e}")

database = None
testdb = None

try:
    os.remove(os.path.dirname(os.path.abspath(__file__)) + "\\test.db")
    os.remove(path)
except:
    pass

print(f"\nTESTING DONE \n{passed_tests}/{total_tests} passed {round((passed_tests/total_tests) * 100, 2)}%")
