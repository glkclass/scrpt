import argparse


"""Module "arg" - contains stuff used for script input args maintenance"""
parser = argparse.ArgumentParser(description='Scrpt', formatter_class=argparse.RawTextHelpFormatter)


def _add_arg(name, type, default, choices, help):
    if default is not None:
        parser.add_argument('--%s' % name, type=type, help=help, default=default, choices=choices)
    else:
        parser.add_argument('%s' % name, type=int, help=help, choices=choices)


def define_int(name, default=None, choices=None, help=None):
    _add_arg(name, int, default, choices, help)


def define_str(name, default=None, choices=None, help=None):
    _add_arg(name, str, default, choices, help)


def parse(args_str=None):
    """Parse scrpt input arguments"""
    args = parser.parse_args(args_str)
    return args
