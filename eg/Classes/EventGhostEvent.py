# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2016 EventGhost Project <http://www.eventghost.org/>
#
# EventGhost is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# EventGhost is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with EventGhost. If not, see <http://www.gnu.org/licenses/>.

from fnmatch import fnmatchcase
from collections import deque
from time import clock
import six
import threading

# Local imports
import eg

# some shortcuts to speed things up
#pylint: disable-msg=C0103
actionThread = eg.actionThread
LogEvent = eg.log.LogEvent
RunProgram = eg.RunProgram
GetItemPath = eg.EventItem.GetPath
config = eg.config


runningEvents = {}


class EventSingleton(type):

    def __call__(cls, suffix="", payload=None, prefix="Main", source=eg):
        if suffix:
            string = prefix + "." + suffix
        else:
            string = prefix

        if string in eg.runningEvents:
            eg.runningEvents[string].payloads += [payload]
            eg.runningEvents[string].sources = [source]

        else:
            eg.runningEvents[string] = (
                super(EventSingleton, cls).__call__(
                    suffix,
                    payload,
                    prefix,
                    source
                )
            )

        return eg.runningEvents[string]


@six.add_metaclass(EventSingleton)
class EventGhostEvent(threading.Thread):
    """
    .. attribute:: string

        This is the full qualified event string as you see it inside the
        logger, with the exception that if the payload field
        (that is explained below) is not None the logger will also show it
        behind the event string, but this is not a part of the event string
        we are talking about here.

    .. attribute:: payload

        A plugin might publish additional data related to this event.
        Through payload you can access this data. For example the 'Network
        Event Receiver' plugin returns also the IP of the client that has
        generated the event. If there is no data, this field is ``None``.

    .. attribute:: prefix

        This is the first part of the event string till the first dot. This
        normally identifies the source of the event as a short string.

    .. attribute:: suffix

        This is the part of the event string behind the first dot. So you
        could say:

        event.string = event.prefix + '.' + event.suffix

    .. attribute:: time

        The time the event was generated as a floating point number in
        seconds (as returned by the clock() function of Python's time module).
        Since most events are processed very quickly, this is most likely
        nearly the current time. But in some situations it might be more
        clever to use this time, instead of the current time, since even
        small differences might matter (for example if you want to determine
        a double-press).

    .. attribute:: isEnded

        This boolean value indicates if the event is an enduring event and is
        still active. Some plugins (e.g. most of the remote receiver plugins)
        indicate if a button is pressed longer. As long as the button is
        pressed, this flag is ``False`` and in the moment the user releases the
        button the flag turns to ``True``. So you can poll this flag to see, if
        the button is still pressed.

    """
    skipEvent = False

    def __init__(self, suffix="", payload=None, prefix="Main", source=eg):
        if suffix:
            self.string = prefix + "." + suffix
        else:
            self.string = prefix

        self.payloads = [payload]

        self.time = clock()
        self.result = None
        self.lastFoundWindows = []
        self.stopExecutionFlag = False
        self.indent = 0
        self.programReturnStack = []
        self.programCounter = None
        self.isEnded = False
        self.event = self

        self.prefix = prefix
        self.suffix = suffix
        self.payload = payload
        self.source = source

        self.shouldEnd = threading.Event()
        self.upFuncList = []
        self.sources = [source]

        self.__queue = deque()
        self.percent_run = 0.0

        threading.Thread.__init__(self, name=self.string)

    def AddUpFunc(self, func, *args, **kwargs):
        if self.isEnded:
            func(*args, **kwargs)
        else:
            self.upFuncList.append((func, args, kwargs))

    def run(self):
        while self.__queue:
            do = self.__queue.popleft()
            do()

        del self.upFuncList[:]
        del eg.runningEvents[self.string]

    def DoUpFuncs(self):
        for func, args, kwargs in self.upFuncList:
            func(*args, **kwargs)
        self.isEnded = True

    def Execute(self):
        def do():
            self.time = clock()
            self.result = None
            self.lastFoundWindows = []
            self.stopExecutionFlag = False
            self.indent = 0
            self.programReturnStack = []
            self.programCounter = None
            self.isEnded = False
            self.payload = self.payloads.pop(0)
            self.source = self.sources.pop(0)
            self.percent_run = 0.0

            if self.string in eg.notificationHandlers:
                for l in eg.notificationHandlers[self.string].listeners:
                    if l(self) is True:
                        return

            eventHandlerList = []
            for key, val in eg.eventTable.iteritems():
                if (
                    self.event.string == key or
                    (
                        ("*" in key or "?" in key) and
                        fnmatchcase(self.string, key)
                    )
                ):
                    eventHandlerList += val

            activeHandlers = set()
            for eventHandler in eventHandlerList:
                obj = eventHandler
                while obj:
                    if not obj.isEnabled:
                        break
                    obj = obj.parent
                else:
                    activeHandlers.add(eventHandler)

            for listener in eg.log.eventListeners:
                listener.LogEvent(self)

            if config.onlyLogAssigned and len(activeHandlers) == 0:
                self.SetStarted()
                return

            # show the event in the logger
            LogEvent(self)

            activeHandlers = sorted(activeHandlers, key=GetItemPath)
            active_handler_count = float(len(activeHandlers))

            while activeHandlers:
                completed = active_handler_count - len(activeHandlers)
                completed = (float(completed) / active_handler_count) * 100.0

                if eg.mainFrame is not None:
                    eg.mainFrame.logCtrl.SetEventMeter(completed)

                eventHandler = activeHandlers.pop(0)
                try:
                    self.programCounter = (eventHandler.parent, None)
                    self.indent = 1
                    RunProgram()
                except:
                    eg.PrintTraceback()
                if self.skipEvent:
                    break

            if eg.mainFrame is not None:
                eg.mainFrame.logCtrl.SetEventMeter(100.0)

            self.SetStarted()
            eg.SetProcessingState(1, self)

        self.__queue.append(do)

        if not self.is_alive():
            self.start()

    def stop(self):
        if self.is_alive():
            self.join(3)

    def SetShouldEnd(self):
        if not self.shouldEnd.isSet():
            self.shouldEnd.set()
            eg.SetProcessingState(0, self)
            actionThread.Call(self.DoUpFuncs)
            self.__join()

    def SetStarted(self):
        if self.shouldEnd.isSet():
            self.DoUpFuncs()
