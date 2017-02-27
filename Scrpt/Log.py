import sys

from Scrpt_base import Scrpt_base


class Log(Scrpt_base):
    """Class "Log" - implements all logging&reporting operations. To be embedded in others classes requiring such functionality."""
    severity_levels = ('info', 'warning', 'error', 'fatal')
    indent = 0
    indent_str = ''

    def __init__(self, path2log=None, settings=None):
        default_settings = {'verbosity': 1, 'print_cmd': False}
        Scrpt_base.__init__(self, default_settings)
        self.setup(settings)
        self.log = None
        if path2log:
            self.log = open(path2log, 'w')
            self.le = '\n'  # NewLine for txt log
        else:
            self.le = ''  # No NewLine for console log

        self.indent_message(0)

        self.time_stack = {}

    def indent_message(self, indent_val):
        self.indent = indent_val if 0 == indent_val else self.indent + indent_val
        self.indent_str = self.indent * '\t'

        self.log_message_patt =     {
                                        'base': self.indent_str + '[%s] : %s' + self.le,
                                        'time': self.indent_str + '[TME] : %s' + self.le,
                                        'info': self.indent_str + '[INF] : %s' + self.le,
                                        'warning': self.indent_str + '[WAR] : %s' + self.le,
                                        'error': self.indent_str + '[ERR] : %s' + self.le,
                                        'fatal': self.indent_str + '[FTL] : %s' + self.le,
                                        'job':  {
                                                    'started': self.indent_str + '[JOB] : %s : [TME] : %s' + self.le,
                                                    'finished': self.indent_str + '[JOB] : %s : [TME] : %s : [DUR] : %s' + self.le,
                                                },
                                        'cmd': self.indent_str + '[CMD] : %s : [TME] %s' + self.le,
                                    }

    def close(self):
        """Close log if opened"""
        if self.log:
            self.log.close()
            self.log = None

    def _print(self, line):
        """Print message to log file or stdout"""
        if self.log:
            self.log.write(line)
            self.log.flush()
        else:
            print line

    def info(self, msg='', verbosity=0):
        """Print 'Info' message"""
        if verbosity < self.cfg['verbosity']:
            self._print(self.log_message_patt['info'] % msg)

    def warning(self, msg=''):
        """Print 'Warning' message"""
        self._print(self.log_message_patt['warning'] % msg)

    def error(self, msg=''):
        """Print 'Error' message"""
        self._print(self.log_message_patt['error'] % msg)

    def fatal(self, msg=''):
        """Print 'Fatal' message and terminate Scrpt execution."""
        self._print(self.log_message_patt['fatal'] % msg)

        if self.exists():
            self._print(self.log_message_patt['fatal'] % 'Scrpt has been terminated due to \'Fatal exception\' encountered!!!')

        if self.cfg['print_cmd'] is False:
            self.close()
            sys.exit('Scrpt has been terminated due to \'Fatal exception\' encountered (see \'*.log\' for details)!!!')

    def message(self, msg, severity='info'):
        """Print message which type is defined by input param"""
        if 'info' == severity:
            self.info(msg)
        elif 'warning' == severity:
            self.warning(msg)
        elif 'error' == severity:
            self.error(msg)
        elif 'fatal' == severity:
            self.fatal(msg)
        elif 'silent' == severity:
            pass
        else:
            self.error('Wrong log.message severity level: \'%s\' !!!' % severity)

    def time(self, mode='time'):
        """Print time message line"""
        self._print(self.log_message_patt['time'] % self.get_time()[mode])

    def job(self, mode='started', msg_args=()):
        """Print 'job' start/finish message"""
        if 'finished' == mode:
            self.indent_message(-1)
        self._print(self.log_message_patt['job'][mode] % msg_args)
        if 'started' == mode:
            self.indent_message(1)
        

    def cmd(self, msg):
        """Print 'cmd' message line"""
        tme = self.get_time()['time']
        self._print(self.log_message_patt['cmd'] % (msg, tme))

    def settings(self, cfg=None, msg=""):
        """Print given 'unit' settings"""
        if msg:
            self.info(msg)
        cfg = cfg if cfg is not None else self.cfg
        if cfg:
            for setting in cfg.keys():
                self.info("\t%s = %s" % (setting, cfg[setting]))
        else:
            self.info('\tEmpty!')

    def exists(self):
        """Check log file existence"""
        foo = True if self.log else False
        return foo

    def fid(self):
        """Return log file 'id' if exists"""
        foo = self.log if self.exists() else None
        return foo
