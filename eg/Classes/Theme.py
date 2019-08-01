# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2018 EventGhost Project <http://eventghost.net/>
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

import eg
import os
import zipfile
import inspect
import sys
import wx
import wx.lib.agw.supertooltip
import wx.lib.agw.customtreectrl
import wx.lib.agw.balloontip
import wx.lib.buttons
import wx.lib.agw.shapedbutton
import wx.lib.agw.aquabutton
import wx.lib.agw.gradientbutton
import wx.aui
import wx.lib.agw.aui




THEME_TEMPLATE = '''\
class {name}:
    class Colours:
{colours}

    class Fonts:
{fonts}

'''


def get_colour(colour_id):
    return wx.SystemSettings.GetColour(colour_id).Get()


def get_system_font():
    return wx.SystemSettings.GetFont(
        wx.SYS_DEFAULT_GUI_FONT
    ).GetNativeFontInfo().ToString()



class DefaultTheme:
    def __init__(self, name):
        self.__name__ = name

        class Fonts:
            FONT_TREE = get_system_font()
            FONT_LOG = get_system_font()
            FONT_TOOLTIP = get_system_font()
            FONT_MENUBAR = get_system_font()
            FONT_MENU = get_system_font()
            FONT_WINDOW = get_system_font()
            FONT_BUTTON = get_system_font()
            FONT_LISTBOX = get_system_font()
            FONT_CAPTION = get_system_font()


        class Colours:
            COLOUR_TREE = get_colour(wx.SYS_COLOUR_WINDOW)
            COLOUR_TREETEXT = get_colour(wx.SYS_COLOUR_WINDOWTEXT)
            COLOUR_LOG = get_colour(wx.SYS_COLOUR_WINDOW)
            COLOUR_LOGTEXT = get_colour(wx.SYS_COLOUR_WINDOWTEXT)
            COLOUR_LOGERROR = eg.Colour.errorBackground
            COLOUR_LOGERRORTEXT = eg.Colour.errorText
            COLOUR_LOGWARNING = eg.Colour.waningBackground
            COLOUR_LOGWARNINGTEXT = eg.Colour.warningText
            COLOUR_LOGDEBUG = eg.Colour.debugBackground
            COLOUR_LOGDEBUGTEXT = eg.Colour.debugText
            COLOUR_TOOLTIPTEXT = get_colour(wx.SYS_COLOUR_INFOTEXT)
            COLOUR_TOOLTIP = get_colour(wx.SYS_COLOUR_INFOBK)
            COLOUR_MENUBAR = get_colour(wx.SYS_COLOUR_MENUBAR)
            COLOUR_MENUBARTEXT = get_colour(wx.SYS_COLOUR_MENUTEXT)
            COLOUR_MENU = get_colour(wx.SYS_COLOUR_MENU)
            COLOUR_MENUTEXT = get_colour(wx.SYS_COLOUR_MENUTEXT)
            COLOUR_WINDOW = get_colour(wx.SYS_COLOUR_WINDOW)
            COLOUR_WINDOWTEXT = get_colour(wx.SYS_COLOUR_WINDOWTEXT)
            COLOUR_BUTTON = get_colour(wx.SYS_COLOUR_BTNFACE)
            COLOUR_BUTTONTEXT = get_colour(wx.SYS_COLOUR_BTNTEXT)
            COLOUR_LISTBOXTEXT = get_colour(wx.SYS_COLOUR_LISTBOXTEXT)
            COLOUR_LISTBOX = get_colour(wx.SYS_COLOUR_LISTBOX)
            COLOUR_ACTIVECAPTIONTEXT = get_colour(wx.SYS_COLOUR_CAPTIONTEXT)
            COLOUR_ACTIVECAPTION = get_colour(wx.SYS_COLOUR_ACTIVECAPTION)
            COLOUR_INACTIVECAPTION = get_colour(wx.SYS_COLOUR_INACTIVECAPTION)
            COLOUR_INACTIVECAPTIONTEXT = get_colour(wx.SYS_COLOUR_INACTIVECAPTIONTEXT)
            COLOUR_GRADIENTACTIVECAPTION = get_colour(
                wx.SYS_COLOUR_GRADIENTACTIVECAPTION
            )
            COLOUR_GRADIENTINACTIVECAPTION = get_colour(
                wx.SYS_COLOUR_GRADIENTINACTIVECAPTION
            )

        self.Fonts = Fonts
        self.Colours = Colours

DarkTheme = DefaultTheme('TestTheme')


DarkTheme.Colours.COLOUR_WINDOW = (60, 60, 60)
DarkTheme.Colours.COLOUR_WINDOWTEXT = (220, 220, 220)

