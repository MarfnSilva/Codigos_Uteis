# -*- coding: utf-8 -*-

from meerkat_helpers import *
from GenericTrace import *
import sys, threading

if __name__ == '__main__':
    trace("Integração Meerkat: v1.00", color='Gold')
    # TO DO - full_db_verify = True
    log = False
    while True:
        last_modify, datetime_now = read_last_iteration()
        cardholders_to_update = get_wxs_users(last_modify)
        if cardholders_to_update:
            update_meerkat_users(cardholders_to_update)

        write_iteration_datetime(datetime_now)
        log = iam_alive_log(log)
        time.sleep(5)

        