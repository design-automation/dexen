

import time

from dexen.common import data_api


def main():
    do = data_api.DataObject("word_counter")
    do.inc_value("go", 1)
    print "Word count go: ", do.get_value("go")
    time.sleep(2)
    do.inc_value("go", 3)
    time.sleep(4)
    print "Word count go: ", do.get_value("go")


if __name__ == '__main__':
    main()