DarkTheme.Colours.COLOUR_LOG = (60, 60, 60)
DarkTheme.Colours.COLOUR_LOGTEXT = (220, 220, 220)

DarkTheme.Colours.COLOUR_TREE = (60, 60, 60)
DarkTheme.Colours.COLOUR_TREETEXT = (220, 220, 220)

DarkTheme.Colours.COLOUR_BUTTON = (0, 0, 0)
DarkTheme.Colours.COLOUR_BUTTONTEXT = (220, 220, 220)

DarkTheme.Colours.COLOUR_ACTIVECAPTIONTEXT = (0, 255, 0)
DarkTheme.Colours.COLOUR_ACTIVECAPTION = (0, 0, 0)
DarkTheme.Colours.COLOUR_GRADIENTACTIVECAPTION = (0, 255, 0)

DarkTheme.Colours.COLOUR_INACTIVECAPTION = (0, 255, 0)
DarkTheme.Colours.COLOUR_INACTIVECAPTIONTEXT = (0, 0, 0)
DarkTheme.Colours.COLOUR_GRADIENTINACTIVECAPTION = (0, 0, 0)

DarkTheme.Colours.COLOUR_MENUBAR = (0, 0, 0)
DarkTheme.Colours.COLOUR_MENUBARTEXT = (0, 255, 0)
DarkTheme.Colours.COLOUR_MENU = (0, 0, 0)
DarkTheme.Colours.COLOUR_MENUTEXT = (0, 255, 0)


class CurrentThemes(eg.PersistentData):
    BaseTheme = DefaultTheme('DefaultTheme')
    DarkTheme = DarkTheme
    ActiveTheme = BaseTheme


