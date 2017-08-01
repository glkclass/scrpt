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
                    'stdout':       '%(indent)s[SDO] : %(message)s',
                    'stderr':       '%(indent)s[SDR] : %(message)s',
                    'debug':        '%(indent)s[DBG] : %(message)s',
                    'info':         '%(indent)s[INF] : %(message)s',
                    'warning':      '%(indent)s[WAR] : %(message)s',
                    'error':        '%(indent)s[ERR] : %(message)s',
                    # 'fatal':        '%(indent)s[FTL] : %(stack_info)s : %(message)s',
                    'fatal':        '%(indent)s[FTL] : %(message)s',
                    'log':          '%(indent)s[LOG] : %(message)s',
                    'xxx':          '%(indent)s[XXX] : %(message)s',
                    'xxxx':         '%(indent)s[XXXX] : %(message)s',
                    'time':         '%(indent)s[TME] : %(message)s : %(asctime)s',
                    'time_delta':   '%(indent)s[TME] : %(message)s : %(asctime)s : [DLT] : %(delta)s',
                    'cmd':          '%(indent)s[CMD] : %(message)s : [TME] : %(asctime)s',
                    'job_started':  '%(indent)s[JOB] : %(message)s : [TME] : %(asctime)s',
                    'job_finished': '%(indent)s[JOB] : %(message)s : [TME] : %(asctime)s : [DUR] : %(dur)s'
                }
    datetime_frmt = '%Y/%m/%d %H:%M:%S'
    time_frmt = '%H:%M:%S'
    job_dur = 0
    extra = {'indent': ''}
    default_settings = {'print_cmd': False, }

    def __init__(self, name):
        Scrpt_base.__init__(self, self.default_settings)
        Logger.__init__(self, name)

        self.setLevel(logging.INFO)
        self.job_time_stack = {'start': {}, 'time_delta': self.get_time()['now']}  # to store job start/finish time, delta times, ...
        self.indent_message(0)
        self.hdlr = {'console': logging.StreamHandler()}
        self.addHandler(self.hdlr['console'])
        self.propagate = False

        sys.stdout = Stream2Logger('stdout', self, self.INFO)
        # sys.stderr = Stream2Logger('stderr', self, self.ERROR)

    def add_handler(self, path2log):
        # self.removeHandler(self.hdlr['file'])
        self.hdlr['file'] = logging.FileHandler(path2log, mode='w')
        self.addHandler(self.hdlr['file'])

    def set_formatter(self, foo, **kwargs):
        for hdlr_i in self.hdlr.keys():
            self.hdlr[hdlr_i].setFormatter(logging.Formatter(self.msg_frmt[foo], **kwargs))

    def flush(self):
        for hdlr_i in self.hdlr.keys():
            self.hdlr[hdlr_i].flush()

    
    def indent_message(self, indent_val):
        # print('xxx: ' + str(indent_val) )
        self.indent = indent_val if 0 == indent_val else self.indent + indent_val
        self.extra['indent'] = self.indent * '\t'

    def std(self, stdtype, lvl, msg):
        """Print messages from 'STDOUT/ERR'"""
        # print('indent: ' + str(self.indent))
        self.set_formatter(stdtype)
        Logger.log(self, lvl, msg, extra=self.extra)

    def log(self, lvl, msg, *args, **kwargs):
        """Print 'Info' message"""
        if lvl in self.log_level:
            kwargs['extra'] = self.extra
            self.log_func[lvl](self, msg, *args, **kwargs)
            # print (msg)
        else:
            self.set_formatter('log')
            kwargs['extra'] = self.extra
            Logger.log(self, lvl, 'vvv' + msg, *args, **kwargs)
            # self.set_formatter('xxx')

    def debug(self, msg, *args, **kwargs):
        """Print 'Info' message"""
        self.set_formatter('debug')
        kwargs['extra'] = self.extra
        Logger.debug(self, msg, *args, **kwargs)
        self.set_formatter('xxx')

    def info(self, msg, *args, **kwargs):
        """Print 'Info' message"""
        # print('indent: ' + str(self.indent))
        self.set_formatter('info')
        kwargs['extra'] = self.extra
        Logger.info(self, msg, *args, **kwargs)
        self.set_formatter('xxx')

    def warning(self, msg, *args, **kwargs):
        """Print 'Warning' message"""
        self.set_formatter('warning')
        kwargs['extra'] = self.extra
        Logger.warning(self, msg, *args, **kwargs)
        self.set_formatter('xxx')

    def error(self, msg, *args, **kwargs):
        """Print 'Error' message"""
        self.set_formatter('error')
        kwargs['extra'] = self.extra
        Logger.error(self, msg, *args, **kwargs)
        self.set_formatter('xxx')

    def fatal(self, msg, *args, **kwargs):
        """Print 'Fatal' message and terminate Scrpt execution."""
        self.set_formatter('fatal')
        kwargs['extra'] = self.extra
        Logger.critical(self, msg, *args, **kwargs)
        Logger.critical(self, 'Scrpt has been terminated due to \'Fatal exception\' encountered!!!', *args, **kwargs)
        if self.cfg['print_cmd'] is False:
            self.close()
            sys.exit('Scrpt has been terminated due to \'Fatal exception\' encountered (see \'*.log\' for details)!!!')

    def critical(self, msg, *args, **kwargs):
        """Print 'Critial' message."""
        self.set_formatter('fatal')
        kwargs['extra'] = self.extra
        Logger.critical(self, msg, *args, **kwargs)
        self.set_formatter('xxx')

    def time(self, msg='', lvl=INFO):
        """Print time"""
        self.set_formatter('time', datefmt=self.time_frmt)
        Logger.log(self, lvl, msg, extra=self.extra)
        self.set_formatter('xxx')

    def time_delta(self, msg='', lvl=INFO):
        """Print time delta between two calls"""
        self.extra['delta'] = self.get_time()['now'] - self.job_time_stack['time_delta']
        self.job_time_stack['time_delta'] = self.get_time()['now']
        self.set_formatter('time_delta', datefmt=self.time_frmt)
        Logger.log(self, lvl, msg, extra=self.extra)
        self.set_formatter('xxx')

    def job(self, mode='started', name='', lvl=INFO):
        """Print 'job' start/finish message"""
        # print('indent: ' + str(self.indent))
        if mode == 'started':
            self.job_time_stack['start'][name] = self.get_time()['now']
        elif mode == 'finished':
            self.job_dur = self.get_time()['now'] - self.job_time_stack['start'][name]
            self.extra['dur'] = self.job_dur
            self.indent_message(-1)

        self.set_formatter('job_%s' % mode, datefmt=self.datetime_frmt if 'SCRPT' == name else self.time_frmt)
        Logger.log(self, lvl, name, extra=self.extra)
        self.set_formatter('xxx')

        if mode == 'started':
            self.indent_message(1)

    def cmd(self, msg='', lvl=INFO):
        """Print 'cmd' + 'time'"""
        self.set_formatter('cmd', datefmt=self.time_frmt)
        Logger.log(self, lvl, msg, extra=self.extra)
        self.set_formatter('xxx')

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
