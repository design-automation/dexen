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

def EventFromJSON(event_json):
    """ Create an instance of one of the Dexen event classes (subclasses of dexen.common.DexenEvent)
    from a json representation.
    """
    if (not event_json) or ("name" not in event_json):
        return None
    if event_json['name'] == JobStartedEvent.__name__:
        return JobStartedEvent()
    if event_json['name'] == JobStoppedEvent.__name__:
        return JobStoppedEvent()
    if event_json['name'] == PeriodicTimeEvent.__name__:
        return PeriodicTimeEvent(float(event_json['period']))
    if event_json['name'] == OneShotTimeEvent.__name__:
        return OneShotTimeEvent(float(event_json["after"]))
    return DexenEvent()


class DexenEvent(object):
    """ Class that represents a Dexen event - see subclasses.
    """
    def __init__(self):
        pass


class JobStoppedEvent(DexenEvent):
    def __init__(self):
        super(JobStoppedEvent, self).__init__()

    def json(self):
        return {"name" : self.__class__.__name__}


class JobStartedEvent(DexenEvent):
    def __init__(self):
        super(JobStartedEvent, self).__init__()

    def json(self):
        return {"name" : self.__class__.__name__}


class TimeBasedEvent(DexenEvent):
    def __init__(self):
        super(TimeBasedEvent, self).__init__()


class PeriodicTimeEvent(TimeBasedEvent):
    def __init__(self, period):
        super(PeriodicTimeEvent, self).__init__()
        self.period = period # in seconds

    def json(self):
        return {"name" : self.__class__.__name__,
                "period" : self.period}


class OneShotTimeEvent(TimeBasedEvent):
    def __init__(self, after):
        super(OneShotTimeEvent, self).__init__()
        self.after = after

    def json(self):
        return {"name" : self.__class__.__name__,
                "after" : self.after}
