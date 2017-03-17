from sys import platform
import os.path
import os
import re
import subprocess

from Scrpt_base import Scrpt_base
from Log import Log
from Rmt import Rmt
from Path import Path
from File import File


class Util(Scrpt_base):
    """Class 'Util' - contains basic utils (may be embedded in appropriate classes).
    To be embedded in others classes requiring such functionality."""

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
        settings = self.overwrite_settings(self.default_settings, user_settings)  # propagate settings
        Scrpt_base.__init__(self, settings)
        self.log = log if log else Log.Log(settings)  # use external logger if exists, else create internal logger instance
        self.path = Path(self.log, settings)
        self.file = File(self.log, settings)
        self.rmt = Rmt(self.log, self.file, settings)


    def get_folder_item(self, dir, file_pattern, severity='silent'):
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
            self.log.message(self.log_message['get_folder_item'], severity)
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

    def subprocess_call(self, cmd, verbosity=1, shl=True):
        """Execute external command."""
        cmd_list = self.make_list(cmd)
        for cmd in cmd_list:
            self.log.cmd(cmd)
            if 'shutdown' in cmd and not self.cfg['print_cmd']:  # close log file if command='shutdown ...' and 'print_cmd' mode isn't enabled
                self.log.close()
            if self.cfg['print_cmd']:
                continue
            if self.log.log:
                subprocess.call(cmd, shell=shl, stdout=self.log.log, stderr=self.log.log)
            else:
                subprocess.call(cmd, shell=shl)

    def environ(self, name_value, verbosity=1, severity='silent'):
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
            self.log.info(self.log_message['environ']['success'] % (envar_name, os.environ[envar_name]), verbosity)
        else:  # read env var
            envar_name = name_value
            if envar_name not in os.environ.keys():
                self.log.message(self.log_message['environ']['fail'] % envar_name, severity)
                return None
            else:
                self.log.info(self.log_message['environ']['success'] % (envar_name, os.environ[envar_name]), verbosity)

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

        # TODO: port av.artefacts
