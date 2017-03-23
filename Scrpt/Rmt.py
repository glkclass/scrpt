from sys import platform
import os
import fabric.api
import fabric.operations


import urllib2
from Scrpt_base import Scrpt_base
from Log import Log
from File import File

class Rmt(Scrpt_base):
    """Class 'Rmt' - contains 'remote access' utils: run remote session, upload, download, etc.
    To be embedded in others classes requiring such functionality"""

    log_message =   {
                        'upload': '\'Rmt.upload(...)\' status: %s',
                        'download': '\'Rmt.download(...)\' status: %s'
                    }

    default_settings =  {
                            'platform': platform,
                            'environ': {'PATH2CRDNTL': 'AVV_CRDNTL'},
                            'rmt': 'srv_34'
                        }

    def __init__(self, log=None, file=None, user_settings=None):
        settings = self.overwrite_settings(self.default_settings, user_settings)
        Scrpt_base.__init__(self, settings)
        self.log = log if log else Log.Log(settings)  # use external logger if exists, else create internal one
        self.file = file if file else File.File(settings)  # use external file lib if exists, else create internal one
        self.load_crdntl()

    def http(self):
        # response = urllib2.urlopen('link')
        response = urllib2.urlopen('link')
        html = response.read()
        self.log.info(str(html))

    def fab_init(self, crdntl):
        fabric.state.env['host_string'] = crdntl['user'] + '@' + crdntl['ip']
        fabric.state.env['password'] = crdntl['pass']
        fabric.state.env['timeout'] = 10
        fabric.state.env['stdout'] = self.log.fid

    def cmd(self, cmd, path='.'):
        """Login remote server via ssh and run cmd remotely"""
        self.fab_init(self.cfg['crdntl'][self.cfg['rmt']])
        with fabric.api.cd(path):
            if self.log.exists():
                fabric.api.run(cmd, stdout=self.log.fid, stderr=self.log.fid)
            else:
                fabric.api.run(cmd)

    def upload(self, localpath, remotepath, verbosity=0):
        """Upload <single file/group of files> to remote host via sftp"""
        self.fab_init(self.cfg['crdntl'][self.cfg['rmt']])
        localpath_list = self.make_list(localpath)
        ans = []
        for item in localpath_list:
            ans.append(fabric.operations.put(item, remotepath, use_sudo=False))

        self.log.info(self.log_message['upload'] % str(ans), verbosity)

    def download(self, remotepath='.', localpath='.', verbosity=0):
        """Download <single file/group of files> from remote host via sftp"""
        self.fab_init(self.cfg['crdntl'][self.cfg['rmt']])
        remotepath_list = self.make_list(remotepath)
        ans = []
        for item in remotepath_list:
            ans.append(fabric.operations.get(item, localpath, use_sudo=False))
        self.log.info(self.log_message['download'] % str(ans), verbosity)

    def load_crdntl(self, severity='silent'):
        if 'PATH2CRDNTL' not in self.cfg['environ'].keys():
            self.log.message('\'cfg[environ][PATH2CRDNTL]\' variable wasn\'t defined!!!', severity)
            self.log.message('User credentials weren\'t loaded!!!', severity)
        elif self.cfg['environ']['PATH2CRDNTL'] not in os.environ.keys():
            self.log.message('There is no such Env variable: \'%s\' !!!' % self.cfg['environ']['PATH2CRDNTL'], severity)
            self.log.message('User credentials weren\'t loaded!!!', severity)
        elif not os.path.isfile(os.environ[self.cfg['environ']['PATH2CRDNTL']]):
            self.log.message('User credentials weren\'t loaded!!!', severity)
        else:
            self.cfg['crdntl'] = self.file.load(os.environ[self.cfg['environ']['PATH2CRDNTL']], 'json')
