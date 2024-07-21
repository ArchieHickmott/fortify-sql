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
from fortifysql import Database, sqlite3
import os

def test_basic_queries():
    database = Database(":memory:")
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (1, 23, 'John')")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (2, 25, 'Jane')")
    assert isinstance(database.query("SELECT * FROM people", save_data=True), list)

def test_drop_configuration():
    database = Database(":memory:")
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

    assert initial_table_exists != [] and table_exists1 != [] and table_exists2 == []

def test_error_catch():
    database = Database(":memory:")
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (1, 23, 'John')")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (2, 25, 'Jane')")
    database.allow_drop(False)
    database.error_catch(True)
    database.query("DROP TABLE iuwhefiuw")

    database.error_catch(False)
    try:
        database.query("DROP TABLE iuwhefiuw")
        bad_no_error = True
    except:
        bad_no_error = False

    assert not bad_no_error

def test_basic_injection():
    database = Database(':memory:')
    database.allow_drop(True)
    database.query("CREATE TABLE IF NOT EXISTS toDrop (id, value)")
    initial_table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)

    try:
        database.query("SELECT * FROM id WHERE id=?", ("1; DROP TABLE toDrop;"))
    except:
        pass
    table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True)
    assert initial_table_exists and table_exists != []

def test_delete_checking():
    database = Database(':memory:')
    database.allow_drop(False)
    database.error_catch(True, True)
    database.query("CREATE TABLE IF NOT EXISTS toDrop (id, value)")
    initial_table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True) == [('toDrop',)]

    database.query("INSERT INTO toDrop (id, value) VALUES (1, 2)", save_data=False)
    database.query("INSERT INTO toDrop (id, value) VALUES (2, 3)", save_data=False)

    database.query("DELETE FROM toDrop")
    
    database.query("DELETE FROM toDrop WHERE true")

    database.query("DELETE FROM toDrop WHERE 2=2")
    table_exists = database.query("SELECT name FROM sqlite_master WHERE type='table' AND name='toDrop'; ", save_data=True) == [('toDrop',)]
    
    assert initial_table_exists and table_exists
  
def test_banned_multi_query():
    database = Database(":memory:")
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (1, 23, 'John')")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (2, 25, 'Jane')")
    database.error_catch(False)
    try:
        database.query("SELECT * FROM people; SELECT * FROM people")
    except:
        test_pass = True
    database.multi_query("SELECT * FROM people; SELECT * FROM people")
    assert test_pass

def test_banned_statements():
    database = Database(":memory:")
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (1, 23, 'John')")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (2, 25, 'Jane')")
    database.add_banned_statement("SELECT")
    try:
        data = database.query("SELECT * FROM people")
    except:
        test_pass = True

    database.remove_banned_statement("SELECT")
    test_pass = database.query("SELECT * FROM people") != [] and test_pass

    assert test_pass

def test_row_factory():
    database = Database(":memory:")
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (1, 23, 'John')")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (2, 25, 'Jane')")
    database.row_factory(sqlite3.Row)
    data = database.query("SELECT * FROM people")
    data[0]["id"]

def test_backups():
    database = Database(":memory:")
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (1, 23, 'John')")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (2, 25, 'Jane')")
    if os.path.isfile('test.db'):
        os.remove('test.db')
    with open('test.db', 'x') as file:
        pass
    testdb = Database('test.db')
    testdb.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    path = testdb.backup(os.path.dirname(os.path.abspath(__file__)))

    backupdb = Database(path)
    backupdb.query("SELECT * FROM people")
    
    testdb.__del__()
    backupdb.__del__()
    os.remove('test.db')
    os.remove(path)
    

def test_json_config():
    database = Database(":memory:")
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

    assert test_passed

def test_orm_basic_select():
    database = Database(":memory:")
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (1, 23, 'John')")
    database.query("INSERT INTO people (Id, Age, Name) VALUES (2, 25, 'Jane')")
    database.reload_tables()
    database.select(database.people).run()
    database.select_distinct(database.people).run()
    test_passed = isinstance(database.select(database.people, database.people.Age).where(database.people.Age == 23).run(), list)
    assert test_passed

def test_full_crud():
    database = Database(":memory:")
    database.query("CREATE TABLE IF NOT EXISTS people (Id INTEGER PRIMARY KEY, Age INTEGER, Name TEXT)")
    database.reload_tables()
    people = database.people
    
    # Create
    database.insert(people).values(1, 23, 'John')
    database.insert(people).values(2, 25, 'Jane')
    
    # Read
    database.select(people).run()
    
    # Update
    database.update(people, abort=True).values(people.Age == 25).where(people.Age != 25)
    
    # Delete
    database.delete(people, people.Id == 2)

