import sqlite3
from sqlite_db_tools.common import open_connection
import sys
import os


class Migration():

    def __init__(self, source, destination, table):
        self.src_db = source
        self.dest_db = destination
        self.source_table = table
        self.dest_table = table
        self.autoincrement = False
        self.auto_field = 'id'
        self.source = open_connection(self.src_db)
        self.dest = open_connection(self.dest_db)

    def copy_table(self):
        src_data = self.source.execute('select * from ' + self.source_table)
        for row in src_data.fetchall():
            cols = tuple([key for key in row.keys()])
            # Create basic insert statement that will be populated with values
            ins = 'INSERT OR REPLACE INTO {} {} VALUES ({})'.format(
                self.dest_table, cols, ','.join(['?'] * len(cols))
            )
            # values = [row[c] for c in cols]
            values = []
            for c in cols:
                if self.autoincrement is True and c == self.auto_field:
                    values.append(None)
                else:
                    values.append(row[c])
            self.dest.execute(ins, values)
        self.dest.commit()
        self.source.close()
        self.dest.close()

    def copy_table_structure(self):
        # Copy schema from one table to another
        src_data = self.source.execute('select * from ' + self.source_table)


class Internal_Migration():

    def __init__(self, db, table1, table2):
        self.table1 = table1
        self.table2 = table2
        self.db = open_connection(db)
        self.autoincrement = False
        self.auto_field = 'id'

    def close(self):
        self.db.close()

    def copy_table(self):
        src_data = self.db.execute('select * from ' + self.table1)
        for row in src_data.fetchall():
            cols = tuple([key for key in row.keys()])
            # Create basic insert statement that will be populated with values
            ins = 'INSERT OR REPLACE INTO {} {} VALUES ({})'.format(
                self.table2, cols, ','.join(['?'] * len(cols))
            )
            # values = [row[c] for c in cols]
            values = []
            for c in cols:
                if self.autoincrement is True and c == self.auto_field:
                    values.append(None)
                else:
                    values.append(row[c])
            self.db.execute(ins, values)
        self.db.commit()

    def copy_schema(self):
        query = (
            'pragma table_info("{}")'
        ).format(self.table1)
        results = self.db.execute(query).fetchall()
        for row in results:
            print([c for c in row])
