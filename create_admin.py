from codegen import generate_code
from queries_db import add_row_users


code = generate_code()

add_row_users(code, 'Admin', '0', '11111111111', code, '0')

print(code)
