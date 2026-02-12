#!/usr/bin/env python3


# Requirements:
#
# pip install polib
# pip install googletrans==4.0.0-rc1  (versione sincrona)

import os
import argparse
import polib

# https://py-googletrans.readthedocs.io/en/latest/
from googletrans import Translator


def get_language_from_filepath(filepath):
    """
    Esempio: 'backend/locale/zh_hans/LC_MESSAGES/django.po' --> 'zh_hans'
    """
    parts = filepath.split(os.sep)
    idx = parts.index("locale")
    lang = parts[idx + 1]
    assert parts[idx+2]=='LC_MESSAGES', 'missing "LC_MESSAGES" in %s' % filepath
    return lang


def main():
    # Parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pofile",
        help="path of po file to be auto translated"
    )
    parser.add_argument(
        "--source-language",
        default="en",
        help="Default: en",
    )
    parser.add_argument(
        "-f",
        "--fuzzy",
        action="store_true",
        default=False,
        help="Set fuzzy flag for new translations",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        default=False,
        help="Don't execute commands, just pretend. (default: False)",
    )
    parsed = parser.parse_args()
    #print('Result:',  vars(parsed))

    filepath = parsed.pofile

    source = parsed.source_language
    target = get_language_from_filepath(filepath)
    if target in ['zh-hans', 'zh_hans', 'zh', ]:
        target = "zh-cn"
    if target in ['zh-hant', 'zh_hant', ]:
        target = "zh-tw"

    translator = Translator()
    # Esempio:
    # translator.translate("device", src="en", dest="zh-cn").text

    po = polib.pofile(filepath)
    print("Numero di voci:", len(po))
    print("Header Project-Id-Version:", po.metadata.get("Project-Id-Version"))
    n = 0
    for entry in po:
        if not entry.msgstr:

            try:
                print('original:    "%s"' % entry.msgid)
                #if not parsed.dry_run:
                if True:
                    result = translator.translate(entry.msgid, src=source, dest=target)
                    translation = result.text
                    print('translation: "%s"' % translation)
                    entry.msgstr = translation
                    if parsed.fuzzy:
                        entry.flags.append("fuzzy")
                n += 1
            except Exception as e:
                print('ERRORE: ' + str(e))

    print('\n%d messages have been translated' % n)
    if n > 0 and not parsed.dry_run:
        print('Saving file "%s" ...' % filepath)
        po.save(filepath)

if __name__ == "__main__":
    main()
