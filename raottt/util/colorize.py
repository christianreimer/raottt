"""
Convenience functions to print colored output to terminal.
"""

# Don't want complaints about the me() function
# pylint: disable=C0103


BLUE = '\033[94m'
RED = '\033[91m'
YELLOW = '\033[93m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
GREEN = '\033[92m'
ENDC = '\033[0m'


def me(col, txt):
    """Returns the txt in col color"""
    try:
        return globals()[col.lower()](txt)
    except KeyError:
        return txt


def blue(txt):
    """Returns a string with txt in blue color"""
    return '%s%s%s' % (BLUE, txt, ENDC)


def red(txt):
    """Returns a string with txt in red color"""
    return '%s%s%s' % (RED, txt, ENDC)


def yellow(txt):
    """Returns a string with txt in yellow color"""
    return '%s%s%s' % (YELLOW, txt, ENDC)


def purple(txt):
    """Returns a string with txt in purple color"""
    return '%s%s%s' % (PURPLE, txt, ENDC)


def cyan(txt):
    """Returns a string with txt in cyan color"""
    return '%s%s%s' % (CYAN, txt, ENDC)


def darkcyan(txt):
    """Returns a string with txt in dark cyan color"""
    return '%s%s%s' % (DARKCYAN, txt, ENDC)


def gren(txt):
    """Returns a string with txt in green color"""
    return '%s%s%s' % (GREEN, txt, ENDC)
