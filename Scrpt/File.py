from sys import platform
import shutil
import re
import json
import yaml
import xml.etree.ElementTree
import zipfile

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

    def __init__(self, log=None, settings=None):
        default_settings =  {
                                'print_cmd': False,
                            }
        Scrpt_base.__init__(self, default_settings)
        self.log = log if log else Log.Log(default_settings)  # use external logger if exists, else create internal logger instance
        self.path = Path(self.log, default_settings)
        self.setup(settings)

    def setup(self, settings=None):
        """ Add/update File and embedded unit settings"""
        Scrpt_base.setup(self, settings)
        self.log.setup(settings)
        self.path.setup(settings)

    def load(self, format, path2file, strip=None, severity='silent'):
        loader = {'json': json.load, 'yaml': yaml.load}
        if not self.path.isfile(path2file, 'load(\'%s\' ...)' % format, severity):
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

    def save(self, format, data2store, path2file, severity='silent'):
        self.path.exists(path2file, 'save(\'%s\' ...)' % format, severity)
        fid = open(path2file, 'w')
        data2store_list = self.path.make_list(data2store)
        for item in data2store_list:
            if 'txt' == format:
                fid.write(str(item) + '\n')
            elif 'json' == format:
                json.dump(item, fid, sort_keys=True, indent=4)
        fid.flush()
        fid.close()

    def pack(self, path2src, path2dst_file, archivator='zip', severity='silent'):
        """linux 'pack folder cmd' line: tar -zcvf dst_file.tzr.gx src_folder"""
        if not self.path.exists(path2src, 'pack(...)', severity):
            return None
        log_message = self.log_message['pack'] % (path2src, path2dst_file)
        self.log.info(log_message)
        if self.cfg['print_cmd']:
            return

        archivator = str(archivator)
        if 'zip' == archivator:
            if self.path.isfile(path2src, severity='silent'):
                path2dst_file += '.%s' % archivator
                with zipfile.ZipFile(path2dst_file, 'w') as myzip:
                    myzip.write(path2src)
                    myzip.close()
            elif self.path.isdir(path2src, severity='silent'):
                shutil.make_archive(path2dst_file, archivator, path2src)

    def unpack(self, path2src_file, path2dst_folder, archivator='zip', severity='silent'):
        if not self.path.isfile(path2src_file, 'unpack(...)', severity):
            return None
        log_message = self.log_message['unpack'] % (path2src_file, path2dst_folder)
        self.log.info(log_message)
        if self.cfg['print_cmd']:
            return
        if 'zip' == str(archivator):
            with zipfile.ZipFile(path2src_file, 'r') as myzip:
                myzip.extractall(path2dst_folder)

    def remove_patt(self, path_2_txt, pattern_2_remove, severity='silent'):
        lines_in = self.load('txt', path_2_txt, severity=severity)
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
