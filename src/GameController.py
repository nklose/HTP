# Main controller for HTP
# Collection of universal utility functions

import time

from datetime import datetime

time_format = '%Y-%m-%d %H:%M:%S'

# gets the current timestamp
def current_time():
    ts = time.time()
    return datetime.fromtimestamp(ts).strftime(time_format)

# converts a string to a timestamp
def string_to_ts(string):
    return datetime.strptime(string, time_format)

# converts a timestamp to a string
def ts_to_string(ts):
    return datetime.strftime(ts, time_format)
