from django.core.exceptions import MiddlewareNotUsed
import sys

from . import build_index, milli_db_is_present
from .settings import (
    MILLI_REBUILD_CACHE_ON_SERVER_START,
    MILLI_NO_LOGGING,
    MILLI_BUILD_CACHE_ON_SERVER_START,
)


class MilliStartupMiddleware:
    def __init__(self, *args, **kwargs):
        # This file only gets run once, so this middleware is parsed and then
        # immediately jettisoned from the middleware list and never run again.
        raise MiddlewareNotUsed("Startup complete")


log = not MILLI_NO_LOGGING
built = False

if not milli_db_is_present() and MILLI_BUILD_CACHE_ON_SERVER_START:
    if log:
        sys.stdout.write("Creating search index...\n")
    build_index()
    built = True

elif (
    milli_db_is_present()
    and MILLI_REBUILD_CACHE_ON_SERVER_START
    and MILLI_BUILD_CACHE_ON_SERVER_START
):
    if log:
        sys.stdout.write("Rebuilding search index...\n")
    build_index(remove_existing=True)
    built = True

if log and built:
    sys.stdout.write("Search index complete!\n")
