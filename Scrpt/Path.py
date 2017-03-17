from sys import platform
import os.path
import os
import shutil
import stat

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
                                        'file_exists': 'The dir: \'%s\' wasn\'t created due to existing file of same name!',
                                        'folder_exists': 'The dir: \'%s\' already exists.',
                                        'folder_doesnt_exist': 'The folder \'%s\' doesn\'t exist. Has been created...'
                                    },

                        'remove':   {
                                        'folder_exists': 'Removing %s ...',
                                        'folder_doesnt_exist': 'The folder \'%s\' doesn\'t exist!',
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

    def __init__(self, log=None, user_settings=None):
        settings = self.overwrite_settings(self.default_settings, user_settings)  # propagate settings
        Scrpt_base.__init__(self, settings)
        self.log = log if log else Log.Log(settings)  # use external logger if exists, else create internal logger instance

    def isfile(self, path, msg=None, severity='silent'):
        path_list = self.make_list(path)
        for path in path_list:
            if not os.path.isfile(path):
                log_message = '%s -> %s' % (msg, self.log_message['isfile'] % path) if msg else self.log_message['isfile'] % path
                self.log.message(log_message, severity)
                return False
            else:
                return True

    def isdir(self, path, msg=None, severity='silent'):
        path_list = self.make_list(path)
        for path in path_list:
            if not os.path.isdir(path):
                log_message = '%s -> %s' % (msg, self.log_message['isdir'] % path) if msg else self.log_message['isdir'] % path
                self.log.message(log_message, severity)
                return False
            else:
                return True

    def exists(self, path, msg=None, severity='silent'):
        path_list = self.make_list(path)
        for path in path_list:
            if not os.path.exists(path):
                log_message = '%s -> %s' % (msg, self.log_message['exists'] % path) if msg else self.log_message['exists'] % path
                self.log.message(log_message, severity)
                return False
            else:
                return True

    def mkdir(self, path, msg=None, severity='silent', verbosity=1):
        if not os.path.exists(path):
            os.makedirs(path)
            self.log.info(self.log_message['mkdir']['folder_doesnt_exists'] % path, verbosity)
        else:
            if os.path.isfile(path):
                self.log.message(self.log_message['mkdir']['file_exists'] % path, 'fail')
            else:
                self.log.info(self.log_message['mkdir']['folder_exists'] % path, verbosity)

    def remove(self, path, severity='silent', verbosity=1):
        path_list = self.make_list(path)
        for path in path_list:
            self.log.info(self.log_message['remove']['folder_exists'] % path, verbosity)
            if self.exists(path, self.log_message['remove']['folder_doesnt_exist'] % path, severity):
                os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                if os.path.isfile(path):
                    os.remove(path)
                elif self.isdir(path):
                    shutil.rmtree(path)

    def copy_dir_content(self, src, dst, items=None, severity='error', verbosity=1):
        if not self.isdir(src, self.log_message['copy_dir_content']['src_folder_doesnt_exist'] % src, severity):
            return
        if self.cfg['print_cmd']:
            return
        if not self.isdir(dst):
            self.mkdir(dst, verbosity=0)
            self.log.info(self.log_message['copy_dir_content']['dst_folder_doesnt_exist'] % dst, verbosity)
        self.log.info(self.log_message['copy_dir_content']['src_folder_exists'] % (src, dst), verbosity)
        src_dir_item = self.make_list(items) if items is not None else os.listdir(src)
        for item in src_dir_item:
            src_item = os.path.join(src, item)
            self.log.info(self.log_message['copy_dir_content']['src_item_exists'] % (src_item, dst), verbosity)
            if os.path.isfile(src_item):
                shutil.copy(src_item, dst)
            elif self.isdir(src_item):
                shutil.copytree(src_item, os.path.join(dst, item))

    def remove_dir_content(self, path, severity='silent', verbosity=1):
        if not self.isdir(path, self.log_message['remove_dir_content']['folder_doesnt_exist'] % path, severity):
            return
        self.log.info(self.log_message['remove_dir_content']['folder_exists'] % path, verbosity)
        if self.cfg['print_cmd']:
            return
        dir_item_list = os.listdir(path)
        for item in dir_item_list:
            path_item = os.path.join(path, item)
            self.log.info(self.log_message['remove_dir_content']['item_exists'] % path_item, verbosity)
            if os.path.isfile(path_item):
                os.remove(path_item)
            elif self.isdir(path_item):
                shutil.rmtree(path_item)


