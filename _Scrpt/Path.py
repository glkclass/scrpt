from sys import platform
import os.path
import os
import shutil
import stat
import re

from Scrpt_base import Scrpt_base
from Log import Log


class Path(Scrpt_base):
    """Class 'Path' - contains 'file/folder path process' utils: check existence, copy, remove, create, etc.
    To be embedded in others classes requiring such functionality"""

    log_message =   {
                        'isfile': 'There is no such file: \'%s\'!',
                        'isdir': 'There is no such folder: \'%s\'!',
                        'exists': 'There is no such path: \'%s\'!',
                        
                        'mkdir':    {
                                        'file_exists': 'The folder: \'%s\' wasn\'t created due to existing file of same name!',
                                        'folder_exists': 'The folder: \'%s\' already exists.',
                                        'folder_doesnt_exist': 'The folder \'%s\' doesn\'t exist. Has been created...'
                                    },

                        'remove':   {
                                        'item_exists': 'Removing %s ...'
                                    },


                        'move':     {
                                        'item_exists': 'Moving %s to %s...'
                                    },

                        'copy_dir_content': {
                                                'src_folder_exists': 'Copying folder content \'%s\' -> \'%s\' ...',
                                                'src_item_exists': 'Copying folder item \'%s\' -> \'%s\' ...',
                                                'src_folder_doesnt_exist': 'The folder \'%s\' doesn\'t exist!',
                                                'dst_folder_doesnt_exist': 'The folder \'%s\' doesn\'t exist. Has been created...'
                                            },

                        'remove_dir_content':   {
                                                    'folder_exists': 'Removing folder content: \'%s\' ...',
                                                    'item_exists': 'Removing item: \'%s\' ...',
                                                    'folder_doesnt_exist': 'The folder \'%s\' doesn\'t exist!',
                                                }
                    }

    default_settings = {'print_cmd': False}

    def __init__(self, log, user_settings=None):
        Scrpt_base.__init__(self, self.default_settings)
        self.update_settings(user_settings)
        self.log = log  # logger should be define outside

    def isfile(self, path, verbosity=20):
        path_list = self.make_list(path)
        for path in path_list:
            if not os.path.isfile(path):
                self.log.log(verbosity, self.log_message['isfile'] % path)
                return False
            else:
                return True

    def isdir(self, path, verbosity=20):
        path_list = self.make_list(path)
        for path in path_list:
            if not os.path.isdir(path):
                self.log.log(verbosity, self.log_message['isdir'] % path)
                return False
            else:
                return True

    def exists(self, path, verbosity=20):
        path_list = self.make_list(path)
        for path in path_list:
            if not os.path.exists(path):
                self.log.log(verbosity, self.log_message['exists'] % path)
                return False
            else:
                return True

    def mkdir(self, path, verbosity=20):
        if not os.path.exists(path):
            os.makedirs(path)
            self.log.log(verbosity, self.log_message['mkdir']['folder_doesnt_exist'] % path)
        else:
            if os.path.isfile(path):
                self.log.log(verbosity, self.log_message['mkdir']['file_exists'] % path)
            else:
                self.log.log(verbosity, self.log_message['mkdir']['folder_exists'] % path)

    def remove(self, path, verbosity=20):
        path_list = self.make_list(path)
        for path in path_list:
            self.log.log(verbosity, self.log_message['remove']['item_exists'] % path)
            if self.exists(path):
                os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                if os.path.isfile(path):
                    os.remove(path)
                elif self.isdir(path):
                    shutil.rmtree(path)

    def move(self, src, dst, verbosity=20):
        path_list = self.make_list(src)
        for path in path_list:
            self.log.log(verbosity, self.log_message['move']['item_exists'] % (src, dst))
            if self.exists(src):
                os.chmod(src, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                shutil.move(src, dst)

    def copy_dir_content(self, src, dst, items=None, verbosity=20):
        if not self.isdir(src, verbosity):
            return
        if self.cfg['print_cmd']:
            return
        if not self.isdir(dst):
            self.mkdir(dst, verbosity=0)
            self.log.log(verbosity, self.log_message['copy_dir_content']['dst_folder_doesnt_exist'] % dst)
        self.log.log(verbosity, self.log_message['copy_dir_content']['src_folder_exists'] % (src, dst))
        src_dir_item = self.make_list(items) if items is not None else os.listdir(src)
        for item in src_dir_item:
            src_item = os.path.join(src, item)
            self.log.log(verbosity, self.log_message['copy_dir_content']['src_item_exists'] % (src_item, dst))
            if os.path.isfile(src_item):
                shutil.copy(src_item, dst)
            elif self.isdir(src_item):
                shutil.copytree(src_item, os.path.join(dst, item))

    def remove_dir_content(self, path, verbosity=20):
        if not self.isdir(path):
            return
        self.log.log(verbosity, self.log_message['remove_dir_content']['folder_exists'] % path)
        if self.cfg['print_cmd']:
            return
        dir_item_list = os.listdir(path)
        for item in dir_item_list:
            path_item = os.path.join(path, item)
            self.log.log(verbosity, self.log_message['remove_dir_content']['item_exists'] % path_item)
            if os.path.isfile(path_item):
                os.remove(path_item)
            elif self.isdir(path_item):
                shutil.rmtree(path_item)

    def remove_patt(self, folder, pattern_2_remove, verbosity=20):
        """Remove path based on given pattern"""
        if not self.isdir(folder):
            return
        self.log.log(verbosity, self.log_message['remove_dir_content']['folder_exists'] % folder)
        if self.cfg['print_cmd']:
            return
        patt_list = self.make_list(pattern_2_remove)
        dir_item_list = os.listdir(folder)
        for item in dir_item_list:
            for patt in patt_list:
                foo = re.search(patt, item)
                if foo:
                    break
            else:
                continue
            path_item = os.path.join(folder, item)
            self.log.log(verbosity, self.log_message['remove_dir_content']['item_exists'] % path_item)
            if os.path.isfile(path_item):
                os.remove(path_item)
            elif self.isdir(path_item):
                shutil.rmtree(path_item)

    def find_patt(self, folder, pattern_2_find, verbosity=20):
        """Find path based on given pattern"""
        if not self.isdir(folder):
            return None, None

        found_path = []
        parsed_path = []
        patt_list = self.make_list(pattern_2_find)
        dir_item_list = os.listdir(folder)
        for item in dir_item_list:
            # self.log.info(item)
            for patt in patt_list:
                foo = re.search(patt, item)
                if foo:                
                    # path_item = os.path.join(folder, item)
                    path_item = item
                    found_path.append(path_item)
                    parsed_path.append(foo)
                    break
        return found_path, parsed_path
