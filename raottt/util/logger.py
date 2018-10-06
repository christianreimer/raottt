"""
Logging
"""

import logging
import sys


def setup(lname='raottt.log',
          console_level=logging.INFO,
          file_level=logging.DEBUG):

    """Setup root logger"""

    fmt = '%(asctime)s %(process)d %(levelname)s %(message)s'

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(fmt))

    file_handler = logging.FileHandler(lname)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(logging.Formatter(fmt))

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
