Sample usage:

    Using config file "./messages.conf"
    usage: messages.py [-h] [-v {0,1,2,3}] [-f] [-d] [-a [APPS ...]] [-l [LANGUAGES ...]] command

    positional arguments:
      command               make|compile|collect|install|auto_translate

    options:
      -h, --help            show this help message and exit
      -v {0,1,2,3}, --verbosity {0,1,2,3}
                            Verbosity level. (default: 2)
      -f, --fuzzy           Set fuzzy flag for new translations (only for auto_translate command)
      -d, --dry-run         Don't execute commands, just pretend. (default: False)
      -a [APPS ...], --apps [APPS ...]
      -l [LANGUAGES ...], --languages [LANGUAGES ...]

    Available apps: main, frontend; Available languages: it, es
