from bootstrap import node_generator
from bot import *
from callbacks import init_callbacks
import time
import sys


class FileBot(object):

    def __init__(self, path):
        super(FileBot, self).__init__()
        self.tox = None
        self.stop = False
        self.profile = None
        self.path = path
        print 'FileBot v0.1'

    def main(self):
        self.tox = tox_factory(ProfileHelper.open_profile(self.path))
        init_callbacks(self.tox)
        # bootstrap
        for data in node_generator():
            self.tox.bootstrap(*data)
        settings = Settings()
        self.profile = Bot(self.tox)
        print 'Iterate'
        try:
            while not self.stop:
                self.tox.iterate()
                time.sleep(self.tox.iteration_interval() / 1000.0)
        except KeyboardInterrupt:
            settings.save()
            data = self.tox.get_savedata()
            ProfileHelper.save_profile(data)
            del self.tox


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        bot = FileBot(path)
        bot.main()
    else:
        raise IOError('Path to save file not found')

