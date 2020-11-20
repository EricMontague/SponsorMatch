"""This module contains helper functions related to forms."""


def time_intervals(start, end, delta, time_format):
    """Return a list of tuples containing an id and a datetime.time object
   with each datetime.time object separated by the given delta
   """
    times = []
    i = 1
    current = start
    while current <= end:
        times.append((i, current.strftime(time_format)))
        current += delta
        i += 1
    return times
