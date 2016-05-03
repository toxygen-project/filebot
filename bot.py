from tox import Tox
import os
from settings import *
from toxcore_enums_and_consts import *
from ctypes import *
from util import Singleton
from file_transfers import *
from collections import defaultdict


class Bot(Singleton):

    def __init__(self, tox):
        """
        :param tox: tox instance
        """
        super(Bot, self).__init__()
        self._tox = tox
        self._file_transfers = {}  # dict of file transfers. key - tuple (friend_number, file_number)
        self._downloads = defaultdict(int)  # defaultdict of downloads count

    # -----------------------------------------------------------------------------------------------------------------
    # Edit current user's data
    # -----------------------------------------------------------------------------------------------------------------

    def set_name(self, value):
        self._tox.self_set_name(value.encode('utf-8'))

    def set_status_message(self, value):
        self._tox.self_set_status_message(value.encode('utf-8'))

    # -----------------------------------------------------------------------------------------------------------------
    # Private messages
    # -----------------------------------------------------------------------------------------------------------------

    def send_message(self, number, message, message_type=TOX_MESSAGE_TYPE['NORMAL']):
        """
        Send message with message splitting
        :param number: friend's number
        :param message: message text
        :param message_type: type of message
        """
        while len(message) > TOX_MAX_MESSAGE_LENGTH:
            size = TOX_MAX_MESSAGE_LENGTH * 4 / 5
            last_part = message[size:TOX_MAX_MESSAGE_LENGTH]
            if ' ' in last_part:
                index = last_part.index(' ')
            elif ',' in last_part:
                index = last_part.index(',')
            elif '.' in last_part:
                index = last_part.index('.')
            else:
                index = TOX_MAX_MESSAGE_LENGTH - size - 1
            index += size + 1
            self._tox.friend_send_message(number, message_type, message[:index])
            message = message[index:]
        self._tox.friend_send_message(number, message_type, message)

    def new_message(self, friend_num, message):
        """
        New message
        :param friend_num: number of friend who sent message
        :param message: text of message
        """
        id = self._tox.friend_get_public_key(friend_num)  # public key of user
        settings = Settings.get_instance()
        message = message.strip()
        # message parsing
        if message == 'files':  # get file list
            if id in settings['read']:
                s = ''
                for f in os.listdir(settings['folder']):
                    f = unicode(f)
                    if os.path.isfile(os.path.join(settings['folder'], f)):
                        s += u'{} ({} bytes)\n'.format(f, os.path.getsize(os.path.join(settings['folder'], f)))
                if not s:
                    s = 'Nothing found'
                self.send_message(friend_num, s.encode('utf-8'), TOX_MESSAGE_TYPE['NORMAL'])
            else:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
        elif message.startswith('get '):  # download file or all files
            if id in settings['read']:
                if '--all' not in message:
                    path = settings['folder'] + '/' + unicode(message[4:])
                    if os.path.exists(unicode(path)):
                        self.send_file(unicode(path), friend_num)
                    else:
                        self.send_message(friend_num, 'Wrong file name'.encode('utf-8'))
                else:
                    for f in os.listdir(settings['folder']):
                        if os.path.isfile(os.path.join(settings['folder'], f)):
                            self.send_file(unicode(os.path.join(settings['folder'], f)), friend_num)
            else:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
        elif message == 'help':  # help
            self.send_message(friend_num, """
            help - list of commands\n
            rights - get access rights\n
            files - show list of files (get access)\n
            id - get bot's id (get access)\n
            share <ToxID> <file_name> - send file to friend (get access)\n
            share --all <file_name> - send file to all friends (get access)\n
            size <file_name> - get size of file (get access)\n
            get <file_name> - get file with specified filename (get access)\n
            get --all - get all files (get access)\n
            stats - show statistics (write access)\n
            del <file_name> - remove file with specified filename (delete access)\n
            rename <file_name> --new <new_file_name> - rename file (delete access)\n
            user <ToxID> <rights> - new rights (example: rwdm) for user (masters only)\n
            status <new_status> - new status message (masters only)\n
            name <new_name> - new name (masters only)\n
            message <ToxID> <message_text> - send message to friend (masters only)\n
            message --all <message_text> - send message to all friends (masters only)\n
            stop - stop bot (masters only)\n
            Users with write access can send files to bot.
            """.encode('utf-8'))
        elif message == 'rights':  # get rights
            self.send_message(friend_num, 'Read: {}\nWrite: {}\nDelete: {}\nMaster: {}'
                              .format('Yes' if id in settings['read'] else 'No, sorry',
                                      'Yes' if id in settings['write'] else 'No',
                                      'Yes' if id in settings['delete'] else 'No',
                                      'Yes, sir!' if id in settings['master'] else 'No'))
        elif message.startswith('del '):  # delete file
            if id in settings['delete']:
                path = settings['folder'] + '/' + message[4:]
                if os.path.exists(path):
                    os.remove(path)
                    self.send_message(friend_num, 'File was successfully deleted')
                else:
                    self.send_message(friend_num, 'Wrong file name'.encode('utf-8'))
            else:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
        elif message.startswith('user '):  # new rights for user
            if id not in settings['master']:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
                return
            try:
                rights = message.split(' ')[2]
            except:
                rights = ''
            id = message.split(' ')[1][:TOX_PUBLIC_KEY_SIZE * 2]
            if id in settings['read']:
                settings['read'].remove(id)
            if id in settings['write']:
                settings['write'].remove(id)
            if id in settings['delete']:
                settings['delete'].remove(id)

            if 'r' in rights:
                settings['read'].append(id)
            if 'w' in rights:
                settings['write'].append(id)
            if 'd' in rights:
                settings['delete'].append(id)
            if 'm' in rights:
                settings['master'].append(id)
            settings.save()
            self.send_message(friend_num, 'Updated'.encode('utf-8'))

        elif message.startswith('status '):  # new status
            if id not in settings['master']:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
            else:
                self.set_status_message(message[7:])
        elif message.startswith('name '):  # new name
            if id not in settings['master']:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
            else:
                self.set_name(message[5:])
        elif message.startswith('share '):  # send file to friend (all friends)
            if id in settings['read']:
                if '--all' not in message:
                    fl = ' '.join(message.split(' ')[2:])
                    try:
                        num = self._tox.friend_by_public_key(message.split(' ')[1][:TOX_PUBLIC_KEY_SIZE * 2])
                        print num
                        self.send_file(settings['folder'] + '/' + fl, num)
                    except Exception as ex:
                        print ex
                        self.send_message(friend_num, 'Friend not found'.encode('utf-8'))
                else:
                    fl = ' '.join(message.split(' ')[2:])
                    for num in self._tox.self_get_friend_list():
                        if self._tox.friend_get_connection_status(num):
                            self.send_file(settings['folder'] + '/' + fl, num)
            else:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
        elif message.startswith('rename '):  # rename existing file
            ind = message.index(' --new ')
            old = message[7:ind]
            new = message[ind + 7:]
            if id in settings['delete']:
                if os.path.exists(settings['folder'] + '/' + old):
                    os.rename(settings['folder'] + '/' + old, settings['folder'] + '/' + new)
                    self.send_message(friend_num, 'Renamed'.encode('utf-8'))
                else:
                    self.send_message(friend_num, 'File not found'.encode('utf-8'))
            else:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
        elif message == 'id':  # get TOX ID
            if id in settings['read']:
                tox_id = self._tox.self_get_address()
                self.send_message(friend_num, tox_id.encode('utf-8'))
            else:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
        elif message.startswith('size '):  # get file size
            path = unicode(settings['folder'] + '/' + message[5:])
            if id not in settings['read']:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
            elif not os.path.exists(path):
                self.send_message(friend_num, 'File not found'.encode('utf-8'))
            else:
                bytes_size = os.path.getsize(path)
                if bytes_size < 1024:
                    size = u'{} B'.format(bytes_size)
                elif bytes_size < 1024 * 1024:
                    size = u'{} KB'.format(bytes_size / 1024)
                else:
                    size = u'{} MB'.format(bytes_size / 1024 * 1024)
                s = u'Size: {} ({} bytes)'.format(size, bytes_size)
                self.send_message(friend_num, s.encode('utf-8'))
        elif message.startswith('message '):  # send message to friend (all friends)
            if id not in settings['master']:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
            elif '--all' not in message:
                tox_id = message.split(' ')[1][:TOX_PUBLIC_KEY_SIZE * 2]
                s = ' '.join(message.split(' ')[2:])
                num = self._tox.friend_by_public_key(tox_id)
                try:
                    self.send_message(num, s.encode('utf-8'))
                except:
                    self.send_message(friend_num, 'Friend is not online'.encode('utf-8'))
            else:
                s = ' '.join(message.split(' ')[2:])
                for num in self._tox.self_get_friend_list():
                    if self._tox.friend_get_connection_status(num):
                        self.send_message(num, s.encode('utf-8'))
        elif message == 'stats':  # get stats
            if id not in settings['write']:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
            else:
                s = ''
                for f in os.listdir(settings['folder']):
                    f = unicode(f)
                    if os.path.isfile(os.path.join(settings['folder'], f)):
                        s += u'{} ({} downloads)\n'.format(f,
                                                           self._downloads[os.path.join(settings['folder'], f)])
                if not s:
                    s = 'Nothing found'
                else:
                    s += u'Downloads count: {}'.format(sum(self._downloads.values()))
                count = 0
                for num in self._tox.self_get_friend_list():
                    if self._tox.friend_get_connection_status(num):
                        count += 1
                s = 'Friends: {}\nOnline friends: {}\nFiles:\n'.format(self._tox.self_get_friend_list_size(), count) + s
                self.send_message(friend_num, s.encode('utf-8'), TOX_MESSAGE_TYPE['NORMAL'])
        elif message == 'stop':  # stop bot
            if id in settings['master']:
                settings.save()
                data = self._tox.get_savedata()
                ProfileHelper.save_profile(data)
                del self._tox
                raise SystemExit()
            else:
                self.send_message(friend_num, 'Not enough rights'.encode('utf-8'))
        else:
            self.send_message(friend_num, 'Wrong command'.encode('utf-8'))

    # -----------------------------------------------------------------------------------------------------------------
    # Friend requests
    # -----------------------------------------------------------------------------------------------------------------

    def process_friend_request(self, tox_id, message):
        """
        Accept or ignore friend request
        :param tox_id: tox id of contact
        :param message: message
        """
        print 'Friend request:', message
        self._tox.friend_add_norequest(tox_id)
        settings = Settings.get_instance()
        # give friend default rights
        if 'r' in settings['auto_rights'] and tox_id not in settings['read']:
            settings['read'].append(tox_id)
        if 'w' in settings['auto_rights'] and tox_id not in settings['write']:
            settings['write'].append(tox_id)
        if 'd' in settings['auto_rights'] and tox_id not in settings['delete']:
            settings['delete'].append(tox_id)
        if 'm' in settings['auto_rights'] and tox_id not in settings['master']:
            settings['master'].append(tox_id)
        settings.save()
        data = self._tox.get_savedata()
        ProfileHelper.save_profile(data)

    # -----------------------------------------------------------------------------------------------------------------
    # File transfers support
    # -----------------------------------------------------------------------------------------------------------------

    def incoming_file_transfer(self, friend_number, file_number, size, file_name):
        """
        New transfer
        :param friend_number: number of friend who sent file
        :param file_number: file number
        :param size: file size in bytes
        :param file_name: file name without path
        """
        id = self._tox.friend_get_public_key(friend_number)
        settings = Settings.get_instance()
        if id in settings['write']:
            path = settings['folder']
            new_file_name, i = file_name, 1
            while os.path.isfile(path + '/' + new_file_name):  # file with same name already exists
                if '.' in file_name:  # has extension
                    d = file_name.rindex('.')
                else:  # no extension
                    d = len(file_name)
                new_file_name = file_name[:d] + ' ({})'.format(i) + file_name[d:]
                i += 1
            self.accept_transfer(path + '/' + new_file_name, friend_number, file_number, size)
        else:
            self.cancel_transfer(friend_number, file_number, False)

    def cancel_transfer(self, friend_number, file_number, already_cancelled=False):
        """
        Stop transfer
        :param friend_number: number of friend
        :param file_number: file number
        :param already_cancelled: was cancelled by friend
        """
        if (friend_number, file_number) in self._file_transfers:
            tr = self._file_transfers[(friend_number, file_number)]
            if not already_cancelled:
                tr.cancel()
            else:
                tr.cancelled()
            del self._file_transfers[(friend_number, file_number)]
        else:
            self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])

    def accept_transfer(self, path, friend_number, file_number, size):
        """
        :param path: path for saving
        :param friend_number: friend number
        :param file_number: file number
        :param size: file size
        """
        rt = ReceiveTransfer(path, self._tox, friend_number, size, file_number)
        self._file_transfers[(friend_number, file_number)] = rt
        self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['RESUME'])

    def send_file(self, path, friend_number):
        """
        Send file to current active friend
        :param path: file path
        :param friend_number: friend_number
        """
        self._downloads[path] += 1
        st = SendTransfer(path, self._tox, friend_number)
        self._file_transfers[(friend_number, st.get_file_number())] = st

    def incoming_chunk(self, friend_number, file_number, position, data):
        if (friend_number, file_number) in self._file_transfers:
            transfer = self._file_transfers[(friend_number, file_number)]
            transfer.write_chunk(position, data)
            if transfer.state:
                del self._file_transfers[(friend_number, file_number)]

    def outgoing_chunk(self, friend_number, file_number, position, size):
        if (friend_number, file_number) in self._file_transfers:
            transfer = self._file_transfers[(friend_number, file_number)]
            transfer.send_chunk(position, size)
            if transfer.state:
                del self._file_transfers[(friend_number, file_number)]


def tox_factory(data=None, settings=None):
    """
    :param data: user data from .tox file. None = no saved data, create new profile
    :param settings: current profile settings. None = default settings will be used
    :return: new tox instance
    """
    if settings is None:
        settings = {
            'ipv6_enabled': True,
            'udp_enabled': True,
            'proxy_type': 0,
            'proxy_host': '0',
            'proxy_port': 0,
            'start_port': 0,
            'end_port': 0,
            'tcp_port': 0
        }
    tox_options = Tox.options_new()
    tox_options.contents.udp_enabled = settings['udp_enabled']
    tox_options.contents.proxy_type = settings['proxy_type']
    tox_options.contents.proxy_host = settings['proxy_host']
    tox_options.contents.proxy_port = settings['proxy_port']
    tox_options.contents.start_port = settings['start_port']
    tox_options.contents.end_port = settings['end_port']
    tox_options.contents.tcp_port = settings['tcp_port']
    if data:  # load existing profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['TOX_SAVE']
        tox_options.contents.savedata_data = c_char_p(data)
        tox_options.contents.savedata_length = len(data)
    else:  # create new profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['NONE']
        tox_options.contents.savedata_data = None
        tox_options.contents.savedata_length = 0
    return Tox(tox_options)
