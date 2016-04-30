###File bot
A bot which allows you to easily share files with friends and family using [Tox](https://tox.chat/)

Based on [toxygen](https://github.com/xveduk/toxygen/) toxcore wrapper


# Supported OS:
- Windows
- Linux

#Install:

### Windows

1. [Download and install latest Python 2.7](https://www.python.org/downloads/windows/)
2. [Download file bot](https://github.com/ingvar1995/filebot/archive/master.zip)
3. Unpack archive
4. Download latest libtox.dll build, download latest libsodium.a build, put it into \libs\
5. Run app:
``python main.py path_to_profile``

[libtox.dll for 32-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86_shared_release.zip)

[libtox.dll for 64-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86-64_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86-64_shared_release.zip)

[libsodium.a for 32-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86_static_release.zip)

[libsodium.a for 64-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86-64_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86-64_static_release.zip)


### Linux

1. Install Python2.7: ``sudo apt-get install python2.7``
2. [Download file bot](https://github.com/ingvar1995/filebot/archive/master.zip)
3. Unpack archive 
4. Install [toxcore](https://github.com/irungentoo/toxcore/blob/master/INSTALL.md) in your system
5. Run app:
``python main.py path_to_profile``

#Commands:
help - list of commands

rights - get access rights

files - show list of files (get access)

id - get bot's id (get access)

share <ToxID> <file_name> - send file to friend (get access)

share --all <file_name> - send file to all friends (get access)

size <file_name> - get size of file (get access)

get <file_name> - get file with specified filename (get access)

get --all - get all files (get access)

stats - show statistics (write access)

del <file_name> - remove file with specified filename (delete access)

rename <file_name> --new <new_file_name> - rename file (delete access)

user <ToxID> <rights> - new rights (example: rwdm) for user (masters only)

status <new_status> - new status message (masters only)

name <new_name> - new name (masters only)

message <ToxID> <message_text> - send message to friend (masters only)

message --all <message_text> - send message to all friends (masters only)

stop - stop bot (masters only)


Users with write access can send files to bot.
