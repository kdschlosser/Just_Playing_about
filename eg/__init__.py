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

import stackless
import sys

# the following three import are needed if we are running from source and the
# Python distribution was not installed by the installer. See the following
# link for details:
# http://www.voidspace.org.uk/python/movpy/reference/win32ext.html#id10
import pywintypes  # NOQA
import pythoncom  # NOQA
import win32api  # NOQA

# Local imports
import Cli
from Classes.WindowsVersion import WindowsVersion

import wx
import __builtin__
from types import ModuleType
import os
import locale
import threading
import PIL.Image

PIL.Image.preinit()
PIL.Image.init()

__builtin__.wx = wx


class DynamicModule(object):
    APP_NAME = "EventGhost"
    CORE_PLUGIN_GUIDS = (
        "{9D499A2C-72B6-40B0-8C8C-995831B10BB4}",  # "EventGhost"
        "{A21F443B-221D-44E4-8596-E1ED7100E0A4}",  # "System"
        "{E974D074-B0A3-4D0C-BBD1-992475DDD69D}",  # "Window"
        "{6B1751BF-F94E-4260-AB7E-64C0693FD959}",  # "Mouse"
    )

    ID_TEST = wx.NewId()

    revision = 2000
    startupArguments = Cli.args
    debugLevel = startupArguments.debugLevel
    systemEncoding = locale.getdefaultlocale()[1]
    useTreeItemGUID = False
    document = None
    mainFrame = None
    notificationHandlers = {}
    pluginList = []
    mainThread = threading.currentThread()
    currentItem = None
    GUID = GUID()
    pyCrustFrame = None
    dummyAsyncoreDispatcher = None
    wit = None
    socketSever = None
    eventTable = {}

    @property
    def result(self):
        thread = threading.current_thread()
        if thread == self.mainThread:
            return None

        return thread.result

    @result.setter
    def result(self, value):
        thread = threading.current_thread()
        if thread != self.mainThread:
            thread.result = value

    @property
    def event(self):
        thread = threading.current_thread()
        if thread == self.mainThread:
            return None

        return thread.event

    @event.setter
    def event(self, value):
        pass

    @property
    def eventString(self):
        thread = threading.current_thread()
        if thread == self.mainThread:
            return None

        return thread.event.string

    @eventString.setter
    def eventString(self, value):
        pass

    @property
    def lastFoundWindows(self):
        thread = threading.current_thread()
        if thread == self.mainThread:
            return []

        return thread.lastFoundWindows

    @lastFoundWindows.setter
    def lastFoundWindows(self, value):
        thread = threading.current_thread()
        if thread != self.mainThread:
            thread.lastFoundWindows = value

    @property
    def stopExecutionFlag(self):
        thread = threading.current_thread()
        if thread == self.mainThread:
            return False

        return thread.stopExecutionFlag

    @stopExecutionFlag.setter
    def stopExecutionFlag(self, value):
        thread = threading.current_thread()
        if thread != self.mainThread:
            thread.stopExecutionFlag = value

    @property
    def indent(self):
        thread = threading.current_thread()
        if thread == self.mainThread:
            return 0

        return thread.indent

    @indent.setter
    def indent(self, value):
        thread = threading.current_thread()
        if thread != self.mainThread:
            thread.indent = value

    @property
    def programReturnStack(self):
        thread = threading.current_thread()
        if thread == self.mainThread:
            return []

        return thread.programReturnStack

    @programReturnStack.setter
    def programReturnStack(self, value):
        thread = threading.current_thread()
        if thread != self.mainThread:
            thread.programReturnStack = value

    @property
    def programCounter(self):
        thread = threading.current_thread()
        if thread == self.mainThread:
            return None

        return thread.programCounter

    @programCounter.setter
    def programCounter(self, value):
        thread = threading.current_thread()
        if thread != self.mainThread:
            thread.programCounter = value

    @property
    def Cli(self):
        return Cli

    @property
    def plugins(self):
        if self.__plugins is None:
            self.__plugins = self.Bunch()
        return self.__plugins

    @property
    def globals(self):
        if self.__globals is None:
            self.__globals = self.Bunch()
            self.__globals.eg = self
        return self.__globals

    @property
    def actionGroup(self):
        if self.__actionGroup is None:
            self.__actionGroup = self.Bunch()
            self.__actionGroup.items = []
        return self.__actionGroup

    @staticmethod
    def CommandEvent():
        """Generate new (CmdEvent, Binder) tuple
            e.g. MooCmdEvent, EVT_MOO = EgCommandEvent()
        """
        evttype = wx.NewEventType()


        class _Event(wx.PyCommandEvent):
            def __init__(self, id, **kw):
                wx.PyCommandEvent.__init__(self, evttype, id)
                self.__dict__.update(kw)
                if not hasattr(self, "value"):
                    self.value = None

            def GetValue(self):
                return self.value

            def SetValue(self, value):
                self.value = value


        return _Event, wx.PyEventBinder(evttype, 1)

    ValueChangedEvent, EVT_VALUE_CHANGED = CommandEvent.__func__()

    from WinApi.Dynamic import GetCurrentProcessId  # NOQA

    processId = GetCurrentProcessId()


    class Exception(Exception):
        def __unicode__(self):
            try:
                return "\n".join([unicode(arg) for arg in self.args])
            except UnicodeDecodeError:
                return "\n".join(
                    [str(arg).decode('mbcs') for arg in self.args])


    class StopException(Exception):
        pass


    class HiddenAction:
        pass


    def Bind(self, notification, listener):
        if notification not in self.notificationHandlers:
            notificationHandler = self.NotificationHandler()
            self.notificationHandlers[notification] = notificationHandler
        else:
            notificationHandler = self.notificationHandlers[notification]
        notificationHandler.listeners.append(listener)

    @staticmethod
    def CallWait(func, *args, **kwargs):
        result = [None]
        event = threading.Event()

        def CallWaitWrapper():
            try:
                result[0] = func(*args, **kwargs)
            finally:
                event.set()

        wx.CallAfter(CallWaitWrapper)
        event.wait()
        return result[0]

    @staticmethod
    def DummyFunc(*dummyArgs, **dummyKwargs):
        """
        Just a do-nothing-function, that accepts arbitrary arguments.
        """
        pass

    @staticmethod
    def Exit():
        """
        Sometimes you want to quickly exit a PythonScript, because you don't
        want to build deeply nested if-structures for example. eg.Exit() will
        exit your PythonScript immediately.
        (Note: This is actually a sys.exit() but will not exit EventGhost,
        because the SystemExit exception is catched for a PythonScript.)
        """
        sys.exit()

    def HasActiveHandler(self, eventstring):
        for eventHandler in self.eventTable.get(eventstring, []):
            obj = eventHandler
            while obj:
                if not obj.isEnabled:
                    break
                obj = obj.parent
            else:
                return True
        return False

    @staticmethod
    def MessageBox(message, caption=APP_NAME, style=wx.OK, parent=None):
        from Classes.MessageDialog import MessageDialog
        if parent is None:
            style |= wx.STAY_ON_TOP
        dialog = MessageDialog(parent, message, caption, style)
        result = dialog.ShowModal()
        dialog.Destroy()
        return result

    def Notify(self, notification, value=None):
        if notification in self.notificationHandlers:
            for listener in self.notificationHandlers[notification].listeners:
                listener(value)

    # pylint: disable-msg=W0613
    @staticmethod
    def RegisterPlugin(
        name=None,
        description=None,
        kind="other",
        author="[unknown author]",
        version="[unknown version]",
        icon=None,
        canMultiLoad=False,
        createMacrosOnAdd=False,
        url=None,
        help=None,
        guid=None,
        **kwargs
    ):
        """
        Registers information about a plugin to EventGhost.

        :param name: should be a short descriptive string with the name of the
           plugin.
        :param description: a short description of the plugin.
        :param kind: gives a hint about the category the plugin belongs to. It
            should be a string with a value out of ``"remote"`` (for remote
            receiver plugins), ``"program"`` (for program control plugins),
            ``"external"`` (for plugins that control external hardware) or
            ``"other"`` (if none of the other categories match).
        :param author: can be set to the name or a list of names of the
            developer(s) of the plugin.
        :param version: can be set to a version string.
        :param icon: can be a base64 encoded image for the plugin. If
            ``icon == None``, an "icon.png" will be used if it exists
            in the plugin folder.
        :param canMultiLoad: set this to ``True``, if a configuration can have
           more than one instance of this plugin.
        :param createMacrosOnAdd: if set to ``True``, when adding the plugin,
            EventGhost will ask the user, if he/she wants to add a folder with all
            actions of this plugin to his/her configuration.
        :param url: displays a clickable link in the plugin info dialog.
        :param help: a longer description and/or additional information for the
            plugin. Will be added to
            'description'.
        :param guid: will help EG to identify your plugin, so there are no name
            clashes with other plugins that accidentally might have the same
            name and will later ease the update of plugins.
        :param kwargs: just to consume unknown parameters, to make the call
           backward compatible.
        """
        pass

    # pylint: enable-msg=W0613

    def RestartAsyncore(self):
        """
        Informs the asyncore loop of a new socket to handle.
        """
        import asyncore
        import socket
        oldDispatcher = self.dummyAsyncoreDispatcher
        dispatcher = asyncore.dispatcher()
        dispatcher.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dummyAsyncoreDispatcher = dispatcher
        if oldDispatcher:
            oldDispatcher.close()
        if oldDispatcher is None:
            # create a global asyncore loop thread
            threading.Thread(
                target=asyncore.loop,
                name="AsyncoreThread"
            ).start()

    def RunProgram(self):
        from Classes.MacroItem import MacroItem
        self.stopExecutionFlag = False
        del self.programReturnStack[:]
        while self.programCounter is not None:
            programCounter = self.programCounter
            item, idx = programCounter
            item.Execute()
            if self.programCounter == programCounter:
                # program counter has not changed. Ask the parent for the next
                # item.
                if isinstance(item.parent, MacroItem):
                    self.programCounter = item.parent.GetNextChild(idx)
                else:
                    self.programCounter = None

            while self.programCounter is None and self.programReturnStack:
                # we have no next item in this level. So look in the return
                # stack if any return has to be executed
                self.indent -= 2
                item, idx = self.programReturnStack.pop()
                self.programCounter = item.parent.GetNextChild(idx)
        self.indent = 0

    def StopMacro(self, ignoreReturn=False):
        """
        Instructs EventGhost to stop executing the current macro after the
        current action (thus the PythonScript or PythonCommand) has finished.
        """
        self.programCounter = None
        if ignoreReturn:
            del self.programReturnStack[:]

    def Unbind(self, notification, listener):
        self.notificationHandlers[notification].listeners.remove(listener)

    def Wait(self, secs, raiseException=True):
        import time

        while secs > 0.0:
            if self.stopExecutionFlag:
                if raiseException:
                    raise self.StopException(
                        "Execution interrupted by the user.")
                else:
                    return False
            if secs > 0.1:
                time.sleep(0.1)
            else:
                time.sleep(secs)
            secs -= 0.1
        return True

    @property
    def messageReceiver(self):
        if self.__messageReceiver is None:
            from Classes.MainMessageReceiver import MainMessageReceiver

            self.__messageReceiver = MainMessageReceiver()

        return self.__messageReceiver

    @property
    def app(self):
        if self.__app is None:
            from Classes.App import App

            self.__app = App()

        return self.__app

    @property
    def Icons(self):
        import Icons
        return Icons

    @property
    def log(self):
        if self.__log is None:
            from Classes.Log import Log

            self.__log = Log()

            def TracebackHook(tType, tValue, traceback):
                self.__log.PrintTraceback(excInfo=(tType, tValue, traceback))

            sys.excepthook = TracebackHook

        return self.__log

    @property
    def Print(self):
        return self.log.Print

    @property
    def PrintError(self):
        return self.log.PrintError

    @property
    def PrintNotice(self):
        return self.log.PrintNotice

    @property
    def PrintTraceback(self):
        return self.log.PrintTraceback

    @property
    def PrintDebugNotice(self):
        return self.log.PrintDebugNotice

    @property
    def PrintWarningNotice(self):
        return self.log.PrintWarningNotice

    @property
    def PrintStack(self):
        return self.log.PrintStack

    @property
    def config(self):
        if self.__config is None:
            from Classes.Config import Config

            self.__config = Config()

            self.debugLevel = int(self.__config.logDebug) or self.debugLevel

        return self.__config

    @property
    def colour(self):
        if self.__colour is None:
            from Classes.Colour import Colour

            self.__colour = Colour()

        return self.__colour

    @property
    def text(self):
        if self.__text is None:
            from Classes.Text import Text

            if (
                self.startupArguments.isMain and
                not self.startupArguments.translate
            ):
                self.__text = Text(self.config.language)
            else:
                self.__text = Text('en_EN')

        return self.__text

    @property
    def actionThread(self):
        if self.__actionThread is None:
            from Classes.ActionThread import ActionThread

            self.__actionThread = ActionThread()

        return self.__actionThread

    @property
    def eventThread(self):
        if self.__eventThread is None:
            from Classes.EventThread import EventThread

            self.__eventThread = EventThread()

        return self.__eventThread

    @property
    def pluginManager(self):
        if self.__pluginManager is None:
            from Classes.PluginManager import PluginManager

            self.__pluginManager = PluginManager()

        return self.__pluginManager

    @property
    def scheduler(self):
        if self.__scheduler is None:
            from Classes.Scheduler import Scheduler

            self.__scheduler = Scheduler()

        return self.__scheduler

    @property
    def TriggerEvent(self):
        return self.eventThread.TriggerEvent

    @property
    def TriggerEnduringEvent(self):
        return self.eventThread.TriggerEnduringEvent

    @property
    def SendKeys(self):
        if self.__SendKeys is None:
            from WinApi.SendKeys import SendKeysParser  # NOQA

            self.__SendKeys = SendKeysParser()

        return self.__SendKeys

    @property
    def PluginClass(self):
        from Classes.PluginBase import PluginBase

        return PluginBase

    @property
    def ActionClass(self):
        from Classes.ActionBase import ActionBase

        return ActionBase

    @property
    def taskBarIcon(self):
        if self.__taskBarIcon is None:
            from Classes.TaskBarIcon import TaskBarIcon

            self.__taskBarIcon = TaskBarIcon(
                self.startupArguments.isMain and
                self.config.showTrayIcon and
                not self.startupArguments.translate and
                not self.startupArguments.install and
                not self.startupArguments.pluginFile
            )

        return self.__taskBarIcon

    @property
    def SetProcessingState(self):
        return self.taskBarIcon.SetProcessingState

    @property
    def folderPath(self):
        if self.__folderPath is None:
            from Classes.FolderPath import FolderPath

            self.__folderPath = FolderPath()

        return self.__folderPath

    @property
    def mainDir(self):
        return Cli.mainDir

    @property
    def configDir(self):
        return self.folderPath.configDir

    @property
    def corePluginDir(self):
        return self.folderPath.corePluginDir

    @property
    def localPluginDir(self):
        if self.__localPluginDir is None:
            self.__localPluginDir = self.folderPath.localPluginDir
        return self.__localPluginDir

    @property
    def imagesDir(self):
        return self.folderPath.imagesDir

    @property
    def languagesDir(self):
        return self.folderPath.languagesDir

    @property
    def sitePackagesDir(self):
        return self.folderPath.sitePackagesDir

    @property
    def cFunctions(self):
        cFunctions = __import__('cFunctions')
        if 'eg.cFunctions' not in sys.modules:
            sys.modules['eg.cFunctions'] = cFunctions

        return cFunctions

    @property
    def CorePluginModule(self):
        if self.__CorePluginModule is None:
            corePluginPackage = ModuleType("eg.CorePluginModule")
            corePluginPackage.__path__ = [eg.corePluginDir]

            sys.modules["eg.CorePluginModule"] = corePluginPackage
            self.__CorePluginModule = corePluginPackage

        return self.__CorePluginModule

    @property
    def UserPluginModule(self):
        if self.__UserPluginModule is None:
            userPluginPackage = ModuleType("eg.UserPluginModule")
            userPluginPackage.__path__ = [eg.localPluginDir]

            sys.modules["eg.UserPluginModule"] = userPluginPackage
            self.__UserPluginModule = userPluginPackage

        return self.__UserPluginModule

    @property
    def AboutDialog(self):
        from Classes.AboutDialog import AboutDialog

        return AboutDialog

    @property
    def ActionBase(self):
        from Classes.ActionBase import ActionBase

        return ActionBase

    @property
    def ActionGroup(self):
        from Classes.ActionGroup import ActionGroup

        return ActionGroup

    @property
    def ActionItem(self):
        from Classes.ActionItem import ActionItem

        return ActionItem

    @property
    def ActionSelectButton(self):
        from Classes.ActionSelectButton import ActionSelectButton

        return ActionSelectButton

    @property
    def ActionThread(self):
        from Classes.ActionThread import ActionThread

        return ActionThread

    @property
    def ActionWithStringParameter(self):
        from Classes.ActionWithStringParameter import ActionWithStringParameter

        return ActionWithStringParameter

    @property
    def AddActionDialog(self):
        from Classes.AddActionDialog import AddActionDialog

        return AddActionDialog

    @property
    def AddActionGroupDialog(self):
        from Classes.AddActionGroupDialog import AddActionGroupDialog

        return AddActionGroupDialog

    @property
    def AddEventDialog(self):
        from Classes.AddEventDialog import AddEventDialog

        return AddEventDialog

    @property
    def AddPluginDialog(self):
        from Classes.AddPluginDialog import AddPluginDialog

        return AddPluginDialog

    @property
    def AnimatedWindow(self):
        from Classes.AnimatedWindow import AnimatedWindow

        return AnimatedWindow

    @property
    def App(self):
        from Classes.App import App

        return App

    @property
    def AutostartItem(self):
        from Classes.AutostartItem import AutostartItem

        return AutostartItem

    @property
    def BoxedGroup(self):
        from Classes.BoxedGroup import BoxedGroup

        return BoxedGroup

    @property
    def ButtonRow(self):
        from Classes.ButtonRow import ButtonRow

        return ButtonRow

    @property
    def CheckBoxGrid(self):
        from Classes.CheckBoxGrid import CheckBoxGrid

        return CheckBoxGrid

    @property
    def CheckUpdate(self):
        from Classes.CheckUpdate import CheckUpdate

        return CheckUpdate

    @property
    def Choice(self):
        from Classes.Choice import Choice

        return Choice

    @property
    def Colour(self):
        from Classes.Colour import Colour

        return Colour

    @property
    def ColourSelectButton(self):
        from Classes.ColourSelectButton import ColourSelectButton

        return ColourSelectButton

    @property
    def Config(self):
        from Classes.Config import Config

        return Config

    @property
    def ConfigDialog(self):
        from Classes.ConfigDialog import ConfigDialog

        return ConfigDialog

    @property
    def ConfigPanel(self):
        from Classes.ConfigPanel import ConfigPanel

        return ConfigPanel

    @property
    def ContainerItem(self):
        from Classes.ContainerItem import ContainerItem

        return ContainerItem

    @property
    def ControlProviderMixin(self):
        from Classes.ControlProviderMixin import ControlProviderMixin

        return ControlProviderMixin

    @property
    def Dialog(self):
        from Classes.Dialog import Dialog

        return Dialog

    @property
    def DigitOnlyValidator(self):
        from Classes.DigitOnlyValidator import DigitOnlyValidator

        return DigitOnlyValidator

    @property
    def DirBrowseButton(self):
        from Classes.DirBrowseButton import DirBrowseButton

        return DirBrowseButton

    @property
    def DisplayChoice(self):
        from Classes.DisplayChoice import DisplayChoice

        return DisplayChoice

    @property
    def Document(self):
        from Classes.Document import Document

        return Document

    @property
    def Environment(self):
        from Classes.Environment import Environment

        return Environment

    @property
    def EventGhostEvent(self):
        from Classes.EventGhostEvent import EventGhostEvent

        return EventGhostEvent

    @property
    def EventItem(self):
        from Classes.EventItem import EventItem

        return EventItem

    @property
    def EventRemapDialog(self):
        from Classes.EventRemapDialog import EventRemapDialog

        return EventRemapDialog

    @property
    def EventThread(self):
        from Classes.EventThread import EventThread

        return EventThread

    @property
    def Exceptions(self):
        from Classes.Exceptions import Exceptions

        return Exceptions

    @property
    def ExceptionsProvider(self):
        from Classes.ExceptionsProvider import ExceptionsProvider

        return ExceptionsProvider

    @property
    def ExportDialog(self):
        from Classes.ExportDialog import ExportDialog

        return ExportDialog

    @property
    def FileBrowseButton(self):
        from Classes.FileBrowseButton import FileBrowseButton

        return FileBrowseButton

    @property
    def FindDialog(self):
        from Classes.FindDialog import FindDialog

        return FindDialog

    @property
    def FolderItem(self):
        from Classes.FolderItem import FolderItem

        return FolderItem

    @property
    def FolderPath(self):
        from Classes.FolderPath import FolderPath

        return FolderPath

    @property
    def FontSelectButton(self):
        from Classes.FontSelectButton import FontSelectButton

        return FontSelectButton

    @property
    def HeaderBox(self):
        from Classes.HeaderBox import HeaderBox

        return HeaderBox

    @property
    def HtmlDialog(self):
        from Classes.HtmlDialog import HtmlDialog

        return HtmlDialog

    @property
    def HtmlWindow(self):
        from Classes.HtmlWindow import HtmlWindow

        return HtmlWindow

    @property
    def HyperLinkCtrl(self):
        from Classes.HyperLinkCtrl import HyperLinkCtrl

        return HyperLinkCtrl

    @property
    def ImagePicker(self):
        from Classes.ImagePicker import ImagePicker

        return ImagePicker

    @property
    def IrDecoderPlugin(self):
        from Classes.IrDecoderPlugin import IrDecoderPlugin

        return IrDecoderPlugin

    @property
    def LanguageEditor(self):
        from Classes.LanguageEditor import LanguageEditor

        return LanguageEditor

    @property
    def License(self):
        from Classes.License import License

        return License

    @property
    def Log(self):
        from Classes.Log import Log

        return Log

    @property
    def MacroItem(self):
        from Classes.MacroItem import MacroItem

        return MacroItem

    @property
    def MacroSelectButton(self):
        from Classes.MacroSelectButton import MacroSelectButton

        return MacroSelectButton

    @property
    def MainMessageReceiver(self):
        from Classes.MainMessageReceiver import MainMessageReceiver

        return MainMessageReceiver

    @property
    def MessageDialog(self):
        from Classes.MessageDialog import MessageDialog

        return MessageDialog

    @property
    def MessageReceiver(self):
        from Classes.MessageReceiver import MessageReceiver

        return MessageReceiver

    @property
    def MonitorsCtrl(self):
        from Classes.MonitorsCtrl import MonitorsCtrl

        return MonitorsCtrl

    @property
    def NamespaceTree(self):
        from Classes.NamespaceTree import NamespaceTree

        return NamespaceTree

    @property
    def NetworkSend(self):
        from Classes.NetworkSend import NetworkSend

        return NetworkSend

    @property
    def OptionsDialog(self):
        from Classes.OptionsDialog import OptionsDialog

        return OptionsDialog

    @property
    def Panel(self):
        from Classes.Panel import Panel

        return Panel

    @property
    def Password(self):
        from Classes.Password import Password

        return Password

    @property
    def PasswordCtrl(self):
        from Classes.PasswordCtrl import PasswordCtrl

        return PasswordCtrl

    @property
    def PersistentData(self):
        from Classes.PersistentData import PersistentData

        return PersistentData

    @property
    def PluginBase(self):
        from Classes.PluginBase import PluginBase

        return PluginBase

    @property
    def PluginInstall(self):
        from Classes.PluginInstall import PluginInstall

        return PluginInstall

    @property
    def PluginInstanceInfo(self):
        from Classes.PluginInstanceInfo import PluginInstanceInfo

        return PluginInstanceInfo

    @property
    def PluginItem(self):
        from Classes.PluginItem import PluginItem

        return PluginItem

    @property
    def PluginManager(self):
        from Classes.PluginManager import PluginManager

        return PluginManager

    @property
    def PluginMetaClass(self):
        from Classes.PluginMetaClass import PluginMetaClass

        return PluginMetaClass

    @property
    def PluginModuleInfo(self):
        from Classes.PluginModuleInfo import PluginModuleInfo

        return PluginModuleInfo

    @property
    def PythonEditorCtrl(self):
        from Classes.PythonEditorCtrl import PythonEditorCtrl

        return PythonEditorCtrl

    @property
    def RadioBox(self):
        from Classes.RadioBox import RadioBox

        return RadioBox

    @property
    def RadioButtonGrid(self):
        from Classes.RadioButtonGrid import RadioButtonGrid

        return RadioButtonGrid

    @property
    def RawReceiverPlugin(self):
        from Classes.RawReceiverPlugin import RawReceiverPlugin

        return RawReceiverPlugin

    @property
    def ResettableTimer(self):
        from Classes.ResettableTimer import ResettableTimer

        return ResettableTimer

    @property
    def RootItem(self):
        from Classes.RootItem import RootItem

        return RootItem

    @property
    def Scheduler(self):
        from Classes.Scheduler import Scheduler

        return Scheduler

    @property
    def SerialPort(self):
        from Classes.SerialPort import SerialPort

        return SerialPort

    @property
    def SerialPortChoice(self):
        from Classes.SerialPortChoice import SerialPortChoice

        return SerialPortChoice

    @property
    def SerialThread(self):
        from Classes.SerialThread import SerialThread

        return SerialThread

    @property
    def Shortcut(self):
        from Classes.Shortcut import Shortcut

        return Shortcut

    @property
    def SimpleInputDialog(self):
        from Classes.SimpleInputDialog import SimpleInputDialog

        return SimpleInputDialog

    @property
    def SizeGrip(self):
        from Classes.SizeGrip import SizeGrip

        return SizeGrip

    @property
    def Slider(self):
        from Classes.Slider import Slider

        return Slider

    @property
    def SmartSpinIntCtrl(self):
        from Classes.SmartSpinIntCtrl import SmartSpinIntCtrl

        return SmartSpinIntCtrl

    @property
    def SmartSpinNumCtrl(self):
        from Classes.SmartSpinNumCtrl import SmartSpinNumCtrl

        return SmartSpinNumCtrl

    @property
    def SoundMixerTree(self):
        from Classes.SoundMixerTree import SoundMixerTree

        return SoundMixerTree

    @property
    def SpinIntCtrl(self):
        from Classes.SpinIntCtrl import SpinIntCtrl

        return SpinIntCtrl

    @property
    def SpinNumCtrl(self):
        from Classes.SpinNumCtrl import SpinNumCtrl

        return SpinNumCtrl

    @property
    def StaticTextBox(self):
        from Classes.StaticTextBox import StaticTextBox

        return StaticTextBox

    @property
    def StdLib(self):
        from Classes.StdLib import StdLib

        return StdLib

    @property
    def TaskBarIcon(self):
        from Classes.TaskBarIcon import TaskBarIcon

        return TaskBarIcon

    @property
    def Tasklet(self):
        from Classes.Tasklet import Tasklet

        return Tasklet

    @property
    def TaskletDialog(self):
        from Classes.TaskletDialog import TaskletDialog

        return TaskletDialog

    @property
    def Text(self):
        from Classes.Text import Text

        return Text

    @property
    def Theme(self):
        from Classes.Theme import Theme

        return Theme

    @property
    def ThreadWorker(self):
        from Classes.ThreadWorker import ThreadWorker

        return ThreadWorker

    @property
    def TimeCtrl(self):
        from Classes.TimeCtrl import TimeCtrl

        return TimeCtrl

    @property
    def TimeCtrl_Duration(self):
        from Classes.TimeCtrl_Duration import TimeCtrl_Duration

        return TimeCtrl_Duration

    @property
    def TransferDialog(self):
        from Classes.TransferDialog import TransferDialog

        return TransferDialog

    @property
    def TranslatableStrings(self):
        from Classes.TranslatableStrings import TranslatableStrings

        return TranslatableStrings

    @property
    def Translation(self):
        from Classes.Translation import Translation

        return Translation

    @property
    def TreeItem(self):
        from Classes.TreeItem import TreeItem

        return TreeItem

    @property
    def TreeItemBrowseCtrl(self):
        from Classes.TreeItemBrowseCtrl import TreeItemBrowseCtrl

        return TreeItemBrowseCtrl

    @property
    def TreeItemBrowseDialog(self):
        from Classes.TreeItemBrowseDialog import TreeItemBrowseDialog

        return TreeItemBrowseDialog

    @property
    def TreeLink(self):
        from Classes.TreeLink import TreeLink

        return TreeLink

    @property
    def TreePosition(self):
        from Classes.TreePosition import TreePosition

        return TreePosition

    @property
    def Version(self):
        from Classes.Version import Version

        return Version

    @property
    def WindowDragFinder(self):
        from Classes.WindowDragFinder import WindowDragFinder

        return WindowDragFinder

    @property
    def WindowList(self):
        from Classes.WindowList import WindowList

        return WindowList

    @property
    def WindowMatcher(self):
        from Classes.WindowMatcher import WindowMatcher

        return WindowMatcher

    @property
    def WindowsVersion(self):
        return WindowsVersion

    @property
    def WindowTree(self):
        from Classes.WindowTree import WindowTree

        return WindowTree

    @property
    def WinUsb(self):
        from Classes.WinUsb import WinUsb

        return WinUsb

    @property
    def WinUsbRemote(self):
        from Classes.WinUsbRemote import WinUsbRemote

        return WinUsbRemote

    @property
    def MainFrame(self):
        from Classes.MainFrame import MainFrame

        return MainFrame

    @property
    def UndoHandler(self):
        from Classes.UndoHandler import UndoHandler

        return UndoHandler

    @property
    def Bunch(self):
        from Utils import Bunch

        return Bunch

    @property
    def NotificationHandler(self):
        from Utils import NotificationHandler

        return NotificationHandler

    @property
    def LogIt(self):
        from Utils import LogIt

        return LogIt

    @property
    def LogItWithReturn(self):
        from Utils import LogItWithReturn

        return LogItWithReturn

    @property
    def TimeIt(self):
        from Utils import TimeIt

        return TimeIt

    @property
    def AssertInMainThread(self):
        from Utils import AssertInMainThread

        return AssertInMainThread

    @property
    def AssertInActionThread(self):
        from Utils import AssertInActionThread

        return AssertInActionThread

    @property
    def ParseString(self):
        from Utils import ParseString

        return ParseString

    @property
    def SetDefault(self):
        from Utils import SetDefault

        return SetDefault

    @property
    def EnsureVisible(self):
        from Utils import EnsureVisible

        return EnsureVisible

    @property
    def VBoxSizer(self):
        from Utils import VBoxSizer

        return VBoxSizer

    @property
    def HBoxSizer(self):
        from Utils import HBoxSizer

        return HBoxSizer

    @property
    def EqualizeWidths(self):
        from Utils import EqualizeWidths

        return EqualizeWidths

    @property
    def AsTasklet(self):
        from Utils import AsTasklet

        return AsTasklet

    @property
    def ExecFile(self):
        from Utils import ExecFile

        return ExecFile

    @property
    def GetTopLevelWindow(self):
        from Utils import GetTopLevelWindow

        return GetTopLevelWindow

    @property
    def GetClosestLanguage(self):
        from Utils import GetClosestLanguage

        return GetClosestLanguage

    def __init__(self):
        mod = sys.modules[__name__]

        self.__file__ = mod.__file__
        self.__package__ = mod.__package__
        self.__name__ = mod.__name__
        self.__doc__ = mod.__doc__
        self.__module__ = mod.__module__
        self.__orignal_module__ = mod
        sys.modules[__name__] = self

        import __builtin__
        __builtin__.eg = self

        self.__actionGroup = None
        self.__globals = None
        self.__plugins = None
        self.__messageReceiver = None
        self.__app = None
        self.__log = None
        self.__config = None
        self.__colour = None
        self.__text = None
        self.__actionThread = None
        self.__eventThread = None
        self.__pluginManager = None
        self.__scheduler = None
        self.__SendKeys = None
        self.__taskBarIcon = None
        self.__folderPath = None
        self.__localPluginDir = None
        self.__CorePluginModule = None
        self.__UserPluginModule = None

    def __repr__(self):
        return "<dynamic-module '%s'>" % self.__name__

    def RaiseAssignments(self):
        """
        After this method is called, creation of new attributes will raise
        AttributeError.

        This is meanly used to find unintended assignments while debugging.
        """
        def __setattr__(self, name, value):
            if name not in self.__dict__:
                try:
                    raise AttributeError(
                        "Assignment to new attribute %s" % name
                    )
                except AttributeError:
                    import traceback
                    eg.PrintWarningNotice(traceback.format_exc())

            object.__setattr__(self, name, value)
        self.__class__.__setattr__ = __setattr__

    def Shutdown(self):
        self.PrintDebugNotice("stopping threads")
        self.actionThread.Func(self.actionThread.StopSession)()
        self.scheduler.Stop()
        self.actionThread.Stop()
        self.eventThread.Stop()
        self.socketSever.Stop()

        self.PrintDebugNotice("shutting down")
        self.config.Save()
        self.messageReceiver.Stop()
        if self.dummyAsyncoreDispatcher:
            self.dummyAsyncoreDispatcher.close()

    def Main(self):

        import WinApi.pywin32_patches  # NOQA
        import WinApi.wx_patches  # NOQA
        import WinApi.GenPaths  # NOQA

        if not os.path.exists(self.configDir):
            try:
                os.makedirs(self.configDir)
            except:
                pass

        if not os.path.exists(self.localPluginDir):
            try:
                os.makedirs(self.localPluginDir)
            except:
                self.__localPluginDir = self.corePluginDir

        if Cli.args.isMain:
            if os.path.exists(eg.configDir):
                os.chdir(self.configDir)
            else:
                os.chdir(self.mainDir)

        if Cli.args.install:
            return
        if Cli.args.translate:
            from Classes.LanguageEditor import LanguageEditor
            LanguageEditor()
        elif Cli.args.pluginFile:
            from Classes.PluginInstall import PluginInstall

            PluginInstall.Import(Cli.args.pluginFile)
            return
        else:
            # replace builtin input() with a small dialog
            def Input(prompt=None):
                from Classes.SimpleInputDialog import SimpleInputDialog

                return eval(SimpleInputDialog.RawInput(prompt))

            # replace builtin raw_input() with a small dialog
            def RawInput(prompt=None):
                from Classes.SimpleInputDialog import SimpleInputDialog
                return SimpleInputDialog.RawInput(prompt)

            __builtin__.raw_input = RawInput
            __builtin__.input = Input

            self.scheduler.start()
            self.messageReceiver.Start()

            from Classes.Document import Document
            self.document = Document()

            if self.config.showTrayIcon:
                if not (
                    self.config.hideOnStartup or
                    self.startupArguments.hideOnStartup
                ):
                    self.document.ShowFrame()
            else:
                self.document.ShowFrame()
                if (
                    self.config.hideOnStartup or
                    self.startupArguments.hideOnStartup
                ):
                    self.mainFrame.Iconize(True)

            self.actionThread.Start()

            self.eventThread.startupEvent = self.startupArguments.startupEvent

            config = self.config
            startupFile = self.startupArguments.startupFile
            if startupFile is None:
                startupFile = config.autoloadFilePath
            if startupFile and not os.path.exists(startupFile):
                self.PrintError(self.text.Error.FileNotFound % startupFile)
                startupFile = None

            self.eventThread.Start()
            wx.CallAfter(
                self.eventThread.Call,
                self.eventThread.StartSession,
                startupFile
            )

            if config.checkUpdate:
                from time import gmtime

                # avoid more than one check per day
                today = gmtime()[:3]
                if config.lastUpdateCheckDate != today:
                    from Classes.CheckUpdate import CheckUpdate

                    config.lastUpdateCheckDate = today
                    wx.CallAfter(CheckUpdate.Start)

            # Register restart handler for easy crash recovery.
            if self.WindowsVersion >= 'Vista':
                from ctypes import windll

                args = " ".join(self.app.GetArguments())
                windll.kernel32.RegisterApplicationRestart(args, 8)

            self.Print(self.text.MainFrame.Logger.welcomeText)

            import LoopbackSocket

            self.__socketSever = LoopbackSocket.Start()

        if self.debugLevel:
            try:
                ImportAll()
            except:
                self.PrintDebugNotice(sys.exc_info()[1])

        from Classes.Tasklet import Tasklet
        Tasklet(self.app.MainLoop)().run()
        stackless.run()


