import time

from KVDatabase import *
import threading
import functools


class usingThread:
    def __init__(self, n=1):
        self.conn = threading.Semaphore(n)

    def __call__(self, func):
        @functools.wraps(func)
        def tmp1(*args, **kwargs):
            with self.conn:
                func(*args, **kwargs)

        @functools.wraps(func)
        def tmp(*args, **kwargs):
            threading.Thread(target=tmp1, args=args, kwargs=kwargs).start()

        return tmp


class ScheduleTask:
    def __init__(self, interval=10):
        self.timestamp = 0
        self.interval = interval

    def update_check(self, timestamp):
        self.timestamp = timestamp

    def check_timestamp(self, timestamp):
        if self.timestamp + self.interval <= timestamp:
            self.update_check(timestamp)
            self.do_check()

    def do_check(self):
        pass


class Schedule:
    def __init__(self, task: [ScheduleTask], interval=1):
        self.task: [ScheduleTask] = task
        self.interval = interval
        self.flag = True

    @usingThread(1)
    def start(self):
        while self.flag:
            timestamp = time.time()
            for task in self.task:
                task.check_timestamp(timestamp)
            time.sleep(self.interval)

    def stop(self):
        self.flag = False