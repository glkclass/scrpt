import os
import sys
import argparse
import inspect
import types
from Scrpt_base import Scrpt_base
import logging
import Log
import Util
import time


class Scrpt(Scrpt_base):
    """Class "Scrpt" - base class for all scripts. Contains stuff usefull for script developing/maintaining:
    basic utils / logging&reporting / local&remote file access / etc"""

    default_settings = {'shtdwn': False}

    def __init__(self, log=None, user_settings={}):
        Scrpt_base.__init__(self, self.default_settings)
        self.update_settings(user_settings)
        # create Logger
        if log:
            self.log = log
        else:
            logging.setLoggerClass(Log.Log)
            self.log = logging.getLogger('__name__')
            logging.setLoggerClass(logging.Logger)

        # path2log = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.log' if 'basename' == path2log else path2log
        # self.log.add_handler(path2log)
        self.log.info('Python %s' % sys.version)
        self.methods = self.get_methods()  # job list
        self.attr = self.get_attr()  # job list

        self.log.job('started', 'SCRPT')
        self.util = Util.Util(self.log, self.cfg)  # create Util inst
        self.init_pc_shtdwn(5000)  # set PC 'sleep delay' if 'shutdowning'

    def init_pc_shtdwn(self, mins):
        """Set large "PC sleep delay" when long term job scheduled with "PC shutdown" at the finish."""
        if self.cfg['shtdwn']:
            self.util.pc_setup_sleep(mins)

    def pc_shutdown(self, opt=None):
        """Set "PC sleep delay" = 120 min and shutdown(hibernate) PC"""
        if self.cfg['shtdwn'] is True:
            self.util.pc_setup_sleep(120)
            cmd = 'shutdown' if not opt else 'shutdown %s' % str(opt)  # shutdown or shutdown /h
            self.util.subprocess_call(cmd)

    def finish(self):
        """Finalize Scrpt: write final message/close files/turn off PC/..."""
        self.log.job('finished', 'SCRPT')
        self.log.info('SCRPT fnshd.')

        self.log.close()
        self.pc_shutdown('/h')

    def parse_args(self, args2parse):
        """ Parse input arguments if script should be calling with input args.
            Usage:
                <Code>
                    ...
                    args = []
                    args.append({   'name': arg_name, 
                                    'default': default_value, 
                                    'type': arg_type, 
                                    'values': list_of_possible_values,
                                    'help': 'help string'})
                    parsed_args = scr.parse_args(args)
                    ...
                </Code>
                'arg_name' is the only mandatory field, others are optional.
        """
        parser = argparse.ArgumentParser(description='Scrpt', formatter_class=argparse.RawTextHelpFormatter)
        args2parse = self.make_list(args2parse)
        # if not type(args2parse) is dict:
        #     self.log.fatal('Wrong args2parse structure: %s. Should be defined as dict!!!' % str(args2parse))

        # add args to be parsed
        for arg in args2parse:
            if not type(arg) is dict:
                self.log.fatal('Wrong args2parse structure: %s. Should be defined as dict!!!' % str(arg))

            if 'name' in arg.keys():
                arg_name = arg['name']
            else:
                self.log.fatal('Wrong arg structure: %s (mandatory field \'name\' is absent)!!!' % str(arg))

            arg_help = arg['help'] if 'help' in arg.keys() else ''
            arg_type = arg['type'] if 'type' in arg.keys() else str

            if 'default' in arg.keys():
                parser.add_argument('-%s' % arg_name, type=arg_type, help=arg_help, default=arg['default'])
            else:
                parser.add_argument('%s' % arg_name, type=arg_type, help=arg_help)

        args = parser.parse_args()
        args = vars(args)

        # check input arg values if possible values were defined
        for arg in args2parse:
            arg_values = self.make_list(arg['values']) if 'values' in arg.keys() else None
            if arg_values is not None:
                for item in arg_values:
                    if args[arg['name']] == str(item):
                        break
                else:
                    self.log.fatal('Wrong input arg value: %s. Possible values are: %s' % (args[arg['name']], arg_values))

        return args

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

    def job(self, job, *pos_args, **key_args):
        """Job wrapper. Used to call any class method as job (add appropriate log messages, measure duration, ...)"""
        if type(job) is str:
            hier = job.split('.')
            if 1 == len(hier):
                if job not in self.methods.keys():
                    self.log.fatal('Unrecognized job: %s (...)' % job)
                else:
                    job_name = job
                    job_handle = self.methods[job]
            elif 2 == len(hier):
                attr_name = hier[0]
                if attr_name not in self.attr.keys():
                    self.log.fatal('Unrecognized nested job: %s (...) : %s' % (job, attr_name))
                else:
                    method_name = hier[1]
                    attr = self.attr[attr_name]
                    if method_name not in attr.methods.keys(): 
                        self.log.fatal('Unrecognized nested job: %s (...) : %s' % (job, method_name))
                    else:
                        job_name = job
                        job_handle = attr.methods[method_name]
            else:
                self.log.fatal('Wrong \'job\': maximum two nested levels are supported, but %d were applied: %s (...)' % (len(hier), job))
        elif isinstance(job, types.MethodType):
            job_handle = job
            for key in self.methods.keys():
                if job_handle == self.methods[key]:
                    job_name = key
                    break
            else:
                self.log.fatal('Unrecognized job: %s' % job)

        self.log.job('started', job_name)
        retval = job_handle(*pos_args, **key_args)
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

    def upload_scrpt_stuff(self, src_path='C:\\avv\\design\\_avv\\scrpt\\_Scrpt', dst_path='design/_Scrpt'):
        # for item in ('__init__.py', 'File.py', 'Log.py','Stream2Logger.py', 'Path.py', 'Rmt.py', 'Scrpt.py', 'Scrpt_base.py', 'Util.py'):
        self.util.rmt.upload(os.path.join(src_path, '*.py'), dst_path)
