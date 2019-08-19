import logging
import datetime as dt
from logging.handlers import RotatingFileHandler


formatter = logging.Formatter(
        "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.DEBUG)
streamhandler.setFormatter(formatter)

file_handler = RotatingFileHandler('RelapseDataFormatting_{}.log'.format(dt.datetime.now().date()),
                                   maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logging.basicConfig(format=formatter, handlers=[file_handler, streamhandler], level=logging.INFO)