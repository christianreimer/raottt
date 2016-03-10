"""
Scheduler wrapper for heroku to run a job periodically.
"""

from apscheduler.schedulers.blocking import BlockingScheduler

import os
import spok


sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=2)
def timed_job():
    pid_red = os.environ['SPOK_RED']
    pid_blue = os.environ['SPOK_BLUE']

    min_stock = 50
    lower = 4
    upper = 12
    num_games = 20
    ttl = 3600

    spok.one_sweep(red_pid, blue_pid, min_stock, lower, upper, num_games, ttl)


sched.start()
