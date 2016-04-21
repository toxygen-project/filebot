from settings import Settings
from bot import Bot
from toxcore_enums_and_consts import *
from tox import bin_to_string


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - current user
# -----------------------------------------------------------------------------------------------------------------


def self_connection_status():
    """
    Current user changed connection status (offline, UDP, TCP)
    """
    def wrapped(tox, connection, user_data):
        print 'Connection status: ', str(connection)
    return wrapped


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - friends
# -----------------------------------------------------------------------------------------------------------------


def friend_connection_status(tox, friend_num, new_status, user_data):
    """
    Check friend's connection status (offline, udp, tcp)
    """
    print "Friend #{} connected! Friend's status: {}".format(friend_num, new_status)


def friend_message():
    """
    New message from friend
    """
    def wrapped(tox, friend_number, message_type, message, size, user_data):
        print message.decode('utf-8')
        Bot.get_instance().new_message(friend_number, message.decode('utf-8'))
        # parse message
    return wrapped


def friend_request(tox, public_key, message, message_size, user_data):
    """
    Called when user get new friend request
    """
    profile = Bot.get_instance()
    tox_id = bin_to_string(public_key, TOX_PUBLIC_KEY_SIZE)
    profile.process_friend_request(tox_id, message.decode('utf-8'))

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - file transfers
# -----------------------------------------------------------------------------------------------------------------


def tox_file_recv(tox_link):
    """
    New incoming file
    """
    def wrapped(tox, friend_number, file_number, file_type, size, file_name, file_name_size, user_data):
        profile = Bot.get_instance()
        if file_type == TOX_FILE_KIND['DATA']:
            print 'file'
            file_name = unicode(file_name[:file_name_size].decode('utf-8'))
            profile.incoming_file_transfer(friend_number, file_number, size, file_name)
        else:  # AVATAR
            tox_link.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])
    return wrapped


def file_recv_chunk(tox, friend_number, file_number, position, chunk, length, user_data):
    """
    Incoming chunk
    """
    Bot.get_instance().incoming_chunk(
                          friend_number,
                          file_number,
                          position,
                          chunk[:length] if length else None)


def file_chunk_request(tox, friend_number, file_number, position, size, user_data):
    """
    Outgoing chunk
    """
    Bot.get_instance().outgoing_chunk(
                          friend_number,
                          file_number,
                          position,
                          size)


def file_recv_control(tox, friend_number, file_number, file_control, user_data):
    """
    Friend cancelled, paused or resumed file transfer
    """
    if file_control == TOX_FILE_CONTROL['CANCEL']:
        Bot.get_instance().cancel_transfer(friend_number, file_number, True)

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - initialization
# -----------------------------------------------------------------------------------------------------------------


def init_callbacks(tox):
    """
    Initialization of all callbacks.
    :param tox: tox instance
    """
    tox.callback_self_connection_status(self_connection_status(), 0)

    tox.callback_friend_message(friend_message(), 0)
    tox.callback_friend_connection_status(friend_connection_status, 0)
    tox.callback_friend_request(friend_request, 0)

    tox.callback_file_recv(tox_file_recv(tox), 0)
    tox.callback_file_recv_chunk(file_recv_chunk, 0)
    tox.callback_file_chunk_request(file_chunk_request, 0)
    tox.callback_file_recv_control(file_recv_control, 0)
