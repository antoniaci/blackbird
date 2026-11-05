import os


def isFile(fileName):
    return os.path.isfile(fileName)


def getLinesFromFile(fileName):
    try:
        # utf-8-sig strips the BOM that Windows editors such as Notepad prepend,
        # which would otherwise become part of the first username.
        with open(fileName, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
            return lines
    except:
        return False
