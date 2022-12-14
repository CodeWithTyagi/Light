# Light UserBot
# Copyright (C) 2021-2022 CodeWithTyagi
#
# This file is a part of < https://github.com/CodeWithTyagi/Light >
# Please read the GNU Affero General Public License in
# https://www.github.com/CodeWithTyagi/Light/blob/main/LICENSE

import os
import platform
import sys
from logging import INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger

from ..configs import Var


def where_hosted():
    if os.getenv("DYNO"):
        return "heroku"
    if os.getenv("RAILWAY_STATIC_URL"):
        return "railway"
    if os.getenv("OKTETO_TOKEN"):
        return "okteto"
    if os.getenv("KUBERNETES_PORT"):
        return "qovery | kubernetes"
    if os.getenv("RUNNER_USER") or os.getenv("HOSTNAME"):
        return "github actions"
    if os.getenv("ANDROID_ROOT"):
        return "termux"
    if os.getenv("FLY_APP_NAME"):
        return "fly.io"
    return "local"


from telethon import __version__
from telethon.tl.alltlobjects import LAYER

from ..version import __version__ as lightVer

file = f"light{sys.argv[6]}.log" if len(sys.argv) > 6 else "light.log"

if os.path.exists(file):
    os.remove(file)

HOSTED_ON = where_hosted()
LOGS = getLogger("LightUB")
TelethonLogger = getLogger("Telethon")
TelethonLogger.setLevel(WARNING)

_, v, __ = platform.python_version_tuple()

if int(v) < 10:
    from ._extra import _fix_logging

    _fix_logging(FileHandler)

if HOSTED_ON == "local":
    from ._extra import _ask_input

    _ask_input()

_LOG_FORMAT = "%(asctime)s | %(filename)s : [%(name)s ~ %(levelname)s] - %(message)s"
basicConfig(
    format=_LOG_FORMAT,
    level=INFO,
    datefmt="%d/%m/%y, %H:%M:%S",
    handlers=[FileHandler(file), StreamHandler()],
)

try:
    import coloredlogs

    coloredlogs.install(level=None, logger=LOGS, fmt=_LOG_FORMAT)
    try:
        from ..fns._safety import KEEP_SAFE, call_back

    except Exception:

        LOGS.exception("'safety' package not found!")
except ImportError:
    pass

LOGS.info(
    """
              -------------------------------------
                  Starting Light Bot Deployment
              -------------------------------------
"""
)

LOGS.info(f"Python version - {platform.python_version()}")
LOGS.info(f"Telethon Version - {__version__} [Layer: {LAYER}]")
LOGS.info(f"Light Bot Version - {lightVer} [{HOSTED_ON}]")
