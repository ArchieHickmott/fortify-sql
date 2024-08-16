# Fortify SQL
A python library for easy SQL injection prevention. Designed arround the SQLite3 library. <br>

the main purpose of the library is to be a lightweight but secure SQL library. By security it means preventing from injections through both parameterisation and security rules. Some security rules include:
 
 - being able to limit one statement per query
 - banning DROP/similar statements from ever being executed in a connection
 - banning certain syntax from statements such as comments

these rules aim to provide a second layer of defense in a scenario when traditional sqli prevention fails/is incorrectly used


# Beta 0.4.1 New Features:
 - can use ORM instead of sql queries
 - the ORM imports the database and creates objects for all tables objects
 - these objects can be used to make queries without directly writing any SQL 
 - Pretty print method, it does what it says it does. Prints the table, prettily
 - started work on more comprehensive tests

## Quickstart
install using pip
```shell
pip install fortifysql
```
fortify is designed around the database class, start by importing fortifysql and specifying the path of the database to connect to
```python
from fortifysql import Database

database = Database("mydatabase.db")
```
and then to make requests:
```python
data = database.query("SELECT * FROM myTable")
```
Parameters are defined with a '?' in the request and are passed through in a tuple
```python
data = database.query("SELECT * FROM myTable WHERE id=?" (user_id,))
```
## Quickstart ORM
the ORM is fairly basic, no joins or DDL but. It's a DML with basic CRUD abilities.
To get data from a table
```python
data = database.mytable()
```
or
```python
data = database.mytable.get().all()
```
filters can be applied
```python
data = database.mytable.get().filter(col1=3).all()
```
the table attributes are created when the database is imported so don't worry if your syntax highlighting doesn't show it existing, if you want syntax highlighting it can be done in two ways

1: type annotations
```python
from fortifysql import Database, Table
db = Database("mydb.db")
my_table: Table = db.mytable
my_other_table: Table = db.other_table
```
2: Custom database class
```python
from fortifysql import Database, Table

MyDatabase(Database):
    my_table: Table
    my_other_table: Table

db = MyDatabase("mydb.db")
```