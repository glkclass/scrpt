import os
import sys
import argparse
import inspect
import types
from Scrpt_base import Scrpt_base
import Log
import Util
import time

class Scrpt(Scrpt_base):
    """Class "Scrpt" - base class for all scripts. Contains stuff usefull for script developing/maintaining:
    basic utils / logging&reporting / local&remote file access / etc"""

    def __init__(self, path2log=None, settings=None):
        default_settings =  {
                                'shtdwn': False
                            }
        Scrpt_base.__init__(self, default_settings)
        # create Log inst
        if 'log_basename' == path2log:
            log_basename = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.log'
            self.log = Log.Log(log_basename, default_settings)
        else:
            self.log = Log.Log(path2log, default_settings)
        self.jobs = self.generate_job_list()  #job list
        self.job_time_stack = {'dur': {}, 'start': {}}  # to store job start/finish time

        self.log.info('Scrpt strtd...')
        self.job_time_stack['SCRPT'] = self.get_time()['now']
        self.log.job('started', ('SCRPT', self.get_time()['date_time']))
        self.util = Util.Util(self.log, default_settings)  # create Util inst
        self.setup(settings)  # setup/propagate settings
        self.init_pc_shtdwn(5000)  # set PC 'sleep delay' if 'shutdowning'


    def setup(self, settings=None):
        """ Add/update Scrpt and embedded unit settings"""
        Scrpt_base.setup(self, settings)
        self.util.setup(settings)
        self.log.setup(settings)

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
        dur = self.get_time()['now'] - self.job_time_stack['SCRPT']
        self.log.job('finished', ('SCRPT', self.get_time()['date_time'], dur))
        self.log.info('Scrpt fnshd!',)
        self.pc_shutdown('/h')
        self.log.close()

    def parse_args(self, args2parse):
        """Parse input arguments if script should be calling with input args."""
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
                self.log.fatal('Wrong arg structure %s (mandatory field \'name\' is absent)!!!' % str(arg))

            arg_help = arg['help'] if 'help' in arg.keys() else ''

            if 'default' in arg.keys():
                parser.add_argument('-%s' % arg_name, help=arg_help, default=arg['default'])
            else:
                parser.add_argument('%s' % arg_name, help=arg_help)

        args = parser.parse_args()
        args = vars(args)

        # check input arg values if possible options were defined
        for arg in args2parse:
            arg_options = self.make_list(arg['options']) if 'options' in arg.keys() else None
            if arg_options is not None:
                if 'default' in arg.keys():
                    arg_options.append(arg['default'])
                for item in arg_options:
                    if args[arg['name']] == str(item):
                        break
                else:
                    self.log.fatal('Wrong input arg value: %s. Possible options are: %s' % (args[arg['name']], arg_options))
        return args

    def generate_job_list(self):
        """Create dict: {class method name: class method handle}"""
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        jobs = [item for item in methods if not item[0].startswith('_') and not item[0].endswith('_')]
        job_list = {}
        for item in jobs:
            job_list[item[0]] = item[1]
        return job_list

    def job(self, job, *pos_args, **key_args):
        """Job wrapper. Used to call any class method as job (add appropriate log messages, measure duration, ...)"""
        if type(job) is str:
            job_name = job
            job_handle = self.jobs[job_name]
        elif isinstance(job, types.MethodType):
            job_handle = job
            for key in self.jobs.keys():
                if job == self.jobs[key]:
                    job_name = key
                    break
            else:
                self.log.fatal('Unrecognized method: %s' % job)

        self.job_time_stack['start'][job_name] = self.get_time()['now']
        self.log.job('started', (job_name, self.get_time()['time']))
        retval = job_handle(*pos_args, **key_args)
        dur = self.get_time()['now'] - self.job_time_stack['start'][job_name]
        self.job_time_stack['dur'][job_name] = dur
        self.log.job('finished', (job_name, self.get_time()['time'], dur))
        return retval

    def sleep(self, time2sleep=None):
        """Generate pause for 'time2sleep' seconds during execution..."""
        tme2slp = time2sleep if time2sleep else self.cfg['time2sleep'] if 'time2sleep' in self.cfg.keys() else 0
        if tme2slp:
            seconds = tme2slp % 60
            minutes = tme2slp / 60
            hours = minutes / 60
            self.log.info('Sleeping for %02dh:%02dm:%02ds ...' % (hours, minutes, seconds))
            time.sleep(tme2slp)
