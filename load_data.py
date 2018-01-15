import xml.etree.cElementTree as ET
import re
import sqlite3
import argparse
import unicodecsv as csv
from db_setup import get_path_to_db

PATH = 'maps/{file}-map.xml'
TABLES = [
    'nodes',
    'nodes_tags',
    'ways',
    'ways_tags',
    'ways_nodes'
]
CSV_FORMAT = 'data/{file}.csv'

nodes = []
node_tags = []
ways = []
way_tags = []
way_nds = []

# Modified RE for lower colon to match on numbers and upper case before and after colon
LOWER_COLON = re.compile(r'^([a-zA-Z]|_)*:([a-zA-Z0-9]|_)*$')
PROBLEMCHARS = re.compile(r'[=\+&<>;\'"\?%#$@\,\. \t\r\n]')


def build_node(node):
    node_id = node.get('id')

    for tag in node.iter('tag'):
        node_tags.append(build_tag_elem(tag, node_id))

    return {
        "id": node_id,
        "lat": node.get('lat'),
        "lon": node.get('lon'),
        "user": node.get('user'),
        "uid": node.get('uid'),
        "version": node.get('version'),
        "changeset": node.get('changeset'),
        "timestamp": node.get('timestamp')
    }


def build_way(way):
    way_id = way.get('id')

    for tag in way.iter('tag'):
        way_tags.append(build_tag_elem(tag, way_id))

    position = 0
    for nd in way.iter('nd'):
        way_nds.append(build_way_nd(nd, way_id, position))
        position += 1

    return {
        "id": way_id,
        "user": way.get('user'),
        "uid": way.get('uid'),
        "version": way.get('version'),
        "changeset": way.get('changeset'),
        "timestamp": way.get('timestamp')
    }


def build_tag_elem(tag, parent_id):
    if LOWER_COLON.match(tag.get('k')):
        return {
            "id": parent_id,
            "key": tag.get('k').split(':', 1)[1],
            "value": tag.get('v'),
            "type": tag.get('k').split(':', 1)[0]
        }
    elif PROBLEMCHARS.match(tag.get('k')):
        return None
    else:
        return {
            "id": parent_id,
            "key": tag.get('k'),
            "value": tag.get('v'),
            "type": 'regular'
        }


def build_way_nd(way_nd, way_id, position):
    node_id = way_nd.get('ref')
    return {
        "id": way_id,
        "node_id": node_id,
        "position": position
    }


def write_to_csv(file, object):
    """
    Take an object that has been created by processing OSM XML data and convert to a CSV
    Used to persist manipulated data before loading to the local database
    :param file: name of the file to be created
    :param object: the list of dictionaries that will be written to csv
    :return: None
    """

    keys = object[0].keys()
    with open(CSV_FORMAT.format(file=file), 'wb') as output:
        dict_writer = csv.DictWriter(output, keys)
        dict_writer.writeheader()
        dict_writer.writerows(object)


def clear_db():
    """
    Loop through every table in the database definition and clear out all old data
    Run through at the start of every data load to ensure a clean slate
    """
    with sqlite3.connect(get_path_to_db()) as conn:
        c = conn.cursor()

        for table in TABLES:
            c.execute('DELETE FROM {table}'.format(table=table))

        conn.commit()


def import_csvs_to_db():
    """
    Loop through all the table files that have previously been created
    Convert them from csv to list of dicts
    Send them to db writers to create the appropriate entries in the db
    :return: None
    """
    for file in TABLES:
        input_object = []
        with open(CSV_FORMAT.format(file=file), 'rb') as input:
            for row in csv.DictReader(input):
                input_object.append(row)

        write_to_db(file, input_object)


def write_to_db(table, object):
    """
    Get all target CSVs from current working directory and import to db
    """
    with sqlite3.connect(get_path_to_db()) as conn:
        c = conn.cursor()

        # break dictionary apart into multiple rows, split out columns and insert values using placeholder tags
        for row in object:
            columns = ', '.join(row.keys())
            placeholders = ', '.join('?' * len(row))
            sql = 'INSERT INTO {table} ({col}) VALUES ({place})'.format(table=table, col=columns, place=placeholders)
            c.execute(sql, row.values())

        conn.commit()


def process_file(location):
    """
    Processes the xml OSM data for the desired location, creates appropriate objects, and inserts into the db tables
    :param location: name of the desired location file (minus -map.xml suffix)
    :return: None
    """
    print('Processing data for {location}'.format(location=location))

    for event, elem in ET.iterparse(PATH.format(file=location), events=('start',)):
        if elem.tag == 'node':
            nodes.append(build_node(elem))
        elif elem.tag == 'way':
            ways.append(build_way(elem))

    print('Nodes:', len(nodes))
    print('Node Tags:', len(node_tags))

    print('Ways:', len(ways))
    print('Way Tags:', len(way_tags))
    print('Way Nodes:', len(way_nds))

    # create the required CSV files from the current dictionaries
    write_to_csv('nodes', nodes)
    write_to_csv('nodes_tags', node_tags)
    write_to_csv('ways', ways)
    write_to_csv('ways_nodes', way_nds)
    write_to_csv('ways_tags', way_tags)

    # clean out all existing data from the db
    clear_db()

    # loop through the csvs on disk and insert into the DB
    import_csvs_to_db()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Specify what location is desired to be imported.')
    parser.add_argument('--location', dest='location')
    parser.set_defaults(location='marin-county')

    args = parser.parse_args()

    process_file(args.location)
