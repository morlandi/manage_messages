Sample usage:

    Using config file "./manage_messages.conf"
    usage: manage_messages.py [-h] [-v {0,1,2,3}] [-d] [-a [APPS [APPS ...]]]
                              [-l [LANGUAGES [LANGUAGES ...]]]
                              command

    positional arguments:
      command               make|compile|collect|install

    optional arguments:
      -h, --help            show this help message and exit
      -v {0,1,2,3}, --verbosity {0,1,2,3}
                            Verbosity level. (default: 2)
      -d, --dry-run         Don't execute commands, just pretend. (default: False)
      -a [APPS [APPS ...]], --apps [APPS [APPS ...]]
      -l [LANGUAGES [LANGUAGES ...]], --languages [LANGUAGES [LANGUAGES ...]]

    Available apps: app1, app2, ...
    Available languages: it, es, ...
