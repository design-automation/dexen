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


class DexenRegistryDiscoveryError(Exception):
    pass

class DexenConnectionException(Exception):
    pass

class DexenInvalidJobDefError(Exception):
    pass

class DexenInvalidJobNameError(Exception):
    pass

class ScriptException(Exception):
    pass

class SlaveException(Exception):
    pass

class AllNodeBusyException(Exception):
    pass

class ServerAlreadyRegisteredException(Exception):
    pass

class ConnectionIsNoneException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class JobNotExistsException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        
class ScoreNotExistsException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class ScoreAlreadyExistsException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class JobAlreadyStoppedException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class JobIsRunningException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class TaskAlreadyRegisteredException(Exception):
    pass

class NonExistentTaskException(Exception):
    pass
