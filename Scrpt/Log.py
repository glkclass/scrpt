import sys
import logging
from Scrpt_base import Scrpt_base
from Stream2Logger import Stream2Logger

Logger = logging.getLoggerClass()


class Log(Logger, Scrpt_base):
    """Class "Log" - inherits standard python logging.Logger class and adds some custom functionality."""
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    FATAL = logging.CRITICAL
    log_level = [DEBUG, INFO, WARNING, ERROR, FATAL]

    msg_frmt =  {
                    'stdout':   '%(indent)s[SDO] : %(message)s',
                    'stderr':   '%(indent)s[SDR] : %(message)s',
                    'debug':    '%(indent)s[DBG] : %(message)s',
                    'info':     '%(indent)s[INF] : %(message)s',
                    'warning':  '%(indent)s[WAR] : %(message)s',
                    'error':    '%(indent)s[ERR] : %(message)s',
                    'fatal':    '%(indent)s[FTL] : %(stack_info)s : %(message)s',
                    'log':      '%(indent)s[LOG] : %(message)s',
                    'time':     '%(indent)s[TME] : %(asctime)s : %(message)s',
                    'cmd':      '%(indent)s[CMD] : %(message)s : [TME] : %(asctime)s',
                    'job':
                        {
                    'started':  '%(indent)s[JOB] : %(message)s : [TME] : %(asctime)s',
                    'finished': '%(indent)s[JOB] : %(message)s : [TME] : %(asctime)s : [DUR] : %(dur)s'
                        }
                }
    datetimefmt = '%Y/%m/%d %H:%M:%S'
    timefmt = '%H:%M:%S'

    extra = {'indent': ''}
    default_settings = {'print_cmd': False, }

    def __init__(self, name):
        Scrpt_base.__init__(self, self.default_settings)
        Logger.__init__(self, name)
        self.setLevel(self.INFO)
        self.job_time_stack = {'start': {}}  # to store job start/finish time
        self.indent_message(0)
        sys.stdout = Stream2Logger('stdout', self, self.INFO)
        # sys.stderr = Stream2Logger('stderr', self, self.ERROR)


    def add_handler(self, path2log):
        if path2log:
            self.hdlr = logging.FileHandler(path2log, mode='w')
        else:
            self.hdlr = logging.StreamHandler()
        self.addHandler(self.hdlr)
        # sys.stdout = self.hdlr

    def indent_message(self, indent_val):
        self.indent = indent_val if 0 == indent_val else self.indent + indent_val
        self.extra['indent'] = self.indent * '\t'

    def std(self, stdtype, lvl, msg):
        """Print messages from 'STDOUT/ERR'"""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt[stdtype]))
        Logger.log(self, lvl, msg, extra=self.extra)

    def log(self, lvl, msg, *args, **kwargs):
        """Print 'Info' message"""
        if lvl in self.log_level:
            kwargs['extra'] = self.extra
            self.log_func[lvl](self, msg, *args, kwargs)
        else:
            self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['log']))
            kwargs['extra'] = self.extra
            Logger.log(self, lvl, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Print 'Info' message"""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['debug']))
        kwargs['extra'] = self.extra
        Logger.debug(self, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Print 'Info' message"""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['info']))
        kwargs['extra'] = self.extra
        Logger.info(self, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Print 'Warning' message"""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['warning']))
        kwargs['extra'] = self.extra
        Logger.warning(self, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Print 'Error' message"""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['error']))
        kwargs['extra'] = self.extra
        Logger.error(self, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        """Print 'Fatal' message and terminate Scrpt execution."""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['fatal']))
        kwargs['extra'] = self.extra
        Logger.critical(self, msg, *args, **kwargs)
        Logger.critical(self, 'Scrpt has been terminated due to \'Fatal exception\' encountered!!!', *args, **kwargs)
        if self.cfg['print_cmd'] is False:
            self.close()
            sys.exit('Scrpt has been terminated due to \'Fatal exception\' encountered (see \'*.log\' for details)!!!')

    def critical(self, msg, *args, **kwargs):
        """Print 'Critial' message."""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['fatal']))
        kwargs['extra'] = self.extra
        Logger.critical(self, msg, *args, **kwargs)

    def time(self, msg='', lvl=INFO):
        """Print time"""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['time'], datefmt=self.timefmt))
        Logger.log(self, lvl, msg, extra=self.extra)

    def job(self, mode='started', name='', lvl=INFO):
        """Print 'job' start/finish message"""
        if mode == 'started':
            self.job_time_stack['start'][name] = self.get_time()['now']
        elif mode == 'finished':
            self.extra['dur'] = self.get_time()['now'] - self.job_time_stack['start'][name]
            self.indent_message(-1)

        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['job'][mode], datefmt=self.datetimefmt if 'SCRPT' == name else self.timefmt))
        Logger.log(self, lvl, name, extra=self.extra)

        if mode == 'started':
            self.indent_message(1)

    def cmd(self, msg='', lvl=INFO):
        """Print 'cmd' + 'time'"""
        self.hdlr.setFormatter(logging.Formatter(self.msg_frmt['cmd'], datefmt=self.timefmt))
        Logger.log(self, lvl, msg, extra=self.extra)

    def close(self):
        """Close log if opened"""
        logging.shutdown()

    def settings(self, cfg=None, msg=""):
        """Print given 'unit' settings"""
        if msg:
            self.info(msg)
        cfg = cfg if cfg is not None else self.cfg
        if cfg:
            for setting in cfg.keys():
                self.info("\t%s = %s" % (setting, cfg[setting]))
        else:
            self.info('\tEmpty settings!')

    log_func_name = [debug, info, warning, error, fatal]
    log_func = dict(zip(log_level, log_func_name))
