from os import pardir
from os.path import abspath, join, dirname

DEFAULT_DATA_DIR = abspath(join(dirname(abspath(__file__)), pardir, pardir, 'data'))


def default_raw_dir():
    return join(DEFAULT_DATA_DIR, 'raw')


def default_json_dir():
    return join(DEFAULT_DATA_DIR, 'json')


def default_index_dir():
    return join(DEFAULT_DATA_DIR, 'index')


# TODO move extraction code into 'extract' module
# TODO move indexation code into 'index' module
