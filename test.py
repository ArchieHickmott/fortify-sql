"""
Testing script to verify library works
"""

import sqlparse

request = "DELETE FROM mytable WHERE 1=1"
new_table = "supercali"
parsed = sqlparse.parse(request)[0]
if parsed.get_type() == "DELETE":
    token_list = sqlparse.sql.TokenList(parsed.tokens)
    for token in token_list:
        if token.value == "FROM":
            from_id = token_list.token_index(token)
            table = token_list.token_next(from_id)[1].value

query = request.replace(table, new_table)
print(query)