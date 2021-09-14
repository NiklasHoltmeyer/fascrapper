from pathlib import Path

from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer


def Json_DB(*paths):
    serialization = SerializationMiddleware(JSONStorage)
    serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

    return TinyDB(Path(*paths), storage=serialization)
