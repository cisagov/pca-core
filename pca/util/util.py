"""pca/util/util.py."""

# Standard Python Libraries
from collections import OrderedDict
from datetime import datetime

# import netaddr      #TODO Get rid of this; need replacement for IPSet functionality
import ipaddress
import itertools
import json
import logging
from logging.handlers import RotatingFileHandler
import sys
import time

# Third-Party Libraries
import bson
from dateutil.relativedelta import SU, relativedelta
import dateutil.tz as tz


def ranges(i):
    """Generate pairs of range beginning and ends from a sorted list of integers."""
    for bogus, b in itertools.groupby(enumerate(i), lambda x_y: x_y[0] - x_y[1]):
        b = list(b)
        yield b[0][1], b[-1][1]


def list_to_range_string(sortedList):
    """Generate a shorthand string representing the integers of a sorted list."""
    r = ranges(sortedList)
    result = []
    for a, b in r:
        if a == b:
            result.append(str(a))
        else:
            result.append("{}-{}".format(a, b))
    return ",".join(result)


def range_string_to_list(range_string):
    """Return a list of the values represented by a range string."""
    if range_string == "":
        return []
    output = list()
    for x in range_string.split(","):
        y = x.split("-")
        if len(y) > 1:
            output.extend(range(int(y[0]), int(y[1]) + 1))
        else:
            output.append(int(y[0]))
    return output


def copy_attrs(source, dest, skip=[]):
    """Copy attributes from source to destination."""
    for (k, v) in source.items():
        if k in skip:
            continue
        dest[k] = v


def custom_json_handler(obj):
    """Parse JSON object."""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    elif type(obj) == bson.objectid.ObjectId:
        return repr(obj)
    elif type(obj) in [
        ipaddress.IPv4Address,
        ipaddress.IPv6Address,
        ipaddress.IPv4Network,
        ipaddress.IPv6Network,
    ]:
        return str(obj)
    # elif type(obj) == netaddr.IPSet:
    #     return obj.iter_cidrs()
    else:
        raise TypeError(
            "Object of type %s with value of %s is not JSON serializable"
            % (type(obj), repr(obj))
        )


def pp(obj):
    """Pretty print function."""
    print(to_json(obj))


def to_json(obj):
    """Write object to JSON."""
    return json.dumps(obj, sort_keys=True, indent=4, default=custom_json_handler)


def isXML(filename):
    """Determine if file is in XML format."""
    f = open(filename)
    line = f.readline()
    if line.startswith("<?xml"):
        return True
    return False


def count_file_lines(filename):
    """Count the number of lines in a file."""
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def clean_mongo_key(key):
    """Clean up key as MongoDB dict keys cannot contain periods or start with a $."""
    key = key.replace(".", "_")
    if key.startswith("$"):
        key = key.replace("$", "_", 1)
    return key


def safe_divide(numerator, denominator, precision=1, default=0.0):
    """Safely divide two numbers, avoiding div by zero and handling int div."""
    if denominator == 0:
        return default
    return round(float(numerator) / denominator, precision)


def safe_percent(numerator, denominator, precision=1, default=0.0):
    """Safely produces a percentage, avoiding div by zero."""
    if denominator == 0:
        return default
    return round(float(numerator) / denominator * 100, precision)


def pretty_bail(self, exception, thing):
    """Print exception then exits the program."""
    print(exception)
    print("=" * 80)
    pp(thing)
    sys.exit(-1)


def time_to_utc(in_time):
    """Convert time to UTC.

    If the time passed in does not have zone information, it is assumed to be
    the local timezone.
    """
    if in_time.tzinfo is None:
        in_time = in_time.replace(tzinfo=tz.tzlocal())
    utc_time = in_time.astimezone(tz.tzutc())
    return utc_time


