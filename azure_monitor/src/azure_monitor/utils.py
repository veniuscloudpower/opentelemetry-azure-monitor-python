# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import locale
import os
import platform
import sys
import threading
import time

from opentelemetry.sdk.version import __version__ as opentelemetry_version

from azure_monitor.version import __version__ as ext_version

azure_monitor_context = {
    "ai.cloud.role": os.path.basename(sys.argv[0]) or "Python Application",
    "ai.cloud.roleInstance": platform.node(),
    "ai.device.id": platform.node(),
    "ai.device.locale": locale.getdefaultlocale()[0],
    "ai.device.osVersion": platform.version(),
    "ai.device.type": "Other",
    "ai.internal.sdkVersion": "py{}:ot{}:ext{}".format(
        platform.python_version(), opentelemetry_version, ext_version
    ),
}


def ns_to_duration(nanoseconds):
    value = (nanoseconds + 500000) // 1000000  # duration in milliseconds
    value, microseconds = divmod(value, 1000)
    value, seconds = divmod(value, 60)
    value, minutes = divmod(value, 60)
    days, hours = divmod(value, 24)
    return "{:d}.{:02d}:{:02d}:{:02d}.{:03d}".format(
        days, hours, minutes, seconds, microseconds
    )


class PeriodicTask(threading.Thread):
    """Thread that periodically calls a given function.

    :type interval: int or float
    :param interval: Seconds between calls to the function.

    :type function: function
    :param function: The function to call.

    :type args: list
    :param args: The args passed in while calling `function`.

    :type kwargs: dict
    :param args: The kwargs passed in while calling `function`.
    """

    def __init__(self, interval, function, args=None, kwargs=None):
        super(PeriodicTask, self).__init__()
        self.interval = interval
        self.function = function
        self.args = args or []
        self.kwargs = kwargs or {}
        self.finished = threading.Event()

    def run(self):
        wait_time = self.interval
        while not self.finished.wait(wait_time):
            start_time = time.time()
            self.function(*self.args, **self.kwargs)
            elapsed_time = time.time() - start_time
            wait_time = max(self.interval - elapsed_time, 0)

    def cancel(self):
        self.finished.set()
