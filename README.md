# ***tidy***

***Simple downloads organiser*** - written in python with easy yaml configuration. 

requires: ruamel.yaml, watchdog, pathlib and click python modules.

> pip install ruamel.yaml watchdog pathlib click

Running tidy.py:

edit ***config.yaml*** with the folder you want watched and destination folder for your files.

> git clone https://github.com/brazenwinter/tidy.py.git
>
> cd tidy.py
>
> python tidy.py run

runs the program in watcher mode.

tidy.py supports command-line arguments, for details use:

> python tidy.py --help
>
>Usage: tidy.py [OPTIONS] COMMAND [ARGS]...
>
>Options:
>  --help  Show this message and exit.
>
>Commands:
>
>  add     example: tidy add txt documents - Extension to add to...
>
>  config  example: tidy config - Prints configuration to console
>
>  log     example: tidy log /home/user - Change log file directory
>
>  remove  example: tidy remove txt - Removes extension from configuration
>
>  run     example: tidy run - Runs the program
>
>  watch   example: tidy watch /home/user/Downloads - Change watched...

***Todo***

[x] Create an option for easy recursive scanning

[] add ability to organise files by date

[] create simple gui for control (pyqt?)

