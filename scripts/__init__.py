import logging
import datetime as dt
from logging.handlers import RotatingFileHandler
formatter = logging.Formatter(
    "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

logger = logging.getLogger()
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)
streamhandler.setFormatter(formatter)

file_handler = RotatingFileHandler('RelapseDataFormatting_{}.log'.format(dt.datetime.now().date()),
                                   maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(streamhandler)
logger.setLevel(logging.INFO)