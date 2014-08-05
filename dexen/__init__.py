# ==================================================================================================
#
#    Copyright (c) 2008, Patrick Janssen (patrick@janssen.name)
#
#    This file is part of Dexen.
#
#    Dexen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Dexen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================

from dexen.client.api import *


def getLoggingConfig(log_path):
    return {
        "version" : 1,
        "disable_existing_loggers" : False,
        "formatters" : {
            "simple" : {
                "format" : "[%(levelname)-5s] - %(asctime)s - %(name)-15s - " +
                           "%(message)s",
                "datefmt" : "%Y/%m/%d %H:%M:%S"
            }
        },
        "handlers" : {
            "console" : {
                "level" : "INFO",
                "class" : "logging.StreamHandler",
                "formatter" : "simple"
            },
            "file": {
                "level" : "DEBUG",
                "class" : "logging.FileHandler",
                "formatter" : "simple",
                "filename" : log_path,
                "mode" : "w"
            }
        },
        "loggers" : {
            __name__ : {
                "handlers" : ["console", "file"],
                "level" : "DEBUG",
            }
        }
    }

