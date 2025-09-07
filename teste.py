import sqlite3
database = sqlite3.connect("data/user.db")
cursor = database.cursor()
print(cursor.execute("SELECT * FROM Accounts").fetchall())
database.commit()
database.close()