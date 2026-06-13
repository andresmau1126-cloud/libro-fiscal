import sqlite3 
conn=sqlite3.connect('backend/db.sqlite3') 
cur=conn.cursor() 
cur.execute('select email,nombre,rol,activo,is_superuser from usuarios where rol=" "admin') ; echo for row in cur.fetchall(): print(row) ; echo conn.close() ; C:\Users\MAURICIO\AppData\Local\Programs\Python\Python312\python.exe tmp_admin.py ; del tmp_admin.py