eg = DynamicModule()


def ImportAll():
    def Traverse(root, moduleRoot):
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name = os.path.basename(path)
                if name in [".svn", ".git", ".idea"]:
                    continue
                if not os.path.exists(os.path.join(path, "__init__.py")):
                    continue
                moduleName = moduleRoot + "." + name
                # print moduleName
                __import__(moduleName)
                Traverse(path, moduleName)
                continue
            base, ext = os.path.splitext(name)
            if ext != ".py":
                continue
            if base == "__init__":
                continue
            moduleName = moduleRoot + "." + base
            if moduleName in (
                "eg.StaticImports",
                "eg.CorePluginModule.EventGhost.OsdSkins.Default",
            ):
                continue
            # print moduleName
            __import__(moduleName)

    Traverse(os.path.join(eg.mainDir, "eg"), "eg")
    Traverse(eg.corePluginDir, "eg.CorePluginModule")

# This is only here to make pylint happy. It is never really imported

if 'MAKES_IDE_HAPPY' in os.environ:
    def RaiseAssignments():
        pass

    ImportAll()

    from StaticImports import *  # NOQA

    APP_NAME = eg.APP_NAME
    useTreeItemGUID = eg.useTreeItemGUID
    CORE_PLUGIN_GUIDS = eg.CORE_PLUGIN_GUIDS

    import LoopbackSocket

    import Icons

    socketSever = LoopbackSocket.Start()
    ID_TEST = eg.ID_TEST
    revision = eg.revision
    startupArguments = eg.startupArguments
    systemEncoding = eg.systemEncoding
    mainFrame = MainFrame()
    result = eg.result
    plugins = Bunch()
    globals = Bunch()
    globals.eg = eg
    event = eg.event
    eventTable = eg.eventTable
    eventString = eg.eventString
    notificationHandlers = eg.notificationHandlers
    programCounter = eg.programCounter
    programReturnStack = eg.programReturnStack
    indent = eg.indent
    pluginList = Bunch()
    mainThread = eg.mainThread
    stopExecutionFlag = eg.stopExecutionFlag
    lastFoundWindows = eg.lastFoundWindows
    currentItem = eg.currentItem
    actionGroup = Bunch()
    actionGroup.items = []
    GUID = GUID()


    def CommandEvent():
        pass


    class Exception(Exception):
        pass


    class StopException(Exception):
        pass


    class HiddenAction:
        pass


    def Bind(notification, listener):
        pass

    def CallWait(func, *args, **kwargs):
        pass

    def DummyFunc(*dummyArgs, **dummyKwargs):
        pass

    def Exit():
        pass

    def HasActiveHandler(eventstring):
        pass

    def MessageBox(message, caption=eg.APP_NAME, style=wx.OK, parent=None):
        pass

    def Notify(notification, value=None):
        pass

    def RegisterPlugin(
        name=None,
        description=None,
        kind="other",
        author="[unknown author]",
        version="[unknown version]",
        icon=None,
        canMultiLoad=False,
        createMacrosOnAdd=False,
        url=None,
        help=None,
        guid=None,
        **kwargs
    ):
        pass

    def RestartAsyncore():
        pass

    def RunProgram():
        pass

    def StopMacro(ignoreReturn=False):
        pass

    ValueChangedEvent = eg.ValueChangedEvent
    EVT_VALUE_CHANGED = eg.EVT_VALUE_CHANGED

    pyCrustFrame = eg.pyCrustFrame
    dummyAsyncoreDispatcher = eg.dummyAsyncoreDispatcher
    processId = eg.processId
    messageReceiver = MainMessageReceiver()
    app = App()
    log = Log()


    def Print(*args, **kwargs):
        pass

    def PrintDebugNotice(*args):
        pass

    def PrintWarningNotice(*args):
        pass

    def PrintError(*args, **kwargs):
        pass

    def PrintNotice(*args, **kwargs):
        pass

    def PrintStack(skip=0):
        pass

    def PrintTraceback(msg=None, skip=0, source=None, excInfo=None):
        pass


    config = Config()
    debugLevel = config.logDebug
    colour = Colour()
    text = Text('en_US')
    actionThread = ActionThread()
    eventThread = EventThread()
    pluginManager = PluginManager()
    scheduler = Scheduler()


    def TriggerEvent(
        suffix,
        payload=None,
        prefix="Main",
        source=eg
    ):
        pass


    def TriggerEnduringEvent(
        suffix,
        payload=None,
        prefix="Main",
        source=eg
    ):
        pass

    from WinApi.SendKeys import SendKeysParser
    SendKeys = SendKeysParser()

    PluginClass = PluginBase
    ActionClass = ActionBase
    taskBarIcon = TaskBarIcon(False)

    def SetProcessingState(state, event):
        pass

    wit = False
    document = Document()
    folderPath = FolderPath()
    mainDir = ''
    configDir = ''
    corePluginDir = ''
    localPluginDir = ''
    imagesDir = ''
    languagesDir = ''
    sitePackagesDir = ''
    pluginDirs = []
    cFunctions = None
    CorePluginModule = None
    UserPluginModule = None

if eg.debugLevel:
    eg.RaiseAssignments()
