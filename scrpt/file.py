import re
import json
import yaml
import xml.etree.ElementTree
import pickle

import path
import util
import log_util

log = log_util.get_logger(__name__)


"""Module 'file' - contains utils working with 'file content': read, write, parse..."""


def load(path2file, format='txt'):
    loader = {'json': {'loader': json.load, 'filemode': 'r'},
              'yaml': {'loader': yaml.load, 'filemode': 'r'},
              'pkl': {'loader': pickle.load, 'filemode': 'rb'}}

    if not path.isfile(path2file):
        return None
    if 'txt' == format:
        with open(path2file, 'r') as txt:
            lines = txt.readlines()
        return lines
    elif 'xml' == format:
        with xml.etree.ElementTree.parse(path2file) as xml_root:
            return xml_root.getroot()
    elif format in loader:
        with open(path2file, loader[format]['filemode']) as fid:
            foo = loader[format]['loader'](fid)
            return foo


def save(data2store, path2file, format='txt', append=False, **kwargs):
    filemode = {True: 'a', False: 'w'}[append]
    saver = {'json': {'saver': json.dump, 'filemode': filemode},
             'pkl': {'saver': pickle.dump, 'filemode': filemode + 'b'}}

    if path.exists(path2file):
        log.info('%s will be overwritten' % path2file)
    if 'txt' == format:
        data2store = util.make_list(data2store)
        with open(path2file, filemode) as fid:
            for item in data2store:
                foo = str(item)
                fid.write(foo)
    elif format in saver:
        # json.dump(data2store, fid, sort_keys=True, indent=2)
        # pickle.dump(lst, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
        with open(path2file, saver[format]['filemode']) as fid:
            saver[format]['saver'](data2store, fid, **kwargs)
    else:
        log.error('Unsupported format: %s!' % format)


def remove_patt(path2txt, pattern2remove):
    """Parse txt files: remove lines containing given re patterns"""
    lines_in = load(path2txt, 'txt')
    if not lines_in:
        return
    patt_list = util.make_list(pattern2remove)
    lines_out = []
    for line in lines_in:
        for patt in patt_list:
            foo = re.search(patt, line)
            if foo:
                break
        else:
            lines_out.append(line)
    save(lines_out, path2txt, 'txt')


def find_patt(path2txt, pattern2find):
    """Parse txt files: find lines containing given re patterns"""
    lines = load(path2txt, 'txt')
    if lines is None:
        return None

    pattern2find = util.make_list(pattern2find)
    lines_out = {item: None for item in pattern2find}
    for line in lines:
        for patt in pattern2find:
            foo = re.search(patt, line)
            if foo:
                if lines_out[patt] is not None:
                    lines_out[patt].append(foo)
                else:
                    lines_out[patt] = [foo]
    return lines_out
