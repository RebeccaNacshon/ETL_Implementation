# -----------------------------------------------------------------------------
#    HeartBeat - Yet Another HeartBeat Server
#    Copyright (C) 2011 Some Hackers In Town
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------------

import logging
from logging.handlers import RotatingFileHandler
from ConfigParser import NoSectionError


def setup_logger(config=None, logfile=None, debug=False):
    """
    Setup the Master channel of HeartBeat logger.
    """
    logparam = {}
    handlerparam = {}
    LOG_FORMAT = '[%(asctime)s] %(levelname)-8s : "%(message)s"'

    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOG_MAX_BYTES = 2 * 1024 * 1024  # 2Mb
    LOG_BACKUP_COUNT = 5
    LOG_LEVEL = 1
    formatter = logging.Formatter(LOG_FORMAT)
    logparam['format'] = LOG_FORMAT
    logparam['level'] = int(LOG_LEVEL)
    logparam['datefmt'] = LOG_DATE_FORMAT
    handlerparam['maxBytes'] = LOG_MAX_BYTES
    handlerparam['backupCount'] = LOG_BACKUP_COUNT
    if config:
        try:
            logparam['level'] = int(config.get("Log", "level"))
            logparam['datefmt'] = config.get("Log", "date_format")
            handlerparam['maxBytes'] = int(config.get("Log", "max_size"))
            handlerparam['backupCount'] = int(config.get("Log", "backups"))
        except NoSectionError:
            print "Malform config file. 'Log' section is missing."
            print "Skipping."

    logging.basicConfig(**logparam)
    logger = logging.getLogger("HeartBeat")

    if logfile:
        LOG_FILENAME = logfile
        handler = RotatingFileHandler(
        LOG_FILENAME, **handlerparam)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = debug
    return logger
