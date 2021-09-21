from pathlib import Path

from tinydb import TinyDB
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from default_logger.defaultLogger import defaultLogger

from functools import wraps
import time
from math import ceil


def Json_DB(*paths):
    serializationMiddleware = SerializationMiddleware(JSONStorage)
    serializationMiddleware.register_serializer(DateTimeSerializer(), 'TinyDate')

    storage = (CachingMiddleware(serializationMiddleware))

    return TinyDB(Path(*paths), storage=storage)


def list_json_dbs(path, BLACKLIST=["visited.json"]):
    _blacklist_filter = lambda x: len([bl for bl in BLACKLIST if bl in str(x)]) == 0
    return [x for x in Path(path).rglob('*.json') if _blacklist_filter(x)]


def walk_entries(path):
    for db_path in list_json_dbs(path):
        db = Json_DB(db_path)
        for entry in db.all():
            yield entry


def time_logger(**kwargs):
    logger = kwargs.get("logger", defaultLogger("Fashion Scrapper"))

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **inner_kwargs):
            startTime = time.time()
            name = kwargs.get("name", func.__name__)
            header = kwargs.get("header", None)
            footer = kwargs.get("footer", None)

            if header:
                header_msg = pad_str(header, **kwargs)
                logger.debug(header_msg, extra={'name_override': func.__name__})

            result = func(*args, **inner_kwargs)

            totalTime = time.time() - startTime

            logger.debug(f"[{name}] Elapsed Time: {totalTime}s", extra={'name_override': func.__name__})

            if footer:
                footer_msg = pad_str(footer, **kwargs)
                logger.debug(footer_msg, extra={'name_override': func.__name__})
            return result

        return wrapper

    return decorator


def pad_str(msg, **kwargs):
    length = kwargs.get("padding_length", 32)
    symbol = kwargs.get("padding_symbol", "*")

    symbol_count = ceil((length - len(msg)) / 2) - 1

    symbols = symbol * symbol_count
    return f"{symbols} {msg} {symbols}"