class Theme(object):

    def __init__(self):
        self.active_widgets = []
        self.__changed_classes = []

    def on_destroy(self, evt):
        obj = evt.GetEventObject()

        if obj in self.active_widgets:
            self.active_widgets.remove(obj)

        evt.Skip()

    def handle_item(self, item):

        try:
            if isinstance(item, eg.HeaderBox):
                text = item.text

                text = text.replace(
                    'bgcolor="' + item.GetBackgroundColour().GetAsString(
                        wx.C2S_HTML_SYNTAX),
                    'bgcolor="' + self.window_colour.GetAsString(
                        wx.C2S_HTML_SYNTAX)
                )

                text = text.replace(
                    'text="' + item.GetForegroundColour().GetAsString(
                        wx.C2S_HTML_SYNTAX),
                    'text="' + self.window_text_colour.GetAsString(
                        wx.C2S_HTML_SYNTAX)
                )
                item.text = text

            if eg.mainFrame is not None and item == eg.mainFrame.logCtrl:
                from .MainFrame.LogCtrl import _create_colour_attributes

                item.SetFont(self.log_font)
                item.SetBackgroundColour(self.log_colour)

                eg.mainFrame.logCtrl.logColours = _create_colour_attributes(
                    self.log_text_colour,
                    self.log_colour
                )
                eg.mainFrame.logCtrl.errorColours = _create_colour_attributes(
                    self.log_error_text_colour,
                    self.log_error_colour
                )
                eg.mainFrame.logCtrl.warningColours = _create_colour_attributes(
                    self.log_warning_text_colour,
                    self.log_warning_colour
                )
                eg.mainFrame.logCtrl.debugColours = _create_colour_attributes(
                    self.log_debug_text_colour,
                    self.log_debug_colour
                )

            elif isinstance(item, (
                wx.CheckListBox,
                wx.ComboBox,
                wx.Choice,
                wx.ListBox,
                wx.VListBox,
                wx.ListCtrl
            )):
                item.SetFont(self.listbox_font)
                item.SetBackgroundColour(self.listbox_colour)
                item.SetForegroundColour(self.listbox_text_colour)

            elif isinstance(item, wx.MenuItem):
                item.SetBackgroundColour(self.menu_colour)

                item.SetFont(self.menu_font)

            elif isinstance(item, wx.MenuBar):
                item.SetBackgroundColour(self.menubar_colour)
                item.SetForegroundColour(self.menubar_text_colour)
                item.SetFont(self.menubar_font)

            elif isinstance(item, (
                wx.lib.agw.supertooltip.SuperToolTip,
                wx.TipWindow,
                wx.ToolTip
            )):
                item.SetBackgroundColour(self.tooltip_colour)
                item.SetForegroundColour(self.tooltip_text_colour)
                item.SetFont(self.tooltip_font)

            elif isinstance(item, wx.lib.agw.balloontip.BalloonTip):
                tooltip_bold_font = wx.FontFromNativeInfoString(self.theme.Fonts.FONT_TOOLTIP)
                tooltip_bold_font.SetWeight(wx.FONTFLAG_BOLD)

                item.SetBalloonColour(self.tooltip_colour)
                item.SetTitleFont(tooltip_bold_font)
                item.SetMessageFont(self.tooltip_font)
                item.SetTitleColour(self.tooltip_text_colour)
                item.SetMessageColour(self.tooltip_text_colour)

            elif isinstance(item, (
                wx.TreeCtrl,
                wx.lib.agw.customtreectrl.CustomTreeCtrl
            )):
                item.SetBackgroundColour(self.tree_colour)
                item.SetForegroundColour(self.tree_text_colour)
                item.SetFont(self.tree_font)

            elif isinstance(item, (
                wx.Button,
                wx.ToggleButton,
                wx.lib.agw.aquabutton.AquaButton,
                wx.lib.agw.aquabutton.AquaToggleButton,
                wx.lib.agw.gradientbutton.GradientButton,
                wx.lib.agw.shapedbutton.SBitmapTextButton,
                wx.lib.agw.shapedbutton.SBitmapTextToggleButton,
                wx.lib.buttons.GenBitmapTextButton,
                wx.lib.buttons.GenBitmapTextToggleButton,
            )):
                item.SetBackgroundColour(self.button_colour)
                item.SetForegroundColour(self.button_text_colour)
                item.SetFont(self.button_font)

            elif isinstance(item, (
                wx.lib.agw.shapedbutton.SBitmapButton,
                wx.lib.agw.shapedbutton.SBitmapToggleButton,
                wx.lib.buttons.GenBitmapButton,
                wx.lib.buttons.GenToggleButton,
                wx.lib.buttons.GenBitmapToggleButton
            )):
                item.SetBackgroundColour(self.button_colour)

            elif isinstance(item, (wx.lib.agw.aui.AuiManager, wx.aui.AuiManager)):

                ap = item.GetArtProvider()
                ap.SetColor(wx.aui.AUI_DOCKART_BACKGROUND_COLOUR, self.window_colour)
                ap.SetColor(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_COLOUR,
                    self.active_caption_colour)
                ap.SetColor(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR,
                    self.active_caption_gradient_colour)
                ap.SetColor(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR,
                    self.active_caption_text_colour)
                ap.SetColor(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR,
                    self.inactive_caption_colour)
                ap.SetColor(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR,
                    self.inactive_caption_gradient_colour)
                ap.SetColor(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR,
                    self.inactive_caption_text_colour)
                ap.SetFont(wx.aui.AUI_DOCKART_CAPTION_FONT, self.caption_font)

            else:
                try:
                    item.SetFont(self.window_font)
                except AttributeError:
                    pass

                try:
                    item.SetBackgroundColour(self.window_colour)
                except AttributeError:
                    pass

                try:
                    item.SetForegroundColour(self.window_text_colour)
                except AttributeError:
                    pass

            try:
                item.Refresh()
                item.Update()
            except AttributeError:
                pass
        except wx.PyDeadObjectError:
            self.active_widgets.remove(item)

    def set_theme(self, theme):
        self.theme = theme

        self.tree_colour = wx.Colour(*theme.Colours.COLOUR_TREE)
        self.tree_text_colour = wx.Colour(*theme.Colours.COLOUR_TREETEXT)

        self.log_colour = wx.Colour(*theme.Colours.COLOUR_LOG)
        self.log_text_colour = wx.Colour(*theme.Colours.COLOUR_LOGTEXT)
        self.log_error_colour = wx.Colour(*theme.Colours.COLOUR_LOGERROR)
        self.log_error_text_colour = wx.Colour(*theme.Colours.COLOUR_LOGERRORTEXT)
        self.log_warning_colour = wx.Colour(*theme.Colours.COLOUR_LOGWARNING)
        self.log_warning_text_colour = wx.Colour(*theme.Colours.COLOUR_LOGWARNINGTEXT)
        self.log_debug_colour = wx.Colour(*theme.Colours.COLOUR_LOGDEBUG)
        self.log_debug_text_colour = wx.Colour(*theme.Colours.COLOUR_LOGDEBUGTEXT)

        self.window_colour = wx.Colour(*theme.Colours.COLOUR_WINDOW)
        self.window_text_colour = wx.Colour(*theme.Colours.COLOUR_WINDOWTEXT)

        self.button_colour = wx.Colour(*theme.Colours.COLOUR_BUTTON)
        self.button_text_colour = wx.Colour(*theme.Colours.COLOUR_BUTTONTEXT)

        self.listbox_colour = wx.Colour(*theme.Colours.COLOUR_LISTBOX)
        self.listbox_text_colour = wx.Colour(*theme.Colours.COLOUR_LISTBOXTEXT)

        self.menu_colour = wx.Colour(*theme.Colours.COLOUR_MENU)
        self.menu_text_colour = wx.Colour(*theme.Colours.COLOUR_MENUTEXT)

        self.menubar_colour = wx.Colour(*theme.Colours.COLOUR_MENUBAR)
        self.menubar_text_colour = wx.Colour(*theme.Colours.COLOUR_MENUBARTEXT)

        self.tooltip_colour = wx.Colour(*theme.Colours.COLOUR_TOOLTIP)
        self.tooltip_text_colour = wx.Colour(*theme.Colours.COLOUR_TOOLTIPTEXT)

        self.active_caption_colour = wx.Colour(*theme.Colours.COLOUR_ACTIVECAPTION)
        self.active_caption_gradient_colour = wx.Colour(*theme.Colours.COLOUR_GRADIENTACTIVECAPTION)
        self.active_caption_text_colour = wx.Colour(*theme.Colours.COLOUR_ACTIVECAPTIONTEXT)

        self.inactive_caption_text_colour = wx.Colour(*theme.Colours.COLOUR_INACTIVECAPTIONTEXT)
        self.inactive_caption_colour = wx.Colour(*theme.Colours.COLOUR_INACTIVECAPTION)
        self.inactive_caption_gradient_colour = wx.Colour(*theme.Colours.COLOUR_GRADIENTINACTIVECAPTION)

        self.tree_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_TREE)
        self.log_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_LOG)
        self.window_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_WINDOW)
        self.button_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_BUTTON)
        self.listbox_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_LISTBOX)
        self.caption_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_CAPTION)
        self.menu_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_MENU)
        self.menubar_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_MENUBAR)
        self.tooltip_font = wx.FontFromNativeInfoString(theme.Fonts.FONT_TOOLTIP)

        for item in self.active_widgets:
            self.handle_item(item)

    def stop(self):
        for patched_cls in self.__changed_classes:
            # mod = patched_cls.__original_module__
            # cls = patched_cls.__original_class__
            # setattr(mod, cls.__name__, cls)
            patched_cls.__init__ = patched_cls.__original_init__

        del self.__changed_classes[:]

    def modify_class(self, cls):

        def __init__(instance, *args, **kwargs):
            instance.__original_init__(*args, **kwargs)
            try:
                instance.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)
            except AttributeError:
                pass

            self.active_widgets.append(instance)
            wx.CallAfter(self.handle_item, instance)

        self.__changed_classes += [cls]
        cls.__original_init__ = cls.__init__
        cls.__init__ = __init__

    def start(self):
        if self.__changed_classes:
            return

        path = os.path.dirname(wx.__file__)

        if '.zip' in path:
            zip_path, mod_path = path.split('.zip')
            zip_file = zipfile.ZipFile(zip_path + '.zip')
            mod_path = mod_path[1:]
            wx_files = zip_file.namelist()

        else:
            mod_path = os.path.split(path)[1]
            wx_files = []
            for root, dirs, files in os.walk(path):
                wx_files += list(
                    os.path.join(mod_path + root.rsplit(mod_path)[-1], f)
                    for f in files
                )

        mods = []

        for item in wx_files:
            if item.startswith(mod_path):
                item = item.split('\\')
                if len(item) == 1:
                    item = item[0].split('/')

                mod_pth = item[:-1]
                mod, ext = os.path.splitext(item[-1])
                if not ext[1:].startswith('py'):
                    continue

                if mod == '__init__':
                    mod = ''
                elif mod.startswith('_'):
                    continue
                else:
                    mod = '.' + mod

                mod = '.'.join(mod_pth) + mod
                if mod not in mods:
                    mods += [mod]

        mods.insert(0, 'wx')
        for wx_mod in mods:
            try:
                _ = __import__(wx_mod)
            except:
                continue

            mod = sys.modules[wx_mod]

            for key, value in mod.__dict__.items():
                if key.startswith('_'):
                    continue
                if 'DC' in key:
                    continue

                if inspect.isclass(value) and value not in self.__changed_classes:
                    try:
                        for cls in value.__mro__:
                            if not cls.__module__.startswith('wx'):
                                continue

                            if not hasattr(cls, 'SetBackgroundColour'):
                                continue

                            self.modify_class(value)

                            break
                    except AttributeError:
                        pass

        self.modify_class(wx.lib.agw.aui.AuiManager)
        self.modify_class(wx.aui.AuiManager)

        self.set_theme(CurrentThemes.ActiveTheme)

        return self


Theme = Theme()
