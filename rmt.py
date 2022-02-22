#!/usr/bin python
"""Remote host access util: upload/download/run commands"""
import warnings
import urllib
import os

# supress these paramiko warnings
warnings.filterwarnings("ignore", message=r"encode_point has been deprecated")
warnings.filterwarnings("ignore", message=r"Support for unsafe construction of public numbers from encoded data will be removed in a future version")


# import sys
from fabric import Connection
import path
import log_util

cfg = None
rmtc = None
log = log_util.get_logger(__name__, level="INFO")


def configure(cfg_):
    """First of all user should configure rmt access service: setup remote host, user, password
    cfg_ - dict containing appropriate config fields
    """
    global cfg  # remote host config
    global rmtc  # fabric.connection instance
    cfg = {key: cfg_[key] for key in ['host', 'user', 'password']}
    rmtc = Connection(host=cfg['host'], user=cfg['user'], connect_kwargs={'password': cfg['password']}, connect_timeout=10)


def run(cmd):
    """Login remote host via ssh and run given command
    cmd - command to execute remotely
    return - command log
    """
    if cfg is not None:
        return rmtc.run(cmd)
    else:
        log.error('Unable to execute. \'rmt\' wasn\'t configured!!!')
        return None


def upload(localpath, remotepath=''):
    """Upload <single file/group of files> to remote host using sftp
    localpath - local filename(s)
    remotepath - remote filename(s)
    return - list of uploaded files
    """
    if cfg is not None:
        local_path_list = [localpath] if not isinstance(localpath, (list, tuple)) else localpath
        remote_path_list = [remotepath] if not isinstance(remotepath, (list, tuple)) else remotepath

        if 1 == len(remote_path_list):
            remote_path_list = remote_path_list * len(local_path_list)

        if len(remote_path_list) != len(local_path_list):
            log.error('Unable to execute upload. Number of remote (destination) paths doesn\'t match to number of local (source) ones!!!\n%s\nvs\n%s' % (remote_path_list, local_path_list))
            return None

        uploaded = []
        for remote_item, local_item in zip(remote_path_list, local_path_list):
            if path.isfile(local_item):
                log.info('%s will be uploaded to %s::/%s' % (path.getsize(local_item), cfg['host'], remote_item))
                res = rmtc.put(local_item, remote_item)
                log.info('Uploaded %s to %s' % (res.local, res.remote))
                uploaded.append(res.remote)
        return uploaded
    else:
        log.error('Unable to execute. \'rmt\' wasn\'t configured!!!')
        return None


def download(remotepath, localpath=''):
    """Download <single file/group of files> from remote host
    localpath - local filename(s)
    remotepath - remote filename(s)
    return - list of downloaded files
    """
    if cfg is not None:
        remote_path_list = [remotepath] if not isinstance(remotepath, (list, tuple)) else remotepath
        local_path_list = [localpath] if not isinstance(localpath, (list, tuple)) else localpath

        if 1 == len(local_path_list):
            local_path_list = local_path_list * len(remote_path_list)

        if len(remote_path_list) != len(local_path_list):
            log.error('Unable to execute download. Number of local (destination) paths doesn\'t match to number of remote (source) ones!!!')
            return None

        downloaded = []
        for remote_item, local_item in zip(remote_path_list, local_path_list):
            log.info('%s will be downloaded from %s' % (remote_item, cfg['remote_host']))
            if os.path.isdir(local_item):  # fix fabric bug: add filename when local_path is folder
                local_item = os.path.join(local_item, os.path.basename(remote_item))
            try:
                res = rmtc.get(remote_item, local_item)
            except (IOError) as e:
                log.error(e)
                continue
            log.info('Downloaded %s to %s' % (res.remote, res.local))
            downloaded.append(res.local)
        return downloaded
    else:
        log.error('Unable to execute. \'rmt\' wasn\'t configured!!!')
        return None


def http(link):
    # response = urllib2.urlopen('link')
    html = urllib.urlopen(link).read()
    return str(html)
