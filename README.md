# Fortify SQL
A python library for easy SQL injection prevention. Designed arround the SQLite3 python database library. <br>
Current features are:<br>
-	Connect and executes queries on database<br>
-	Allows devs to configure if DROP is allowed on database<br>
-	Allows devs to configure if queries are error caught and printed to console<br>
-	Includes secure features:<br>
    -	Basic injection proof<br>
    -	Can’t use DELETE FROM table WHERE 1=1; as an alternative to drop if DROP is not allowed on database<br>
    -	Can’t run more than one statement on a query that is labelled as single statement<br>
-	One line of code to execute a query<br>
-   Allow statements to be set as blocked by dev so they can’t be executed on the database

## What's New In Beta 0.4.0
 - Can connect to database in memory
 - tests.py has no requirements, other than FortifySQL of course
 - Improved documentation website
 - Errors no longer say FortifySQL, to prevent Error based information gathering
 - Can import database configurations from JSON file/string

## Quickstart
install using pip
```shell
pip install fortifysql
```
fortify is designed arround the database class, start by importing fortifysql and specifying the path of the database to connect to
```python
from fortifysql import Database

database = Database("mydatabase.db")
```
and then to make requests:
```python
data = database.query("SELECT * FROM myTable", save_data = True) # use save_data if you want any data from the request
```
Parameters are defined with a '?' in the request and are passed through in a tuple
```python
data = database.query("SELECT * FROM myTable WHERE id=?", save_data = True, (user_id,))
```
