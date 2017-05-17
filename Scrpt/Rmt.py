from sys import platform
import os
import fabric.api
import fabric.operations
import logging

import urllib
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
        Scrpt_base.__init__(self, self.default_settings)
        self.update_settings(user_settings)
        if log:
            self.log = log  # use external logger if exists
        else:
            # create own Logger
            logging.setLoggerClass(Log.Log)
            self.log = logging.getLogger(__name__)
        self.file = file if file else File.File(self.settings)  # use external file lib if exists, else create internal one
        self.load_crdntl()

    def http(self):
        # response = urllib2.urlopen('link')
        response = urllib.urlopen('link')
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
            if self.log:
                fabric.api.run(cmd, stdout=self.log.hdlr, stderr=self.log.hdlr)
            else:
                fabric.api.run(cmd)

    def upload(self, localpath, remotepath, verbosity=20):
        """Upload <single file/group of files> to remote host via sftp"""
        self.fab_init(self.cfg['crdntl'][self.cfg['rmt']])

        localpath_list = self.make_list(localpath)
        ans = []
        for item in localpath_list:
            ans.append(fabric.operations.put(item, remotepath, use_sudo=False))

        self.log.log(verbosity, self.log_message['upload'] % str(ans))

    def download(self, remotepath='.', localpath='.', verbosity=20):
        """Download <single file/group of files> from remote host via sftp"""
        self.fab_init(self.cfg['crdntl'][self.cfg['rmt']])
        remotepath_list = self.make_list(remotepath)
        ans = []
        for item in remotepath_list:
            ans.append(fabric.operations.get(item, localpath, use_sudo=False))
        self.log.log(verbosity, self.log_message['download'] % str(ans))

    def load_crdntl(self, verbosity=20):
        if 'PATH2CRDNTL' not in self.cfg['environ'].keys():
            self.log.log(verbosity, '\'cfg[environ][PATH2CRDNTL]\' variable wasn\'t defined!!!')
            self.log.log(verbosity, 'User credentials weren\'t loaded!!!')
        elif self.cfg['environ']['PATH2CRDNTL'] not in os.environ.keys():
            self.log.log(verbosity, 'There is no such Env variable: \'%s\' !!!' % self.cfg['environ']['PATH2CRDNTL'])
            self.log.log(verbosity, 'User credentials weren\'t loaded!!!')
        elif not os.path.isfile(os.environ[self.cfg['environ']['PATH2CRDNTL']]):
            self.log.log(verbosity, 'User credentials weren\'t loaded!!!')
        else:
            self.cfg['crdntl'] = self.file.load(os.environ[self.cfg['environ']['PATH2CRDNTL']], 'json')
