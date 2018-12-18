#!/usr/bin/env python
from __future__ import print_function

"""
Utility script to manage messages in Django
(c) 2016 Mario Orlandi, Brainstorm S.n.c.
"""

__author__    = "Mario Orlandi"
__version__   = "1.2.0"
__copyright__ = "Copyright (c) 2016-2018, Brainstorm S.n.c."
__license__   = "GPL"

import os
import argparse
import importlib
try:
    import configparser
except:
    from six.moves import configparser

DRY_RUN = False


def run_command(command):
    if DRY_RUN:
        print("\x1b[1;37;40m# " + command + "\x1b[0m")
    else:
        print("\x1b[1;37;40m" + command + "\x1b[0m")
        rc = os.system(command)
        if rc != 0:
            raise Exception(command)


def assure_path_exists(path):
    if not os.path.exists(path):
        if DRY_RUN:
            print("\x1b[1;37;40m# os.makedirs(" + path + ")\x1b[0m")
        else:
            print("\x1b[1;37;40m os.makedirs(" + path + ")\x1b[0m")
            os.makedirs(path)

def fail(message):
    print('ERROR: ' + message)
    exit(-1)


def read_config_file():
    """
    Parse the config file if exists;
    otherwise, create a default config file and exit
    """

    def create_default_config_file(config_filename):

        default_config = """
[general]
project={project}
settings_module={project}.settings
translations_target_folder=./translations
apps=app1, app2
"""
        cwd = os.getcwd()
        project = os.path.split(cwd)[-1]
        text = default_config.format(
            project=project,
        )
        with open(config_filename, 'w') as configfile:
            configfile.write(text)

    config_filename = './%s%sconf' % (os.path.splitext(os.path.basename(__file__))[0], os.path.extsep)
    config = configparser.ConfigParser()
    success = len(config.read(config_filename)) > 0
    if success:
        print('Using config file "%s"' % config_filename)
    else:
        # if not found, create a default config file and re-read it
        print('Creating default config file "%s" ...' % config_filename)
        create_default_config_file(config_filename)
        print('Default config file "%s" has been created; please check it before running this script again' % config_filename)
        exit(-1)

    return config


def list_available_languages(settings_module):
    # Given:
    #
    #   LANGUAGE_CODE = 'en-us'
    #   LANGUAGES = [
    #       ('en', 'English'),
    #       ('it', 'Italiano'),
    #       ('es', 'Spanish'),
    #   ]
    #
    # Then:
    #
    #   ['it', 'es', ]

    settings = importlib.import_module(settings_module)
    language_code = settings.LANGUAGE_CODE
    if '-' in language_code:
        language_code = language_code[:language_code.find('-')]
    languages = [item[0] for item in settings.LANGUAGES if item[0] != language_code]
    return languages


def do_makemessages(apps, languages):

    base_path = os.path.dirname(os.path.abspath(__file__))
    for app in apps:

        # es: "mkdir app/locale/it" ...
        for language in languages:
            assure_path_exists(os.path.join(app, 'locale', language))

        # es: "cd app; python BASE_PATH/manage.py makemessages -a -l it -l es -l de"
        command = "cd %s; python %s makemessages %s" % (
            app,
            os.path.join(base_path, "manage.py"),
            ' '.join(['-l %s' % language for language in languages]),
        )
        run_command(command)


def do_compilemessages(apps, languages):

    base_path = os.path.dirname(os.path.abspath(__file__))
    for app in apps:

        # es: "cd app; python BASE_PATH/manage.py compilemessages"
        command = "cd %s; python %s compilemessages %s" % (
            app,
            os.path.join(base_path, "manage.py"),
            ' '.join(['-l %s' % language for language in languages]),
        )
        run_command(command)


def do_collectmessages(apps, languages, target_folder):

    base_path = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isdir(target_folder):
        raise Exception('Folder "%s" not found' % target_folder)

    print('Collecting translation files ...')
    for language in languages:

        print('Language: %s' % language)

        for app in apps:

            #
            # Collect po file as follows:
            #     MYAPP/locale/LANGUAGE/LC_MESSAGES/django.po --> ./translations/LANGUAGE/LANGUAGE_MYAPP.po
            #
            # in order to:
            #   1) remember both source language and app name in "django.po" copy
            #   2) collect all copies in a specific language folder under "translations"
            #
            # If app is kept in a subfolder, replace each "/" with "~" to obtain a flat filename:
            #     FOLDER/MYAPP/locale/LANGUAGE/LC_MESSAGES/django.po --> ./translations/LANGUAGE/LANGUAGE_FOLDER~MYAPP.po
            #

            assure_path_exists(os.path.join(target_folder, language))
            source_path = os.path.join(base_path, app, "locale", language, "LC_MESSAGES", "django.po")
            target_file = "%s_%s.po" % (language, app.replace('/', '~'))
            target_path = os.path.join(target_folder, language, target_file)

            if os.path.isfile(source_path):
                try:
                    #copyfile(source_path, target_path)
                    command = "cp %s %s" % (source_path, target_path)
                    run_command(command)
                    message = "[ok]"
                except:
                    message = "[NOT FOUND]"
            else:
                message = "[NOT FOUND]"
            print('    %-12.12s %s' % (message, target_path))


