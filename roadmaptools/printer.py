import sys

from datetime import datetime


def print_info(info, file=sys.stdout):
    print("[{0}]: {1}".format(datetime.now().time(), info), file=file)


def print_err(info):
    print_info(info, file=sys.stderr)


def print_table(table):
    col_width = max(len(str(word)) for row in table for word in row) + 2  # padding
    for row in table:
        print ("".join(str(word).ljust(col_width) for word in row))
