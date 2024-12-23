import logging
import sys

from .cgen import cgen


if __name__ == "__main__":
    try:
        result = cgen()
    except Exception as error:
        logging.fatal(error)
        result = 1
    sys.exit(result)
