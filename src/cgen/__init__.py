import logging
import sys

from .cgen import cgen


def main() -> None:
    try:
        result = cgen()
    except Exception as error:
        logging.fatal(error)
        result = 1
    sys.exit(result)
