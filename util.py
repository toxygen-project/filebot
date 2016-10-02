import os


def log(data):
    with open(curr_directory() + '/logs.log', 'a') as fl:
        fl.write(str(data) + '\n')


def curr_directory():
    return os.path.dirname(os.path.realpath(__file__))


def folder_size(path):
    size = 0
    for f in os.listdir(path):
        f = unicode(f)
        if os.path.isfile(os.path.join(path, f)):
            size += os.path.getsize(os.path.join(path, f))
    return size


class Singleton(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls._instance
