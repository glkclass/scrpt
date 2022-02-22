import os.path as osp
import os
import shutil
import stat
import re
import humanize
# import subprocess
import util
import log_util

log = log_util.get_logger(__name__, level="INFO")


def get_dir_content(dir):
    """Walk into folder hierarchy, generate list of files"""
    total_files = []
    total_subdirs = []
    for root, subdirs, files in os.walk(dir):
        # print(root, subdirs)
        for filename in files:
            item = osp.join(root, filename)
            if item not in total_files:
                total_files.append(item)
        for subdir in subdirs:
            item = osp.join(root, subdir)
            if item not in total_subdirs:
                total_subdirs.append(item)
    return total_files, total_subdirs


def getsize(path):
    """Disk size in human readable format"""
    return humanize.naturalsize(os.stat(path).st_size)
    # return subprocess.check_output(['du', '-sh', path]).split()[0].decode('utf-8')


def mkdir(path):
    if not osp.exists(path):
        os.makedirs(path)
    else:
        if osp.isfile(path):
            log.error('Folder: \'%s\' wasn\'t created due to existing file of such name!' % path)
        else:
            log.info('Folder: \'%s\' already exists.' % path)


def find_patt(dir, pattern='.*'):
    """Find items inside folder matching given RE pattern"""
    if not osp.isdir(dir):
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
    item2remove = util.to_list(path)
    for item in item2remove:
        log.info('Removing %s ...' % item)
        if osp.exists(item):
            os.chmod(item, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            if osp.isfile(item):
                os.remove(item)
            elif osp.isdir(item):
                shutil.rmtree(item)
            else:
                log.error('Can\'t remove %s' % item)


def copy(src_path, dst_path):
    """Copy files & folders"""
    item2copy = util.to_list(src_path)
    for src_path in item2copy:
        log.debug('Copying %s (%s) to %s' % (src_path, getsize(src_path), dst_path))
        if osp.isfile(src_path):
            shutil.copy(src_path, dst_path)
        elif osp.isdir(src_path):
            if not osp.exists(dst_path):
                shutil.copytree(src_path, dst_path)
            else:
                log.error('Destination folder path %s must not exist!' % dst_path)
        else:
            log.error('Can\'t copy %s to %s' % (src_path, dst_path))
