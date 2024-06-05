<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]>      <html class="no-js"> <!--<![endif]-->
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>QUICKSQLITE | Documentation</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/styles/default.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/highlight.min.js"></script>
        <script>hljs.initHighlightingOnLoad();</script>

        <style>
            ol {
                counter-reset: item;
            }
            li {
                display: block;
            }
            ol > li {
                counter-increment: item;
            }
            ol > li::before {
                content: counters(item, ".") ". ";
                margin-left: -20px; 
            }
            ol ol {
                counter-reset: item;
            }
            ol ol > li {
                counter-increment: item;
            }
            ol ol > li::before {
                content: counters(item, ".") " ";
                margin-left: -20px; 
            }
            ol ol ol {
                counter-reset: item;
            }
            ol ol ol > li {
                counter-increment: item;
            }
            ol ol ol > li::before {
                content: counters(item, ".") " ";
                margin-left: -20px; 
            }
        </style>
    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="browsehappy">You are using an <strong>outdated</strong> browser. Please <a href="#">upgrade your browser</a> to improve your experience.</p>
        <![endif]-->
        
        <header>
            <h1><b>
                Quick SQL Lite (QuickSQLite)
            </b></h1>
            <p>
                python development tools for SQLite3. Includes automatic query building for most CRUD operations, Added security features and 
                database managment
            </p>
        </header>
        <nav>
            <ol>
                <li>Database connection/managment
                    <ol>
                        <li>Connecting</li>
                        <li>Error Catching</li>
                        <li>Allow Drop</li>
                    </ol>
                </li>
                <li>Invoking custom requests</li>
                <li>CRUD query building
                    <ol>
                        <li>Create
                        <ol>
                            <li>Insert</li>
                            <li>Create Table</li>
                        </ol>
                        </li>
                        <li>Read
                            <ol>
                                <li>Select</li>
                                <li>Select Order By</li>
                                <li>Select Join</li>
                            </ol>
                        </li>
                    </ol>
                </li>
            </ol>
        </nav>
        <script>
            function setIdsAndHrefs(ol, prefix) {
                const items = ol.children;
                for (let i = 0; i < items.length; i++) {
                    const li = items[i];
                    const id = prefix ? `${prefix}.${i + 1}` : `${i + 1}`;
                   
                    const a = document.createElement('a');
                    a.href = `#${id}`;
                    const textNode = li.firstChild;
                    if (textNode.nodeType === 3) { // Check if it's a text node
                        a.innerHTML = textNode.textContent;
                        textNode.replaceWith(a);
                    } else {
                        a.innerHTML = li.textContent;
                        li.innerHTML = '';
                        li.appendChild(a);
                    }
            
                    const nestedOl = li.querySelector('ol');
                    if (nestedOl) {
                        setIdsAndHrefs(nestedOl, id);
                    }
                }
            }  

            // Initialize hierarchical ids and href attributes for the top-level ol
            document.addEventListener('DOMContentLoaded', () => {
                const topOl = document.querySelector('nav > ol');
                setIdsAndHrefs(topOl, '');
            
                // Smooth scrolling function
                document.querySelectorAll('nav a').forEach(anchor => {
                    anchor.addEventListener('click', function(e) {
                        e.preventDefault();
            
                        const targetId = this.getAttribute('href').substring(1);
                        const targetElement = document.getElementById(targetId);
            
                        if (targetElement) {
                            const offset = getOffset(targetElement);
                            window.scrollTo({
                                top: offset.top,
                                behavior: 'smooth'
                            });
                        }
                    });
                });
            
                // Function to get offset of an element
                function getOffset(el) {
                    const rect = el.getBoundingClientRect();
                    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    return { top: rect.top + scrollTop, left: rect.left + scrollLeft };
                }
            });
        </script>
        <div id="1">
            <h2>Database connection/managment</h2>
            <p>
                It is recomended to import QuickSQLite as such:
                <pre><code class="python">
    from quicksqlite import Database, Table, column
                </code></pre>
            </p>
            <div id="1.1">
                <h3>Connecting</h3>
                <p>
                    connection to the database happens during the initialisation of the Database class. When creating the database class, the file path
                    for the database is passed through as the singular argument. e.g. 
                    <pre><code type="python">   database = Database("my-database-path.db")</code></pre>
                    The source code for the connection to the database is:
                    <pre><code class="python">
    def __init__(self, path: str) -> None:
    if os.path.isfile(path):
        if "/" in path:
            self.name = path.rsplit('/', 1)[1]
        else:
            self.name = path
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cur = None
        self.recent_data = None
    else:
        raise Exception("QuickSQLite error - Database does not exist.")
                    </code></pre>
                </p>
            </div>
            <div id="1.2">
                <h3>Error Catching</h3>
                <p>Error Catching in QuickSQLite is very simple. All it does is it wraps the query with an error catcher and prints any exceptions
                    that occur. Error catching is disabled by default, to enable/disable: 
                    <pre><code class="python">
    database = Database("mydb.db")
    database.error_catching(True) # enables error catching
    database.error_catching(False) # disables error catching
                    </code></pre>
                </p>
            </div>
            <div id="1.3">
                <h3>Allow Drop</h3>
                <p>Enabling Drop on a database will Allow SQL queries such as DROP DATABASE and DROP TABLE. If these queries are never going to be needed
                    to be excecuted with the Database class then Drop should be disabled:
                    <pre><code class="python">
    database = Database("mydb.db")
    database.allow_drop(True) # enables drop
    database.allow_drop(False) # disables drop
                    </code></pre>
                </p>
            </div>
        </div>
        <div id="2">
            <h2>Invoking custom requests</h2>
            <p>
                To invoke a custom SQL request the query method is used. The SQL request is passed as a string. If the request contains any data then
                the data is returned from the method. Example usage:
                <pre><code class="python">
    database.query("SELECT * FROM table1")
    # query: SELECT * FROM table1
    # output: all the data in table1

                </code></pre>
            </p>
        </div>
        <div id="3">
            <h2>CRUD query building</h2>
            <p>
                For all methods that are designated as CRUD query builders, they take arguments that depend on the query. They are excecuted onto
                the database, if there is any data, the data will be returned
            </p>
            <div id="3.1">
                <h3>Create</h3>
                <div id="3.1.1">
                    <h4>Insert</h4>
                    <p>
                        the insert() method takes 3 arguments <b>table, columns, data</b> where data is The query is built like:<br>
                        INSERT INTO <b>table</b> (<b>columns</b>) VALUES (<b>data</b>)<br>
                        If the insert_return() method is called everything else is the same except the query is built like: <br>
                        INSERT INTO <b>table</b> (<b>columns</b>) VALUES (<b>data</b>) RETURNING *<br>
                        this returns any data entered to the table
                    </p>
                    <p>
                        Example use cases:
                        <pre><code class="python">
    database.insert("myTable", "col1, col2, col3", "'val1', 'val2', 'val3'")
    # query: INSERT INTO myTable (col1, col2, col3) VALUES (val1, val2, val3)
    # returns: None

    database.insert("myTable", ['col1', 'col2', 'col3'], ["'val1'", "'val2'", "'val3'"])
    # query: INSERT INTO myTable (col1, col2, col3) VALUES (val1, val2, val3)
    # returns: None

    print(database.insert_return("myTable", "col1, col2, col3", "'val1', 'val2', 'val3'"))
    # query: INSERT INTO myTable (col1, col2, col3) VALUES ('val1', 'val2', 'val3') RETURNING *
    # returns: [('val1', 'val2', 'val3')]
                        </code></pre>
                    </p>
                </div>
                <div id="3.1.2">
                    <h4>
                        Create Table
                    </h4>
                    <p>
                        Table creation uses both the Database class and the Table class. The Table class is used to configure a table and its constraints
                        the Table class will check for basic errors in constraints such as multiple primary keys.<br>
                        The Table class is initiated with a list of columns, columns are generated by the column function.<br>
                        The column function takes a minumum of a name, but can be configured to have constraints, create a constraint by setting
                        the it to a value, by default all contraints are False:
                        <pre><code class="python">
    column("myColumnName", type="INTEGER", unique=True)
    # myColumnName INTEGER UNIQUE
    column("myColumnName", type="INTEGER", primary=True, check="myColumnName > 0")
    # myColumnName INTEGER PRIMARY KEY CHECK (myColumnName > 0)
                        </code></pre>
                        the possible constraints are:<br>
                        <ul>
                            <li style="display: revert">type, string of any valid SQLite type</li>
                            <li style="display: revert">primary, either True or False</li>
                            <li style="display: revert">unique, either True or False</li>
                            <li style="display: revert">not_null, either True or False</li>
                            <li style="display: revert">default, string, default value for column</li>
                            <li style="display: revert">check, any checkable SQLite statement</li>
                        </ul>
                    </p>
                    <p>
                        An example of how a table is created:
                        <pre><code class="python">
    table = Table([
        column("Id", type="INTEGER", primary=True, check="Id > 0"),
        column("age", "INTEGER", check="age > 0"),
        column("name", type="TEXT", not_null=True, unique=True)
    ])
                        </code></pre>
                        once a table is created, table constraints (slightly different to column contraints) can be configured
                        the possible table configuration methods:
                        <ul>
                            <li style="display: revert">Table.add_primary(column, conflict)</li>
                            <li style="display: revert">Table.add_unique(column, conflict)</li>
                            <li style="display: revert">Table.add_check(check)</li>
                            <li style="display: revert">Table.add_foreign_key(child_column, parent_column, table, clause)</li>
                        </ul>
                    </p>
                    <p>
                        Once a table is created and configured it can be commited to the database using the .new_table() method:
                        <pre><code class="python">
    database = Database("test_database.db")

    table = Table([
        column("Id", type="INTEGER", primary=True, check="Id > 0"),
        column("age", "INTEGER", check="age > 0"),
        column("name", type="TEXT", not_null=True, unique=True)
    ])

    database.new_table("myTable", table)
                        </code></pre>
                    </p>
                </div>                
            </div>
            <div id="3.2">
                <h3>Read</h3>
                <div id="3.2.1">
                    <h4>Select</h4>
                    <p>
                        Database.select() is a basic SELECT FROM WHERE query, it requires the columns and from arguments, where is optional by default it
                        is '1=1'. Example usage
                        <pre><code class="python">
    database.select("*", "myTable")
    # query: SELECT * FROM myTable
    # output: the whole table

    databse.select("id, name", "myTable", "id > 3")
    # query: SELECT id, name FROM myTable WHERE id > 3
    # output: the whole table
                        </code></pre>
                    </p>
                </div>
            </div>
        </div>
        <div id="4">
            <h2>Database managment</h2>
            <div id="4.1">
                <h4>
                    Create Index
                </h4>
                <p>
                    the Database.new_index() method requires a name, a table, and columns. Optional argument for unique indexes (true by default)
                </p>
            </div>
            <div id="4.2">


            </div>
        </div>
    </body>
</html>
