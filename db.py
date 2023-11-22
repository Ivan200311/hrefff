import sqlite3

connect = sqlite3.connect("db.db")
cursor = connect.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS  "users" (
	"id"	INTEGER,
	"login"	TEXT,
	"password"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
''')

cursor.execute('''
 CREATE TABLE IF NOT EXISTS "links_types" (
	"id"	INTEGER,
	"type"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
''')
cursor.execute('''
 CREATE TABLE IF NOT EXISTS "links" (
	"id"	INTEGER,
	"link"	TEXT,
	"hreflink"	TEXT,
	"user_id"	INTEGER,
	"link_type_id"	INTEGER,
	"count"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
    FOREIGN KEY (user_id)  REFERENCES users (id),
    FOREIGN KEY (link_type_id)  REFERENCES links_types (id)
);
''')
connect.commit()


types = cursor.execute('''SELECT * FROM links_types''').fetchall()


if types==[]:
    cursor.execute('''INSERT INTO links_types(type) VALUES("Публичная")''')
    connect.commit()

    cursor.execute('''INSERT INTO links_types(type) VALUES("Общая")''')
    connect.commit()

    cursor.execute('''INSERT INTO links_types(type) VALUES("Приватная")''')
    connect.commit()