def time_to_local(in_time):
    """
    Convert time to the local timezone.

    If the time passed in does not have zone information,
    it is assumed to be UTC.
    """
    if in_time.tzinfo is None:
        in_time = in_time.replace(tzinfo=tz.tzutc())
    local_time = in_time.astimezone(tz.tzlocal())
    return local_time


def utcnow():
    """Return a timezone-aware datetime object with the current time in UTC."""
    return datetime.now(tz.tzutc())


class Enumerator(object):
    """Provides an enumerator object."""

    def __init__(self, *names):
        """Initialize values."""
        self._values = OrderedDict((value, value) for value in names)

    def __getattribute__(self, attr):
        """Get Enumerator attributes."""
        try:
            return object.__getattribute__(self, "_values")[attr]
        except KeyError:
            return object.__getattribute__(self, attr)

    def __getitem__(self, item):
        """Get item by Enumerator."""
        if isinstance(item, int):
            return self._values.keys()[item]
        return self._values[item]

    def __repr__(self):
        """Get key values as strings."""
        return repr(self._values.keys())

    def __len__(self):
        """Get length of values."""
        return len(self._values)


class LogFilter(logging.Filter):
    """Filter log."""

    def filter(self, record):
        # import IPython; IPython.embed() #<<< BREAKPOINT >>>
        """Filter out fabric messages."""
        if record.name.startswith("paramiko"):
            return False
        return True


def setup_logging(level=logging.INFO, console=False, filename=None):
    """Configure logging to console and file."""
    LOGGER_FORMAT = "%(asctime)-15s %(levelname)s %(name)s - %(message)s"
    formatter = logging.Formatter(LOGGER_FORMAT)
    formatter.converter = time.gmtime  # log times in UTC
    root = logging.getLogger()
    root.setLevel(level)
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.addFilter(LogFilter())
        root.addHandler(console_handler)
    if filename:
        file_handler = RotatingFileHandler(
            filename, maxBytes=pow(1024, 2) * 128, backupCount=9
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(LogFilter())
        root.addHandler(file_handler)
    return root


def report_dates(now=None):
    """Return a dictionary of dates useful for reporting.

    If a "now" date is provided, dates are calculated using that date,
    otherwise it will use the current wall clock time.  All times UTC.
    See the return statement for a list of the dates returned. ;)
    """
    if now is None:
        now = utcnow()

    if now.month >= 10:  # FY starts in October
        fy_start = now + relativedelta(
            month=10, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    else:
        fy_start = now + relativedelta(
            years=-1, month=10, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    fy_end = fy_start + relativedelta(years=1, microseconds=-1)

    prev_fy_start = fy_start - relativedelta(years=1)
    prev_fy_end = fy_start - relativedelta(microseconds=1)
    month_start = now + relativedelta(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = month_start + relativedelta(months=1, microseconds=-1)
    prev_month_start = month_start - relativedelta(months=1)
    prev_month_end = month_start - relativedelta(microseconds=1)
    week_start = now + relativedelta(
        weekday=SU(-1), hour=0, minute=0, second=0, microsecond=0
    )
    week_end = week_start + relativedelta(day=7, microseconds=-1)
    prev_week_start = now + relativedelta(
        weekday=SU(-2), hour=0, minute=0, second=0, microsecond=0
    )
    prev_week_end = week_start - relativedelta(microseconds=1)

    return {
        "now": now,
        "fy_start": fy_start,
        "fy_end": fy_end,
        "prev_fy_start": prev_fy_start,
        "prev_fy_end": prev_fy_end,
        "month_start": month_start,
        "month_end": month_end,
        "prev_month_start": prev_month_start,
        "prev_month_end": prev_month_end,
        "week_start": week_start,
        "week_end": week_end,
        "prev_week_start": prev_week_start,
        "prev_week_end": prev_week_end,
    }


def warn_and_confirm(message):
    """Ask user to continue."""
    print("WARNING: %s" % message, file=sys.stderr)
    print(file=sys.stderr)
    yes = input('Type "yes" if you are sure that you want to continue: ')
    return yes == "yes"
