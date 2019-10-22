import sys

from typing import Union, Iterable, List
from pandas import DataFrame
from datetime import datetime


def print_info(info, file=sys.stdout, end="\n"):
    print("[{0}]: {1}".format(datetime.now().strftime('%H:%M:%S'), info), file=file, end=end)


def print_err(info):
    print_info(info, file=sys.stderr)


def print_table(table: Union[DataFrame, list]):
    print()

    if isinstance(table, DataFrame):
        col_widths = _get_dataframe_col_widths(table)
        col_widths = [width + 2 for width in col_widths]
        _print_row(list(table.columns), col_widths=col_widths)
        for _, row in table.iterrows():
            _print_row(row, col_widths=col_widths)
    else:
        col_width = max(len(str(word)) for row in table for word in row) + 2  # padding
        for row in table:
            _print_row(row, col_width)


def _print_row(row: Iterable, col_width: int = 0, col_widths: List[int] = None):
    if col_widths:
        tmp_list = [str(word).ljust(col_widths[col_i]) for col_i, word in enumerate(row)]
    else:
        tmp_list = [str(word).ljust(col_width) for word in row]
    print("".join(tmp_list))


def _get_dataframe_col_widths(table: DataFrame) -> List[int]:
    widths = []
    for column in table.columns:
        width = max(table[column].map(lambda x: len(str(x))).max(), len(str(column)))
        widths.append(width)

    return widths


def test_print_table():
    df = DataFrame([['A', 24], ['X', 62], ['F', 0]], columns=['class', 'count'])
    print_table(df)