def do_installmessages(apps, languages, source_folder):

    def find_candidate(base_folder, candidates, extension):
        for candidate in candidates:
            filename = os.path.join(base_folder, candidate + '.' + extension)
            if os.path.isfile(filename):
                return filename
        return ''

    base_path = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isdir(source_folder):
        raise Exception('Folder "%s" not found' % source_folder)

    print('Installing translation files ...')
    for language in languages:

        print('Language: %s' % language)

        for app in apps:

            #
            # Do the reverse of "collect" command; that is:
            #
            #   1) search source file in "translations" folder, accepting either:
            #       - 'translations/LANGUAGE/LANGUAGE_MYAPP.po',
            #       - 'translations/LANGUAGE/MYAPP.po',
            #       - 'translations/LANGUAGE_MYAPP.po'
            #
            #   2) copy source file onto:
            #       - 'MYAPP/locale/LANGUAGE/LC_MESSAGES/django.po'
            #
            #   3) also, eventually remove the obsolete compiled translation file
            #       - 'MYAPP/locale/LANGUAGE/LC_MESSAGES/django.mo'
            #
            # Note that when the app is kept in a subfoder, we'll need to replace
            # "~" in source filename back to "/"
            #

            candidates = [
                os.path.join(language, language + '_' + app.replace('/', '~')),
                os.path.join(language, app.replace('/', '~')),
                language + '_' + app.replace('/', '~'),
            ]

            source_path = find_candidate(source_folder, candidates, 'po')
            if source_path:
                path = os.path.join(base_path, app, "locale", language, "LC_MESSAGES", "django")
                target_path_po = path + '.po'
                target_path_mo = path + '.mo'
                try:
                    #copyfile(source_path, target_path_po)
                    run_command("cp %s %s" % (source_path, target_path_po))
                    message = "[ok]"
                    if os.path.isfile(target_path_mo):
                        run_command("rm %s" % target_path_mo)
                except:
                    message = "[ERROR]"
                print('    %-12.12s %s --> %s' % (message, source_path, target_path_po))


def main():

    global DRY_RUN

    # Read config file
    config = read_config_file()
    project = config.get('general', 'project').strip()
    available_apps = config.get('general', 'apps').split(', ')
    available_languages = list_available_languages(config.get('general', 'settings_module').strip())

    # Parse command line
    parser = argparse.ArgumentParser()
    parser.epilog = 'Available apps: ' + ', '.join(available_apps) + '; ' + \
                    'Available languages: ' + ', '.join(available_languages)
    command_choices = ['make', 'compile', 'collect', 'install', ]

    parser.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2, 3], default=2, help="Verbosity level. (default: 2)")
    parser.add_argument('-d', '--dry-run', action='store_true', default=False, help="Don't execute commands, just pretend. (default: False)")
    parser.add_argument('command', metavar='command', choices=command_choices, help='|'.join(command_choices))
    parser.add_argument('-a', '--apps', nargs='*', required=False)
    parser.add_argument('-l', '--languages', nargs='*', required=False)
    parsed = parser.parse_args()
    #print('Result:',  vars(parsed))

    command = parsed.command
    translations_target_folder = config.get('general', 'translations_target_folder').strip()
    if parsed.dry_run:
        DRY_RUN = True

    # Load app list from "apps" option
    apps = []
    if parsed.apps is None:
        print('Specify one or more apps (-a option), or "all"')
        return -1
    for app in parsed.apps:
        if app == "all":
            apps += available_apps
        elif app in available_apps:
            apps.append(app)
        else:
            raise Exception('Unknown app "%s"' % app)

    # Remove duplicates
    apps = list(set(apps))

    # Load language list from "languages" option
    languages = []
    if parsed.languages is None:
        print('Specify one or more language (-l option), or "all"')
        return -1
    for language in parsed.languages:
        if language == "all":
            languages += available_languages
        elif language in available_languages:
            languages.append(language)
        else:
            raise Exception('Unknown language "%s"' % language)

    # Remove duplicates
    languages = list(set(languages))

    print('command: ' + command)
    print('languages: ' + ', '.join(languages))
    print('apps: ' + ', '.join(apps))


    # Execute command
    if command == 'make':
        do_makemessages(apps, languages)
    elif command == 'compile':
        do_compilemessages(apps, languages)
    elif command == 'collect':
        do_collectmessages(apps, languages, translations_target_folder)
    elif command == 'install':
        do_installmessages(apps, languages, translations_target_folder)
    else:
        fail('Unknown command "%s"' % command)

    print('done.')


if __name__ == "__main__":
    main()
