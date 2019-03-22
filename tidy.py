import os
import shutil
import time
import datetime
from ruamel.yaml import YAML
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import click

############################################################
# config functions

program_dir = os.path.dirname(__file__)
config_path = os.path.join(program_dir, 'config.yaml')
watch = {}
files = {}
types = {}
logdict = {}
recursive = {}
directory = ''


def read_config():
    """reads config.yaml and parses the content assigning
    dictionaries to the values"""
    yaml = YAML()
    global config_path, watch, files, types, logdict, recursive
    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        try:
            watch = cfg['watch']
            files = cfg['files']
            types = cfg['types']
            logdict = cfg['log']
            recursive = cfg['recursive']
        except IndexError:
            print("No Configuration Data")


def save_config():
    """saves the edited dictionaries (edited by the add_value_* definitions)
    to config.yaml to update configuration"""
    yaml = YAML()
    global config_path, watch, files, types, logdict
    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    cfg['watch'] = watch
    cfg['files'] = files
    cfg['types'] = types
    cfg['log'] = logdict
    cfg['recursive'] = recursive
    with open(config_path, 'w') as ymlfile:
        yaml.dump(cfg, ymlfile)
    read_config()


def add_value_files(key, value):
    """adds the specified key, value pair to the files dictionary"""
    global files
    add = {key: value}
    files.update(add)
    save_config()


def add_value_types(key, value):
    """adds the specified key, value pair to the types dictionary"""
    global types
    add = {key: value}
    types.update(add)
    save_config()


def add_value_watch(value):
    """adds the specified value to the watch dictionary"""
    global watch
    key = 'folder'
    add = {key: value}
    watch.update(add)
    save_config()

def change_value_recursivity(value):
    """changes the recursive dictionary to either off or on"""
    global recursive
    key = 'enabled'
    add = {key: value}
    recursive.update(add)
    save_config()


def add_value_logfile(value):
    """adds the specified key, value pair to the logdict dictionary"""
    global logdict
    add = {'file': value}
    logdict.update(add)
    save_config()


def remove_value_files(key):
    """removes the specified key and its value from the files dictionary"""
    global files
    keylist = list(key)
    if keylist[0] == '.':
        key = ''.join(keylist[1:])
    files.pop(key)
    save_config()

############################################################
#  file system functions


def check_directories(start):
    """Checks that the directories specified in the types dictionary exist
    if they dont they are created"""
    global types, recursive
    for value in types.values():
        if os.path.isdir(value):
            continue
        else:
            os.makedirs(value)
    if recursive.get('enabled') == 'on':
        subfolders = [f.path for f in os.scandir(start) if f.is_dir() ]
        for value in types.values():
            if value in subfolders:
                print("Recursive mode is on, however destination directories"
                      " are within the range of the recursive scan, Aborting!")
                raise SystemExit(0)


############################################################
# Directory watcher and Handler


