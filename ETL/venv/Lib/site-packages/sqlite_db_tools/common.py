import sqlite3


def open_connection(db_location):
    db = sqlite3.connect(db_location)
    # Make row dict/tuple type
    db.row_factory = sqlite3.Row
    print('Opened database at: {}'.format(db_location))
    return db
