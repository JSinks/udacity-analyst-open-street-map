import os
import sqlite3

CLEAN_FILE_NAME = 'db_schema_clean'
DB_NAME = 'osm-data'


def get_root():
    return os.path.dirname(os.path.abspath(__file__))


def get_path_to_db():
    return os.path.join(get_root(), 'db', '{db}.db'.format(db=DB_NAME))


def get_path_to_query(file):
    return os.path.join(get_root(), 'queries', '{file}.sql'.format(file=file))


def setup_db():
    # Setup an sqlite3 database as per the schema provided at:
    # https://gist.github.com/swwelch/f1144229848b407e0a5d13fcb7fbbd6f
    #
    # Credit to Stephen Welch (https://gist.github.com/swwelch) for db schema
    with sqlite3.connect(get_path_to_db()) as conn:
        c = conn.cursor()

        query_file = CLEAN_FILE_NAME

        #  Break the provided query file into individual queries
        with open(get_path_to_query(query_file), 'rb') as f:
            create_queries = str(f.read()).split(';')

        # Execute each query individually against the new database
        for query in create_queries:
            c.execute(query.strip())

        # Commit the transaction to the database to finalise creation of the tables
        conn.commit()


if __name__ == '__main__':
    setup_db()
