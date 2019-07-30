import os
import sys
import inspect
import types
import log_util
import util


class Scrpt(object):
    """Class "Scrpt" - base class for scripts"""

    cfg = {'shtdwn': False}

    def __init__(self, log_filename=None, settings={}):
        self.cfg.update(settings)
        self.args = None  # parse input args if exist
        self.log = log_util.get_logger('scrpt', log_filename)  # create Logger

        # Set large "PC sleep delay" when long term job scheduled with "PC shutdown" at the finish
        if self.cfg['shtdwn']:
            util.pc_setup_sleep(6000)

    def main(self, **kwargs):
        if getattr(self.args, 'job', None):  # check the job was defined in input args
            return self.job(self.args.job, **kwargs)
        else:
            self.log.error('Define args.job with job name or override \'main\' method!!!')
            return None

    def run(self, **kwargs):
        self.log.info('python : %s' % sys.version)
        self.log.info('host : %s' % util.get_hostname())
        self.log.info('scrpt started')
        ret = self.main(**kwargs)
        self.log.info('scrpt finished')
        log_util.shutdown()
        if self.cfg['shtdwn'] is True:
            util.pc_shutdown('/h')
        return ret

    def get_methods(self):
        """Create dict: {method_name: method_handler}"""
        return {item[0]: item[1] for item in inspect.getmembers(self, predicate=inspect.ismethod)}

    def job(self, scr_job, **kwargs):
        """Job wrapper. Used to call any class method as job (add appropriate log messages, measure duration(TODO), ...)"""
        methods = self.get_methods()  # job list
        if isinstance(scr_job, str):
            if scr_job not in methods:
                self.log.critical('Unrecognized job: \'%s\'' % scr_job)
                return None
            else:
                job_name = scr_job
                job_handle = self.methods[scr_job]
        elif isinstance(scr_job, types.MethodType):
            job_name = scr_job.__name__
            job_handle = scr_job
        else:
            self.log.critical('unrecognized job: %s !!!' % scr_job)
            return None

        self.log.info('jJob \'%s\' started' % job_name)
        retval = job_handle(**kwargs)
        self.log.info('job \'%s\' finished' % job_name)
        return retval

    def upload_scrpt_stuff(self, scrpt_path, dst_path):
        foo = [os.path.join(scrpt_path, item) for item in os.listdir(scrpt_path) if item.endswith('.py')]
        self.util.rmt.upload(foo, dst_path)

if __name__ == "__main__":
    Scrpt().run()
