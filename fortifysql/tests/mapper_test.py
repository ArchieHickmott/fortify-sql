from fortifysql.orm import Table, Column, Database
from fortifysql.sql_data_types import Integer, Text, Real, Blob
from fortifysql.sql_functions import max

def test_import_table():
    db = Database(":memory:")
    db.query("CREATE TABLE test (c1, c2 INTEGER, c3 REAL, c4 TEXT, c5 BlOB)")
    db.reload_tables()
    table = db.test 
    assert isinstance(table, Table)
    assert isinstance(table.c1, Column)
    assert isinstance(table.c2, Column)
    assert isinstance(table.c3, Column)
    assert isinstance(table.c4, Column)
    assert isinstance(table.c5, Column)
    assert isinstance(table.c1.dtype("1"), Text)
    assert isinstance(table.c2.dtype(1), Integer)
    assert isinstance(table.c3.dtype(1), Real)
    assert isinstance(table.c4.dtype("1"), Text)
    assert isinstance(table.c5.dtype(b'a'), Blob)

def test_get_method():
    db = Database(":memory:")
    db.query("CREATE TABLE test (c1, c2)")
    db.reload_tables()
    table: Table = db.test
    assert isinstance(table(), list)
    try: table()[0]
    except: pass
    else: raise Exception("table shouldn't have any data")
    db.query("INSERT INTO test VALUES ('1', '2')")
    db.query("INSERT INTO test VALUES ('3', '4')")
    db.query("INSERT INTO test VALUES ('5', '6')")
    assert table() == [('1','2'),('3','4'),('5','6')]
    assert table.get(table.c1).all() == [('1',), ('3',), ('5',)]
    assert table.get(max(table.c1)).all() == [('5',)]
    assert table.get(table.c1).filter(c1='5').all()[0] == (5,)
    assert table.get("c1").limit(2) == [('1',), ('2',)]
    assert table.get(table.c1).order("c1 DESC").all() == [('5',), ('3',), ('1',)]
    