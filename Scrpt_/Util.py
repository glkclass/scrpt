from sys import platform
import os.path
import os
import re
import subprocess
import logging
import sys
import matplotlib.pyplot as plt

from Scrpt_base import Scrpt_base
from Log import Log
from Rmt import Rmt
from Path import Path
from File import File


class Util(Scrpt_base):
    """Class 'Util' - contains basic utils (may be embedded in appropriate classes).
    To be embedded in others classes requiring such functionality."""

    # plt = matplotlib.pyplot

    log_message =   {
                        'get_folder_item': 'There is no mathes',
                        'environ': {'fail': 'There is no such Env variable: %s !!!', 'success': 'Env variable: %s = %s'},
                    }
    default_settings =  {
                            'print_cmd': False,
                            'shtdwn': False,
                            'platform': platform
                        }

    def __init__(self, log=None, user_settings=None):
        Scrpt_base.__init__(self, self.default_settings)
        self.update_settings(user_settings)

        if log:
            self.log = log  # use external logger if exists
        else:
            # create own Logger
            logging.setLoggerClass(Log.Log)
            self.log = logging.getLogger(__name__)

        self.path = Path(self.log, self.cfg)
        self.file = File(self.log, self.cfg)
        self.rmt = Rmt(self.log, self.file, self.cfg)

    def get_folder_item(self, dir, file_pattern, verbosity=20):
        file_pattern_list = self.make_list(file_pattern)
        found_patt = []
        dir_item = os.listdir(dir)
        for item in dir_item:
            for patt in file_pattern_list:
                foo = re.search(patt, item)
                if foo:
                    found_patt.append(os.path.join(dir, item))
                    break

        if not found_patt:
            self.log.log(verbosity, self.log_message['get_folder_item'])
            found_patt.append('No matches!')

        return found_patt

    def line_wrap(self, line, prfx='<', sfx='>'):
        return str(prfx) + str(line) + str(sfx)

    def list_evaluate_diff(self, latter, former):
        latter = set(latter)
        former = set(former)
        diff = {}
        if latter - former:
            diff['p'] = list(latter - former)
        if former - latter:
            diff['m'] = list(former - latter)
        return diff

    def dict_create_key_hier(self, foo, keys, type='dict'):
        """Create following dictonary element: dict[keys_0][keys_1]...[keys_n-1] = {} or [].
        Type of created inner element (dict or list) is defined by 'type' parameter"""
        keys = self.make_list(keys)
        for key in keys[:-1]:
            if key not in foo.keys():
                foo[key] = {}
            foo = foo[key]
        if keys[-1] not in foo.keys():
            foo[keys[-1]] = {} if 'dict' == type else []

    def dict_has_key_hier(self, foo, keys):
        """Check whether dictonary has following element: dict[keys_0][keys_1]...[keys_n-1]"""
        keys = self.make_list(keys)
        for key in keys:
            if key in foo.keys():
                foo = foo[key]
            else:
                return False
        return True

    def subprocess_call(self, cmd, verbosity=20, shl=True):
        """Execute external command."""
        cmd_list = self.make_list(cmd)
        for cmd in cmd_list:
            self.log.cmd(cmd, verbosity)
            if self.cfg['print_cmd']:
                continue
            if 'shutdown' in cmd:  # close log file if command='shutdown ...'
                self.log.close()
                subprocess.call(cmd, shell=shl)
            else:
                # subprocess.call(cmd, shell=shl, stdout=sys.stdout, stderr=sys.stderr)
                subprocess.call(cmd, shell=shl)

    def environ(self, name_value, verbosity=40):
        """ Set/read environment variable.
            Use cases:
            environ('ENVAR_NAME=ENVAR_VALUE', verbosity=True)
            environ('ENVAR_NAME=ENVAR_VALUE')
            environ('ENVAR_NAME)
            environ('ENVAR_NAME', verbosity=True)
        """
        name_value = str(name_value)
        if '=' in name_value:  # setup env var
            pair = name_value.split('=')
            envar_name = pair[0].strip()
            envar_value = pair[1].strip()

            if envar_name.upper() in ('PATH', 'PYTHONPATH'):
                os.environ[envar_name] = envar_value if envar_name not in os.environ.keys() else os.environ[envar_name] + os.pathsep + envar_value
            else:
                os.environ[envar_name] = envar_value
            self.log.info(self.log_message['environ']['success'] % (envar_name, os.environ[envar_name]))
        else:  # read env var
            envar_name = name_value
            if envar_name not in os.environ.keys():
                self.log.log(verbosity, self.log_message['environ']['fail'] % envar_name)
                return None
            else:
                self.log.info(self.log_message['environ']['success'] % (envar_name, os.environ[envar_name]))

        return os.environ[envar_name]

    def parse_opt(self, opts, opt_line=''):
        """Parse options line which has following structure: 'opt0|opt1|opt2=3| opt4 | opt5=0 ...'"""
        options = str(opt_line).split('|')
        options = [item.strip() for item in options]  # remove whitespases
        for item in options:
            foo = item.split('=')
            foo = [item.strip() for item in foo]
            if not foo[0] in opts[self.cfg['platform']]['disabled']:
                if len(foo) > 1:
                    opts[foo[0]] = foo[1]
                else:
                    opts[foo[0]] = True
        return opts

    def get_opt(self, opt, opts, default=None):
        return opts[opt] if opt in opts.keys() else default if default else None

    def pc_setup_sleep(self, mins):
        """Set up PC sleep time in minutes"""
        if int(mins) > 5:
            cmd = 'powercfg -x standby-timeout-ac %s' % str(mins)
            self.subprocess_call(cmd)

    def allign_text(self, text, line_length, allign='center', alligner=' '):
        """Allign text inside line with given line length. Left/right gaps are filled by \'alligner\'"""
        foo = line_length - len(text)
        if 0 >= foo:
            return text
        else:
            if 'left' == allign:
                return text + foo * ' '
            elif 'right' == allign:
                return foo * ' ' + text
            elif 'center':
                return (foo / 2) * alligner + text + ((foo / 2) + (foo % 2)) * alligner
            else:
                self.log.error('Wrong \'allign\' value')
                return 'Wrong \'allign\' value'

    user_plots = ('plot_0', 'plot_0_blocked')

    def plt(self, func, *args, **kwargs):
        """Proxy to call matplotlib.pyplot methods. Plus some custom functionality"""

        if func in self.user_plots:  # 'user' plots methods
            getattr(self, func)(*args, **kwargs)
        else:  # 'pyplot' methods
            getattr(plt, func)(*args, **kwargs)

    def plot_0(self, *args, **kwargs):
        plt.close('all')
        plt.plot(*args, **kwargs)
        plt.grid()
        plt.axis('auto')
        plt.show(block=False)

    def plot_0_blocked(self, *args, **kwargs):
        plt.close('all')
        plt.plot(*args, **kwargs)
        plt.grid()
        plt.axis('auto')
        plt.show(block=True)
