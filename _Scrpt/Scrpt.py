import os
import sys
import inspect
import types
import logging
import time
from Scrpt_base import Scrpt_base
import Log
import Util


class Scrpt(Scrpt_base):
    """Class "Scrpt" - base class for all scripts.

    Contains stuff usefull for script developing/maintaining:
    basic utils / logging&reporting / local&remote file access / etc
    """

    default_settings = {'shtdwn': False,
                        'args': 'disable',
                        'platform': sys.platform}

    def __init__(self, log=None, user_settings={}):
        Scrpt_base.__init__(self, self.default_settings)
        self.update_settings(user_settings)
        # create Logger
        if log and str != type(log):
            self.log = log
        else:
            logging.setLoggerClass(Log.Log)
            self.log = logging.getLogger(__name__)
            logging.setLoggerClass(logging.Logger)
            if str == type(log):
                path2log = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.log' if 'basename' == log else log
                self.log.add_handler(path2log)

        if 'enable' == self.cfg['args']:
            from Args import Args
            self.args = Args(self.log, self.cfg)

        self.util = Util.Util(self.log, self.cfg)  # create Util inst
        self.methods = self.get_methods()  # job list
        self.attr = self.get_attr()  # attr list
        self.init_pc_shutdown(5000)  # set PC 'sleep delay' if 'shutdowning'

    def main(self, **kwargs):
        if 'enable' == self.cfg['args'] and 'job' in self.args.__dict__.keys():  # 'parse input args' feature was enabled and 'job' passed in
            return self.job(self.args.job, **kwargs)
        else:
            return self.job('', **kwargs)

    def run(self, **kwargs):
        if 'enable' == self.cfg['args']:
            self.args._parse()
        self.log.info('Python : %s' % sys.version)
        self.log.info('Host : %s' % self.util.get_hostname())
        self.log.job('started', 'SCRPT')
        ret = self.main(**kwargs)
        self.log.job('finished', 'SCRPT')
        self.log.info('SCRPT fnshd.')
        self.log.close()
        self.pc_shutdown('/h')
        return ret

    def init_pc_shutdown(self, mins):
        """Set large "PC sleep delay" when long term job scheduled with "PC shutdown" at the finish."""
        if self.cfg['shtdwn']:
            self.util.pc_setup_sleep(mins)

    def pc_shutdown(self, opt=None):
        """Set "PC sleep delay" = 120 min and shutdown(hibernate) PC"""
        if self.cfg['shtdwn'] is True:
            self.util.pc_setup_sleep(120)
            cmd = 'shutdown' if not opt else 'shutdown %s' % str(opt)  # shutdown or shutdown /h
            self.util.subprocess_call(cmd)

    def get_methods(self):
        """Create dict: {class method name: class method handle}"""
        method_list = inspect.getmembers(self, predicate=inspect.ismethod)
        method_list = [item for item in method_list if not item[0].startswith('_') and not item[0].endswith('_')]
        methods = {}
        for item in method_list:
            methods[item[0]] = item[1]
        return methods

    def get_attr(self):
        return self.__dict__

    def job(self, scr_job, **kwargs):
        """Job wrapper. Used to call any class method as job (add appropriate log messages, measure duration, ...)"""
        if type(scr_job) is str:
            hier = scr_job.split('.')
            if 1 == len(hier):
                if scr_job not in self.methods.keys():
                    self.log.fatal('Unrecognized job: \'%s\'' % scr_job)
                else:
                    job_name = scr_job
                    job_handle = self.methods[scr_job]
            elif 2 == len(hier):
                attr_name = hier[0]
                if attr_name not in self.attr.keys():
                    self.log.fatal('Unrecognized nested job: %s (...) : %s' % (scr_job, attr_name))
                else:
                    method_name = hier[1]
                    attr = self.attr[attr_name]
                    if method_name not in attr.methods.keys(): 
                        self.log.fatal('Unrecognized nested job: %s (...) : %s' % (scr_job, method_name))
                    else:
                        job_name = scr_job
                        job_handle = attr.methods[method_name]
            else:
                self.log.fatal('Wrong \'job\': maximum two nested levels are supported, but %d were applied: %s (...)' % (len(hier), scr_job))
        elif isinstance(scr_job, types.MethodType):
            job_handle = scr_job
            for key in self.methods.keys():
                if job_handle == self.methods[key]:
                    job_name = key
                    break
            else:
                self.log.fatal('Unrecognized job: %s' % scr_job)

        self.log.job('started', job_name)
        retval = job_handle(**kwargs)
        self.log.job('finished', job_name)
        return retval

    def sleep(self, time2sleep=None):
        """Generate pause for 'time2sleep' seconds during execution..."""
        tme2slp = time2sleep if time2sleep else self.cfg['time2sleep'] if 'time2sleep' in self.cfg.keys() else 0
        if tme2slp:
            seconds = tme2slp % 60
            minutes = tme2slp / 60
            hours = minutes / 60
            self.log.time()
            self.log.info('Sleeping for %02dh:%02dm:%02ds ...' % (hours, minutes, seconds))
            time.sleep(tme2slp)
            self.log.time()

    def upload_scrpt_stuff(self, src_path, dst_path):
        # for item in ('__init__.py', 'File.py', 'Log.py','Stream2Logger.py', 'Path.py', 'Rmt.py', 'Scrpt.py', 'Scrpt_base.py', 'Util.py'):
        self.util.rmt.upload(os.path.join(src_path, '*.py'), dst_path)


    def info(self, msg, *args, **kwargs):
        """Proxy for log.info"""
        self.log.info(msg, *args, **kwargs)
        
    def error(self, msg, *args, **kwargs):
        """Proxy for log.error"""
        self.log.error(msg, *args, **kwargs)
