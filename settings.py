from platform import system
import json
import os
import locale
from util import Singleton, curr_directory
from toxcore_enums_and_consts import *


class Settings(Singleton, dict):

    def __init__(self):
        self.path = curr_directory() + '/settings.json'
        if os.path.isfile(self.path):
            with open(self.path) as fl:
                data = fl.read()
            super(self.__class__, self).__init__(json.loads(data))
        else:
            super(self.__class__, self).__init__(Settings.get_default_settings())
            self.save()
        self['read'] = map(lambda x: x[:TOX_PUBLIC_KEY_SIZE * 2], self['read'])
        self['write'] = map(lambda x: x[:TOX_PUBLIC_KEY_SIZE * 2], self['write'])
        self['delete'] = map(lambda x: x[:TOX_PUBLIC_KEY_SIZE * 2], self['delete'])
        self['master'] = map(lambda x: x[:TOX_PUBLIC_KEY_SIZE * 2], self['master'])

    @staticmethod
    def get_default_settings():
        return {
            'read': [],
            'write': [],
            'delete': [],
            'master': [],
            'folder': curr_directory(),
            'auto_rights': 'r'
        }

    def save(self):
        print 'Saving'
        text = json.dumps(self)
        with open(self.path, 'w') as fl:
            fl.write(text)


class ProfileHelper(object):
    """
    Class with static methods for search, load and save profiles
    """

    @staticmethod
    def open_profile(path):
        path = path.decode(locale.getpreferredencoding())
        ProfileHelper._path = path
        with open(ProfileHelper._path, 'rb') as fl:
            data = fl.read()
        if data:
            return data
        else:
            raise IOError('Save file has zero size!')

    @staticmethod
    def save_profile(data):
        with open(ProfileHelper._path, 'wb') as fl:
            fl.write(data)

