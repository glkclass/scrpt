from sys import platform
# import shutil
import re
import json
import yaml
import xml.etree.ElementTree
import zipfile
import tarfile
import os

from Scrpt_base import Scrpt_base
from Log import Log
from Path import Path


class File(Scrpt_base):
    """Class 'File' - contains 'file/folder content process' utils: read, write, prase, pack/ etc.
    To be embedded in others classes requiring such functionality"""

    log_message =   {
                        'pack': 'Packing %s to %s ...',
                        'unpack': 'Unpacking %s to %s ...',
                    }
    default_settings = {'print_cmd': False}

    def __init__(self, log, user_settings=None):
        Scrpt_base.__init__(self, self.default_settings)
        self.update_settings(user_settings)
        self.log = log  # logger should be define outside
        self.path = Path(self.log, self.cfg)

    def load(self, path2file, format='txt', strip=None, verbosity=20):
        loader = {'json': json.load, 'yaml': yaml.load}
        if not self.path.isfile(path2file, verbosity):
            return None
        if 'txt' == format:
            with open(path2file, 'r') as txt:
                lines = txt.readlines()
            lines = [line.strip(strip) for line in lines]
            txt.close()
            return lines
        elif 'xml' == format:
            with xml.etree.ElementTree.parse(path2file) as xml_root:
                return xml_root.getroot()
        elif format in loader.keys():
            with open(path2file, 'r') as fid:
                foo = loader[format](fid)
                fid.close()
                return foo

    def save(self, data2store, path2file, format='txt', fo_mode='w', eol='\n', verbosity=20):
        self.path.exists(path2file, verbosity)
        file_open_mode = {'w': 'w', 'a': 'a'}[fo_mode]
        fid = open(path2file, file_open_mode)
        if 'txt' == format:
            if type(data2store) in (list, tuple):
                for item in data2store:
                    fid.write(str(item) + eol)
            else:
                fid.write(str(item) + eol)
        elif 'json' == format:
            json.dump(data2store, fid, sort_keys=True, indent=4)
        fid.flush()
        fid.close()

    def pack(self, path2src, dst_basename='', arch_name='zip', arch_h=None, verbosity=20):
        arch_name = str(arch_name)
        dst_filename = dst_basename + '.' + arch_name
        if not self.path.exists(path2src, verbosity):
            return None
        if dst_basename:
            self.log.info(self.log_message['pack'] % (path2src, dst_filename))
        if self.cfg['print_cmd']:
            return

        if not arch_h:
            if 'zip' == arch_name:
                arch_h = zipfile.ZipFile(dst_filename, 'w')
            elif 'tar' == arch_name:
                arch_h = tarfile.open(dst_filename, "w")
            elif 'tar.gz' == arch_name:
                arch_h = tarfile.open(dst_filename, "w:gz")

        for item2pack in self.make_list(path2src):
            if self.path.isfile(item2pack, verbosity=20):
                if 'zip' == arch_name:
                    arch_h.write(item2pack)
                elif arch_name in ('tar', 'tar.gz'):
                    arch_h.add(item2pack)
            elif self.path.isdir(item2pack, verbosity=20):
                dir_items = os.listdir(item2pack)
                for dir_item in dir_items:
                    dir_item2pack = os.path.join(item2pack, dir_item)
                    if self.path.isfile(dir_item2pack, verbosity=20):
                        if 'zip' == arch_name:
                            arch_h.write(dir_item2pack)
                        elif arch_name in ('tar', 'tar.gz'):
                            arch_h.add(dir_item2pack)
                    elif self.path.isdir(dir_item2pack, verbosity=20):
                        self.pack(dir_item2pack, arch_name=arch_name, arch_h=arch_h)
        if dst_basename:
            arch_h.close()

    def unpack(self, path2archive, path2dst, arch_name='zip', arch_h=None, verbosity=20):
        if not self.path.isfile(path2archive, 'unpack(...)', verbosity):
            return None
        log_message = self.log_message['unpack'] % (path2archive, path2dst)
        self.log.info(log_message)
        if self.cfg['print_cmd']:
            return

        if not arch_h:
            if 'zip' == arch_name:
                arch_h = zipfile.ZipFile(path2archive, 'r')
            elif 'tar' == arch_name:
                arch_h = tarfile.open(path2archive, "r")
            elif 'tar.gz' == arch_name:
                arch_h = tarfile.open(path2archive, "r:gz")
        arch_h.extractall(path2dst)
        arch_h.close()

    def remove_patt(self, path_2_txt, pattern_2_remove, verbosity=20):
        lines_in = self.load(path_2_txt, 'txt', verbosity=verbosity)
        if not lines_in:
            return
        patt_list = self.make_list(pattern_2_remove)
        lines_out = []
        for line in lines_in:
            for patt in patt_list:
                foo = re.search(patt, line)
                if foo:
                    break
            else:
                lines_out.append(line)
        self.save('txt', lines_out, path_2_txt)

    def find_patt(self, path_2_txt, pattern_2_find, verbosity=20):
        lines_in = self.load(path_2_txt, 'txt', verbosity=verbosity)
        found_lines = []
        parsed_lines = []
        if not lines_in:
            return found_lines, parsed_lines

        patt_list = self.make_list(pattern_2_find)
        for line in lines_in:
            for patt in patt_list:
                foo = re.search(patt, line)
                if foo:
                    found_lines.append(line)
                    parsed_lines.append(foo)
                    break
        return found_lines, parsed_lines
