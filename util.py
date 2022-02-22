#!/usr/bin python
"""Different util: timing, ..."""

import os
import socket
import datetime
import time
import subprocess

import log_util

log = log_util.get_logger(__name__, level="INFO")

def allign_text(text, line_length, allign='center', alligner=' '):
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
            return int(foo / 2) * alligner + text + (int(foo / 2) + (foo % 2)) * alligner
        else:
            log.error('Wrong \'allign\' value')
            return 'Wrong \'allign\' value'


def environ(name_value):
    """ Set/read environment variable.
        Use cases:
        environ('ENVAR_NAME=ENVAR_VALUE')
        environ('ENVAR_NAME')
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
        log.info('Env variable: %s = %s' % (envar_name, os.environ[envar_name]))
    else:  # read env var
        envar_name = name_value
        if envar_name not in os.environ.keys():
            log.error('There is no such Env variable: %s !!!' % envar_name)
            return None
        else:
            log.info('Env variable: %s = %s' % (envar_name, os.environ[envar_name]))

    return os.environ[envar_name]


def parse_opt(opts, opt_line=''):
    """Parse options line which has following structure: 'opt0|opt1|opt2=3| opt4 | opt5=0 ...'"""
    options = str(opt_line).split('|')
    options = [item.strip() for item in options]  # remove whitespases
    for item in options:
        foo = item.split('=')
        foo = [item.strip() for item in foo]
        if len(foo) > 1:
            opts[foo[0]] = foo[1]
        else:
            opts[foo[0]] = True
    return opts


def subprocess_call(cmd, shl=True):
    """TODO: need to rethink/rewrite this util"""
    cmd_list = to_list(cmd)
    for cmd in cmd_list:
        log.debug(cmd)
        # if cfg['print_cmd']:
        #     continue
        if 'shutdown' in cmd:  # close log file if command='shutdown ...'
            log_util.shutdown()
            subprocess.run(
                cmd, shell=shl, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            foo = subprocess.run(
                cmd, shell=shl, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, universal_newlines=True)
            stdout = foo.stdout.split('\n')
            for item in stdout:
                log.debug(item)
            return foo


def dict_create_key_hier(foo, keys, type='dict'):
    """Create following dictonary element: dict[keys_0][keys_1]...[keys_n-1] = {} or [].
    Type of created inner element (dict or list) is defined by 'type' parameter"""
    keys = to_list(keys)
    for key in keys[:-1]:
        if key not in foo.keys():
            foo[key] = {}
        foo = foo[key]
    if keys[-1] not in foo.keys():
        foo[keys[-1]] = {} if 'dict' == type else []


def dict_has_key_hier(foo, keys):
    """Check whether dictonary has following element: dict[keys_0][keys_1]...[keys_n-1]"""
    keys = to_list(keys)
    for key in keys:
        if key in foo.keys():
            foo = foo[key]
        else:
            return False


def get_hostip():
    return socket.gethostbyname(get_hostname())


def get_hostname():
    return socket.gethostname()


def to_list(item):
    return [item] if not isinstance(item, (list, tuple)) else item


def get_unique_time_pattern():
    """ Return string pattern corresponding to current time (including microseconds)"""
    now = datetime.datetime.now()
    time_pattern = '%d_%02d_%02d_%02d_%02d_%02d_%06d' % (now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)
    return time_pattern


# timing util
weekday = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
month = ('Dummy', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')


def get_time():
    """ Get system date/time in different formats"""
    foo = {}
    now = datetime.datetime.now().replace(microsecond=0)
    foo['now'] = now
    foo['month'] = month[now.month]
    foo['weekday'] = weekday[now.weekday()]
    foo['weeknum'] = now.isocalendar()[1]

    foo['time'] = '%02d:%02d:%02d' % (now.hour, now.minute, now.second)
    foo['time_wo_s'] = '%02d:%02d' % (now.hour, now.minute)
    foo['date'] = '%04d/%02d/%02d' % (now.year, now.month, now.day)
    foo['dt'] = '%04d/%02d/%02d  %02d:%02d:%02d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    foo['dt_tag'] = '%04dy%02dm%02dd_%02dh%02dm%02ds' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    foo['dt_wo_y_tag'] = '%02dm%02dd_%02dh%02dm%02ds' % (now.month, now.day, now.hour, now.minute, now.second)
    foo['dt_wo_ys_tag'] = '%02dm%02dd_%02dh%02dm' % (now.month, now.day, now.hour, now.minute)
    return foo


def get_week(date):
    """Get week day and week number from the start of the year"""
    ymd = [int(item) for item in date.split('/')]
    return{
                'num': datetime.date(ymd[0], ymd[1], ymd[2]).isocalendar()[1],
                'day': weekday[datetime.date(ymd[0], ymd[1], ymd[2]).weekday()]
    }


start_timestamp = get_time()['now']  # timestamp to be used by get_timedelta


def get_timedelta(timestamp=None):
    """ Measure time interval from start timestamp (should be set in advance)"""
    timestamp = start_timestamp if not isinstance(timestamp, datetime.datetime) else timestamp
    tme = datetime.datetime.now().replace(microsecond=0)
    set_timestamp()
    return tme - timestamp


def set_timestamp():
    """ Set timestamp"""
    global start_timestamp
    start_timestamp = get_time()['now']
    return start_timestamp


def sleep(time2sleep=None):
    """Generate pause for 'time2sleep' seconds during execution..."""
    if time2sleep:
        hours = time2sleep / 3600
        minutes = (time2sleep % 3600) / 60
        seconds = time2sleep % 60
        log.info('Sleeping for %02dh:%02dm:%02ds ...' % (hours, minutes, seconds))
        time.sleep(time2sleep)
        log.info('Resuming ...')
    return time2sleep


def pc_setup_sleep(mins):
    """Set up System_power_settings:PC_sleep_interval in minutes"""
    if int(mins) > 5:
        cmd = 'powercfg -x standby-timeout-ac %s' % str(mins)
        subprocess_call(cmd)
    else:
        log.error('Too short time for pc sleep interaval!!!')


def pc_shutdown(opt=''):
    """Set up System_power_settings:PC_sleep_interval=120 min and shutdown(hibernate) PC"""
    pc_setup_sleep(120)
    cmd = 'shutdown %s' % str(opt)  # shutdown or shutdown /h
    subprocess_call(cmd)