class Watcher():

    def __init__(self):
        """initialises the directory watcher
        imported from the watchdog module"""
        self.observer = Observer()

    def run(self, directory):
        """sets up the handler of events, in this case a new function was
        defined to be the handler as we want to move created files, the program
        is currently non-recursive though this can be changed if the
        destiniation folders are not within thewatched folder"""
        global recursive
        event_handler = Handler()
        if recursive.get('enabled') == 'on':
            self.observer.schedule(event_handler, directory, recursive=True)
        elif recursive.get('enabled') == 'off':
            self.observer.schedule(event_handler, directory, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt or SystemExit:
            self.observer.stop()
            print("Tidy.py Stopped")
        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        """defines the activity we want to happen when a new file is created
        in the watched folder, in this case if the file extension matches one
        of the extensions in the files dictionary, it is then moved to the
        correct folder found by querying the types dictionary

        all file operations are logged by writing to a text file, location
        of which can be changed in config.yaml"""
        global files, types, logdict
        log = str(logdict['file'])+'/tidypy.log'
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            file = event.src_path
            ext = os.path.splitext(file)[1][1:]
            if not os.path.exists(log):
                open(log, 'w').close()
            if ext in files:
                folder = files.get(ext)
                location = types.get(folder)
                try:
                    shutil.move(file, location)
                    logappend = open(log, "a+")
                    time = datetime.datetime.now()
                    logappend.write(f"{time} -- DONE -- File {file} "
                                    "- moved to {location}\n")
                    logappend.close()
                except shutil.Error:
                    logappend = open(log, "a+")
                    time = datetime.datetime.now()
                    logappend.write(f"{time} -- FAILED -- File {file} "
                                    "- Cannot be moved to {location}\n")
                    logappend.close()


def cleaner(directory):
    """The watcher is only able to fire an event when a new file is created
    this functions aims to move any files currently in the watched folder
    at program start

    this function also has a logging component"""
    global files, types, recursive
    log = str(logdict['file'])+'/tidypy.log'
    if not os.path.exists(log):
        open(log, 'w').close()
    for ext in files.keys():
        if recursive.get('enabled') == 'off':
            listdir = sorted(Path(directory).glob(f'*.{ext}'))
        elif recursive.get('enabled') == 'on':
            listdir = sorted(Path(directory).glob(f'**/*.{ext}'
                                                  ))
        if listdir:
            for file in listdir:
                folder = files.get(ext)
                location = types.get(folder)
                file = os.fspath(file)
                try:
                    shutil.move(file, location)
                    logappend = open(log, "a+")
                    time = datetime.datetime.now()
                    logappend.write(f"{time} -- CLEANER --  File {file} "
                                    "- moved to {location}\n")
                    logappend.close()
                except shutil.Error:
                    logappend = open(log, "a+")
                    time = datetime.datetime.now()
                    logappend.write(f"{time} -- FAILED -- File {file} "
                                    "- Cannot be moved to {location}\n")
                    logappend.close()


############################################################
# Click functions

@click.group()
def cli():
    pass

@cli.command(help='example: tidy add txt documents '
             '- Extension to add to configuration')
@click.argument('extension')
@click.argument('type')
def add(extension, type):
    global directory
    read_config()
    extlist = list(extension)
    if extlist[0] == '.':
        extension = ''.join(extlist[1:])
    if extension in files.keys():
        print("Configuration already found for this extension,"
              " would you like to overwrite? ")
        if input('y/n: ') == 'n':
            return None
    if type not in types.keys():
        value = input("Configuration for this filetype not found, "
                      "where should these be moved?  ")
        add_value_types(type, value)
        print("New type/folder pair added to configuration")
    add_value_files(extension, type)
    check_directories(directory)
    print(f"Extension {extension} - {type} added to configuration")

@cli.command(help='example: tidy remove txt '
             '- Removes extension from configuration')
@click.argument('extension')
def remove(extension):
    read_config()
    remove_value_files(extension)

@cli.command(help='example: tidy watch /home/user/Downloads '
             '- Change watched directory')
@click.argument('watchfile')
def watch(watchfile):
    read_config()
    add_value_watch(watchfile)

@cli.command(help='example: tidy log /home/user '
             '- Change log file directory')
@click.argument('logfile')
def log(logfile):
    read_config()
    add_value_logfile(logfile)

@cli.command(help='example: tidy recursive on/off '
             '- Enable/Disable recursive scanning')
@click.argument('recursivity')
def recursive(recursivity):
    if recursivity != 'on' and recursivity != 'off':
        print("only on/off permitted")
        raise SystemExit(0)
    read_config()
    change_value_recursivity(recursivity)

@cli.command(help='example: tidy config '
             '- Prints configuration to console')
def config():
    with open(config_path, 'r') as file:
        print(file.read())

@cli.command(help='example: tidy run '
             '- Runs the program')
def run():
    read_config()
    directory = watch["folder"]
    check_directories(directory)
    cleaner(directory)
    w = Watcher()
    w.run(directory)


cli.add_command(add)
cli.add_command(remove)
cli.add_command(watch)
cli.add_command(log)
cli.add_command(recursive)
cli.add_command(config)
cli.add_command(run)

if __name__ == '__main__':
    cli()
