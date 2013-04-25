## clog.py

import logging
import sys

class ConsoleHandler(logging.StreamHandler):
    """A handler that logs to console in the sensible way.

    StreamHandler can log to *one of* sys.stdout or sys.stderr.

    It is more sensible to log to sys.stdout by default with only error
    (logging.ERROR and above) messages going to sys.stderr. This is how
    ConsoleHandler behaves.
    """

    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.stream = None # reset it; we are not going to use it anyway

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.__emit(record, sys.stderr)
        else:
            self.__emit(record, sys.stdout)

    def __emit(self, record, strm):
        self.stream = strm
        logging.StreamHandler.emit(self, record)

    def flush(self):
        # Workaround a bug in logging module
        # See:
        #   http://bugs.python.org/issue6333
        if self.stream and hasattr(self.stream, 'flush') and hasattr(self.stream,'closed') and not self.stream.closed:
            logging.StreamHandler.flush(self)



class MyLogger(logging.Logger):
    def info(self, what, *a, **b):
        return logging.Logger.info(self, '[pbj] ' + what, *a, **b)
    def base_logger(self, *a, **b):
        return logging.Logger.info(self, *a, **b)
    def error(self, what, *a, **b):
        return logging.Logger.error(self, '[pbj][error] ' + what, *a, **b)

LOG = MyLogger('[pbj]')
LOG.addHandler(ConsoleHandler())
