import sys
import os
import shutil
import time
import datetime
import logging
from subprocess import call
from ruamel.yaml import YAML
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import collections
from pathlib import Path

############################################################
 # config functions

program_dir = os.path.dirname(__file__)
config_path = os.path.join(program_dir, 'config.yaml')
watch = {}
files = {}
types = {}
logdict = {}
directory = ''

def read_config():
    yaml = YAML()
    global config_path, watch, files, types, logdict
    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        try:
            watch = cfg['watch']
            files = cfg['files']
            types = cfg['types']
            logdict = cfg['log']
        except:
            print("No Configuration Data")

def save_config():
    yaml = YAML()
    global config_path, watch, files, types, logdict
    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    cfg['watch'] = watch
    cfg['files'] = files
    cfg['types'] = types
    cfg['log'] = logdict
    with open(config_path, 'w') as ymlfile:
        yaml.dump(cfg, ymlfile)
    read_config()

def add_value_files(key, value):
    global files
    add = {key: value}
    files.update(add)
    save_config()

def add_value_types(key, value):
    global types
    add = {key: value}
    types.update(add)
    save_config()

def change_value_watch(value):
    global watch
    key = 'folder'
    add = {key: value}
    watch.update(add)
    save_config()

def add_value_logfile(value):
    global logdict
    add = {'file': value}
    logdict.update(add)
    save_config()

############################################################
#  file system functions

def move_file(src, dst):
    shutil.move(src, dst)

def delete_file(src):
    os.remove(src)

def remame_file(src, newname):
    os.rename(src, newname)

def check_directories():
    global types
    for value in types.values():
        if os.path.isdir(value) == True:
            continue
        else:
            os.makedirs(value)

############################################################
# Directory watcher and Handler

class Watcher():

    def __init__(self):
        self.observer = Observer()

    def run(self):
        global directory
        event_handler = Handler()
        self.observer.schedule(event_handler, directory, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Tidy.py Stopped")
        self.observer.join()

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        global files, types, logdict
        log = str(logdict['file'])+'/tidypy.log'
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            file = event.src_path
            ext = os.path.splitext(file)[1][1:]
            if os.path.exists(log) == True:
                pass
            else:
                open(log, 'w').close()
            if ext in files:
                folder = files.get(ext)
                location = types.get(folder)
                shutil.move(file, location)
                logappend = open(log, "a+")
                time = datetime.datetime.now()
                logappend.write(f"{time} -- File {file} - moved to {location}\n")
                logappend.close()

# moves files already in watched folder at program start
def cleaner():
    global files, types, directory
    log = str(logdict['file'])+'/tidypy.log'
    if os.path.exists(log) == True:
        pass
    else:
        open(log, 'w').close()
    for ext in files.keys():
        listdir = sorted(Path(directory).glob(f'*.{ext}'))
        if not listdir:
            pass
        else:
            for file in listdir:
                folder = files.get(ext)
                location = types.get(folder)
                file = os.fspath(file)
                shutil.move(file, location)
                logappend = open(log, "a+")
                time = datetime.datetime.now()
                logappend.write(f"{time} -- CLEANER --  File {file} - moved to {location}\n")
                logappend.close()


if len(sys.argv[1:]) == 0:
    # if no arguments run main program
    if __name__ == '__main__':
        read_config()
        directory = watch["folder"]
        check_directories()
        cleaner()
        w = Watcher()
        w.run()
else:
    # python tidy.py -a (extension type) (type in types dictionary - if not ask user for directory for these files to be saved in)
    read_config()
    arguments = sys.argv[1:]
    try:
        if arguments[0] == '-a' or arguments[0] == '--add':
            ext = str(arguments[1])
            extlist = list(ext)
            if extlist[0] == '.':
                ext = ''.join(extlist[1:])
            type = str(arguments[2])
            if ext in files.keys():
                print("Configuration already found for this extension, would you like to overwrite? ")
                if input('y/n: ') == 'n':
                    raise StopIteration
                else:
                    pass
            if type in types.keys():
                pass
            else:
                value = input("Configuration for this filetype not found, where should these be moved?  ")
                add_value_types(type, value)
                print("New type/folder pair added to configuration")
            add_value_files(ext, type)
            check_directories()
            print(f"Extension {ext} - {type} added to configuration")
        if arguments[0] == '-l' or arguments[0] == '--log':
            newlogfile = arguments[1]
            add_value_logfile(newlogfile)
        if arguments[0] == '-h' or arguments[0] == '--help' or arguments[0] == 'help':
            help = open((str(program_dir) + 'helpfile'), 'r')
            print(help.read())
    except StopIteration: pass
