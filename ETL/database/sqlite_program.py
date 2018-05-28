import sqlite3

"""	This is a database class to create new table , getting the timestamp message from server,
    retrieving maximum id within the databse , inserting new file and etc
"""
class Database:
    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(self.filename)

    def create_table(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS COMPANY
                                (ID INT PRIMARY KEY     NOT NULL,
                                NAME           TEXT    NOT NULL);''')
        print "Table created successfully";

    def get_timestamp_message(self,message):
        print message

    def insert(self, count, filename):
        self.conn.execute("INSERT INTO COMPANY (ID,NAME) VALUES(?, ?)", (count, filename))
        self.conn.commit()
        print "Records created successfully";

    def retrieve_max_id(self):
        cursor = self.conn.execute("SELECT MAX(ID) FROM COMPANY")
        max_id = cursor.fetchone()[0]
        print max_id;
        if max_id is not None:
            return max_id
        else:
            return 0

    def update(self, id,name):
        self.conn.execute("UPDATE COMPANY set NAME = ? where ID = ?", (name, id))
        self.conn.commit()
        print "Total number of rows updated :", self.conn.total_changes

    def delete(self, key):
        self.conn.execute("DELETE from COMPANY where ID = ?;", (key,))
        self.conn.commit()
        print "Total number of rows deleted :", self.conn.total_changes
