import logging
"""Logging util"""

# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s : %(name)s - %(message)s : %(filename)s, %(lineno)d', datefmt='%Y/%m/%d %H:%M:%S')
loggers = {}


def get_logger(logger_name='root', file_name=None, level=None):
    if logger_name not in loggers:
        loggers[logger_name] = logging.getLogger(logger_name)
        loggers[logger_name].debug(f'{level}')

        set_level(level, logger_name)
        # console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        loggers[logger_name].addHandler(ch)
        # file handler
        if file_name:
            fh = logging.FileHandler(file_name, 'w')
            fh.setFormatter(formatter)
            loggers[logger_name].addHandler(fh)
        loggers[logger_name].debug(f"Logger '{logger_name}' was created.")
        return loggers[logger_name]
    else:
        return loggers[logger_name]


def is_level_legal(level):
    levels = ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    return level in range(100) or level in levels


def set_level(level, logger_name='root'):
    if logger_name not in loggers:
        logging.error('There is no such logger: %s' % logger_name)
        return None
    else:
        if level is not None:
            if is_level_legal(level):
                loggers[logger_name].debug('Changing logging level to %s' % str(level))
                loggers[logger_name].setLevel(level)
            else:
                loggers[logger_name].error('This is not a logging level we expect to see: %s' % str(level))
        return loggers[logger_name]


def shutdown():
    logging.shutdown()

get_logger(level='INFO')

