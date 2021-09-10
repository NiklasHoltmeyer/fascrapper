import logging
import sys


def defaultLogger(name, level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)],
                  format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'):
    logging.basicConfig(level=level, format=format, handlers=handlers)

    logger = logging.getLogger(name)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("nltk_data").setLevel(logging.WARNING)
    logging.getLogger("pysndfx").setLevel(logging.WARNING)

    return logger