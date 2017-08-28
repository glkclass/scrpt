import argparse
from Scrpt_base import Scrpt_base


class Args(Scrpt_base):
    """Class "Arg" - contains stuff used for script input args maintenance"""
    def __init__(self, log, user_settings={}):
        self._default_settings = {'shtdwn': False}
        self._options = {}  # input args possible values if defined
        Scrpt_base.__init__(self, self._default_settings)
        self.update_settings(user_settings)
        self._log = log  # logger should be define outside
        self._parser = argparse.ArgumentParser(description='Scrpt', formatter_class=argparse.RawTextHelpFormatter)

    def _add_arg(self, name, default, help, options, type):
        if default is not None:
            self._parser.add_argument('--%s' % name, type=type, help=help, default=default)
        else:
            self._parser.add_argument('%s' % name, type=int, help=help)
        self._options[name] = self.make_list(options) if options else None

    def define_int(self, name, default=None, help='', options=None):
        self._add_arg(name, default, help, options, int)

    def define_str(self, name, default=None, help='Help could be here...', options=None):
        self._add_arg(name, default, help, options, str)

    def _parse(self):
        """Parse scrpt input arguments if exist"""
        args = vars(self._parser.parse_args())

        # check input arg values if possible values(options) were defined
        for arg_name, arg_val in args.items():
            self.__dict__[arg_name] = arg_val
            if self._options[arg_name]:
                if arg_val not in self._options[arg_name]:
                    self._log.fatal('Wrong input arg(\'%s\') value(\'%s\'), possible values are: %s' % (arg_name, arg_val, self._options[arg_name]))

        # print arg values/types
        foo = [(key, type(args[key]), args[key]) for key in args.keys()]
        self._log.info('Input args:')
        for item in foo:
            self._log.info('\'%s\'(%s) = \'%s\'' % item)
        return
