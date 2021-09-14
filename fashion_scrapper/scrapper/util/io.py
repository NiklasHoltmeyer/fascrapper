from pathlib import Path

from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer


def Json_DB(*paths):
    serialization = SerializationMiddleware(JSONStorage)
    serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

    return TinyDB(Path(*paths), storage=serialization)


def list_json_dbs(path, BLACKLIST=["visited.json"]):
    _blacklist_filter = lambda x: len([bl for bl in BLACKLIST if bl in str(x)]) == 0
    return [x for x in Path(path).rglob('*.json') if _blacklist_filter(x)]


def walk_entries(path):
    for db_path in list_json_dbs(path):
        db = Json_DB(db_path)
        for entry in db.all():
            yield entry
