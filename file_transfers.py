from toxcore_enums_and_consts import TOX_FILE_KIND, TOX_FILE_CONTROL
from os.path import basename, getsize
from os import remove
from time import time
from tox import Tox


TOX_FILE_TRANSFER_STATE = {
    'RUNNING': 0,
    'PAUSED': 1,
    'CANCELED': 2,
    'FINISHED': 3,
}


class FileTransfer(object):
    """
    Superclass for file transfers
    """

    def __init__(self, path, tox, friend_number, size, file_number=None):
        self._path = path
        self._tox = tox
        self._friend_number = friend_number
        self.state = TOX_FILE_TRANSFER_STATE['RUNNING']
        self._file_number = file_number
        self._creation_time = time()
        self._size = size
        self._done = 0

    def set_tox(self, tox):
        self._tox = tox

    def get_file_number(self):
        return self._file_number

    def get_friend_number(self):
        return self._friend_number

    def cancel(self):
        self.send_control(TOX_FILE_CONTROL['CANCEL'])
        if hasattr(self, '_file'):
            self._file.close()

    def cancelled(self):
        if hasattr(self, '_file'):
            self._file.close()

    def send_control(self, control):
        if self._tox.file_control(self._friend_number, self._file_number, control):
            self.state = control

    def get_file_id(self):
        return self._tox.file_get_file_id(self._friend_number, self._file_number)

# -----------------------------------------------------------------------------------------------------------------
# Send file
# -----------------------------------------------------------------------------------------------------------------


class SendTransfer(FileTransfer):

    def __init__(self, path, tox, friend_number, kind=TOX_FILE_KIND['DATA'], file_id=None):
        if path is not None:
            self._file = open(path, 'rb')
            size = getsize(path)
        else:
            size = 0
        super(SendTransfer, self).__init__(path, tox, friend_number, size)
        self._file_number = tox.file_send(friend_number, kind, size, file_id,
                                          basename(path).encode('utf-8') if path else '')

    def send_chunk(self, position, size):
        """
        Send chunk
        :param position: start position in file
        :param size: chunk max size
        """
        if size:
            self._file.seek(position)
            data = self._file.read(size)
            self._tox.file_send_chunk(self._friend_number, self._file_number, position, data)
            self._done += size
        else:
            self._file.close()
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']

# -----------------------------------------------------------------------------------------------------------------
# Receive file
# -----------------------------------------------------------------------------------------------------------------


class ReceiveTransfer(FileTransfer):

    def __init__(self, path, tox, friend_number, size, file_number):
        super(ReceiveTransfer, self).__init__(path, tox, friend_number, size, file_number)
        self._file = open(self._path, 'wb')
        self._file.truncate(0)
        self._file_size = 0

    def cancel(self):
        super(ReceiveTransfer, self).cancel()
        remove(self._path)

    def write_chunk(self, position, data):
        """
        Incoming chunk
        :param position: position in file to save data
        :param data: raw data (string)
        """
        if data is None:
            self._file.close()
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']
        else:
            data = ''.join(chr(x) for x in data)
            if self._file_size < position:
                self._file.seek(0, 2)
                self._file.write('\0' * (position - self._file_size))
            self._file.seek(position)
            self._file.write(data)
            self._file.flush()
            l = len(data)
            if position + l > self._file_size:
                self._file_size = position + l
            self._done += l
            if self._done > self._size:
                self.cancel()
                remove(self._path)
