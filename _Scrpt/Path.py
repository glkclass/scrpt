from sys import platform
import os.path
import os
import shutil
import stat
import re
import humanize
# import subprocess
import logging
import util


def get_dir_content(dir):
    """Walk into folder hierarchy, generate list of files"""
    total_files = []
    total_subdirs = []
    for root, subdirs, files in os.walk(dir):
        # print(root, subdirs)
        for filename in files:
            item = os.path.join(root, filename)
            if item not in total_files:
                total_files.append(item)
        for subdir in subdirs:
            item = os.path.join(root, subdir)
            if item not in total_subdirs:
                total_subdirs.append(item)
    return total_files, total_subdirs


def getsize(path):
    """Disk size in human readable format"""
    return humanize.naturalsize(os.stat(path).st_size)
    # return subprocess.check_output(['du', '-sh', path]).split()[0].decode('utf-8')


def convert2lnx(path2convert):
    return path2convert.replace('\\', '/')


def isfile(path):
    if not os.path.isfile(path):
        logging.info('There is no such file: \'%s\'!' % path)
        return False
    else:
        return True


def isdir(path):
    if not os.path.isdir(path):
        logging.info('There is no such folder: \'%s\'!' % path)
        return False
    else:
        return True


def exists(path):
    if not os.path.exists(path):
        logging.info('There is no such path: \'%s\'!' % path)
        return False
    else:
        return True


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        if os.path.isfile(path):
            logging.error('Folder: \'%s\' wasn\'t created due to existing file of such name!' % path)
        else:
            logging.info('Folder: \'%s\' already exists.' % path)


def find_patt(dir, pattern='.*'):
    """Find items inside folder matching given RE pattern"""
    if not isdir(dir):
        return None
    items_found = []
    dir_files, dir_subdirs = get_dir_content(dir)
    for item in dir_files + dir_subdirs:
        foo = re.search(pattern, item)
        if foo:
            items_found.append(item)
    return items_found


def remove(path):
    """Remove items"""
    item2remove = util.make_list(path)
    for item in item2remove:
        logging.log('Removing %s ...' % item)
        if exists(item):
            os.chmod(item, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            if os.path.isfile(item):
                os.remove(item)
            elif isdir(item):
                shutil.rmtree(item)
            else:
                logging.error('Can\'t remove %s' % item)


def copy(src_path, dst_path):
    """Copy firls & folders"""
    item2copy = util.make_list(src_path)
    for src_path in item2copy:
        logging.info('Copying %s (%s) to %s' % (src_path, getsize(src_path), dst_path))
        if os.ath.isfile(src_path):
            shutil.copy(src_path, dst_path)
        elif isdir(src_path):
            if not exists(dst_path):
                shutil.copytree(src_path, dst_path)
            else:
                logging.error('Destination folder path %s must not exist!' % dst_path)
        else:
            logging.error('Can\'t copy %s to %s' % (src_path, dst_path))
