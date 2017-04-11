import logging


class Stream2Logger(object):
    """Fake file-like stream object that redirects stdout/stderr writes to a logger instance"""

    def __init__(self, stdtype, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.stdtype = stdtype

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.std(self.stdtype, self.log_level, line.rstrip())
            pass

    def flush(self):
        self.logger.hdlr.flush()
        pass
