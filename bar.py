from Scrpt.Scrpt import Scrpt


class bar_scrpt(Scrpt):
    def run(self):
        self.log.info('Info message example...')
        self.log.warning('Warning message example...')
        self.log.error('Error message example...')
        self.log.settings(msg='Default settings:')

        self.log.time()
        self.log.warning('Warning message example...')
        self.log.error('Error message example...')
        self.log.settings(msg='Default settings:')
        self.log.settings(self.log.cfg, msg='Logger settings:')

bar_scrpt_settings = {'print_cmd': False, 'shtdwn': False}
foo = bar_scrpt('', settings=bar_scrpt_settings)
foo.job('run')
foo.finish()
