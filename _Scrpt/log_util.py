import logging

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(name)s : %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
loggers = {}


def get_logger(logger_name='root', file_name=None, level=logging.DEBUG):
    if logger_name not in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        # console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        # file handler
        if file_name:
            fh = logging.FileHandler(file_name, 'w')
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        loggers[logger_name] = logger
        return loggers[logger_name]
    else:
        return loggers[logger_name]


def shutdown():
    logging.shutdown()

