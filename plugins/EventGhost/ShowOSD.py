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

import threading
from os import listdir
from os.path import abspath, dirname, join

import wx

import eg
from eg.WinApi.Dynamic import (
    CreateEvent,
    SetEvent,
    SetWindowPos,
    SWP_FRAMECHANGED,
    SWP_HIDEWINDOW,
    SWP_NOACTIVATE,
    SWP_NOOWNERZORDER,
    SWP_SHOWWINDOW,
)
from eg.WinApi.Utils import GetMonitorDimensions

HWND_FLAGS = SWP_NOACTIVATE | SWP_NOOWNERZORDER | SWP_FRAMECHANGED

SKIN_DIR = join(
    abspath(dirname(__file__.decode('mbcs'))),
    "OsdSkins"
)
SKINS = [name[:-3] for name in listdir(SKIN_DIR) if name.endswith(".py")]
SKINS.sort()

DEFAULT_FONT_INFO = wx.Font(
    18,
    wx.SWISS,
    wx.NORMAL,
    wx.BOLD
).GetNativeFontInfoDesc()


class ShowOSD(eg.ActionBase):
    name = "Show OSD"
    description = "Shows a simple On Screen Display."
    iconFile = "icons/ShowOSD"

    class text:
        label = "Show OSD: %s"
        editText = "Text to display:"
        osdFont = "Text Font:"
        osdColour = "Text Colour:"
        outlineFont = "Outline OSD:"
        alignment = "Alignment:"
        scroll = "Scroll text lines: "
        alignmentChoices = [
            "Top Left",
            "Top Right",
            "Bottom Left",
            "Bottom Right",
            "Screen Center",
            "Bottom Center",
            "Top Center",
            "Left Center",
            "Right Center",
        ]
        justification = 'Justification:'
        justificationChoices = [
            'Left',
            'Center',
            'Right'
        ]
        display = "Show on display:"
        xOffset = "Horizontal offset X:"
        yOffset = "Vertical offset Y:"
        wait1 = "Autohide OSD after:"
        wait2 = "0 = never"
        skin = "Use skin:"

    def __call__(
            self,
            osdText="",
            fontInfo=None,
            foregroundColour=(255, 255, 255),
            backgroundColour=(0, 0, 0),
            alignment=0,
            offset=(0, 0),
            displayNumber=0,
            timeout=3.0,
            skin=None,
            justification=0,
            scroll=0
    ):
        if isinstance(skin, bool):
            skin = SKINS[0] if skin else None
        self.osdFrame.timer.cancel()
        osdText = eg.ParseString(osdText)
        event = CreateEvent(None, 0, 0, None)
        wx.CallAfter(
            self.osdFrame.ShowOSD,
            osdText,
            fontInfo,
            foregroundColour,
            backgroundColour,
            alignment,
            offset,
            displayNumber,
            timeout,
            event,
            skin,
            justification,
            scroll
        )
        eg.actionThread.WaitOnEvent(event)

    def Configure(
            self,
            osdText="",
            fontInfo=None,
            foregroundColour=(255, 255, 255),
            backgroundColour=(0, 0, 0),
            alignment=0,
            offset=(0, 0),
            displayNumber=0,
            timeout=3.0,
            skin=None,
            justification=0,
            scrollText=0
    ):
        if isinstance(skin, bool):
            skin = SKINS[0] if skin else None
        if fontInfo is None:
            fontInfo = DEFAULT_FONT_INFO
        panel = eg.ConfigPanel()
        text = self.text
        editTextCtrl = panel.TextCtrl(osdText, style=wx.TE_MULTILINE)
        alignmentChoice = panel.Choice(
            alignment, choices=text.alignmentChoices
        )
        justificationChoice = panel.Choice(
            justification, choices=text.justificationChoices
        )
        displayChoice = eg.DisplayChoice(panel, displayNumber)
        xOffsetCtrl = panel.SpinIntCtrl(offset[0], -32000, 32000)
        yOffsetCtrl = panel.SpinIntCtrl(offset[1], -32000, 32000)
        timeCtrl = panel.SpinNumCtrl(timeout)

        fontButton = panel.FontSelectButton(fontInfo)
        foregroundColourButton = panel.ColourSelectButton(foregroundColour)

        if backgroundColour is None:
            tmpColour = (0, 0, 0)
        else:
            tmpColour = backgroundColour
        outlineCheck = panel.CheckBox(
            backgroundColour is not None, ''
        )

        backgroundColourButton = panel.ColourSelectButton(tmpColour)
        backgroundColourButton.Enable(backgroundColour is not None)

        useSkin = skin is not None
        skinCheck = panel.CheckBox(useSkin, '')
        skinChoice = panel.Choice(SKINS.index(skin) if skin else 0, SKINS)
        skinChoice.Enable(useSkin)

        scrollCtrl = panel.SpinIntCtrl(scrollText)
        scrollCheck = panel.CheckBox(scrollText > 0, '')
        scrollCtrl.Enable(scrollText > 0)

        sts = []
        ctrls = []

        def h_sizer(text, ctrl, ctrl2=None, prop=0):
            st = panel.StaticText(text)
            sts.append(st)
            line_sizer = wx.BoxSizer(wx.HORIZONTAL)

            line_sizer.Add(st, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

            if ctrl2 is None:
                line_sizer.Add(ctrl, prop, wx.ALL | wx.EXPAND, 5)
                ctrls.append(ctrl)
            else:
                if isinstance(ctrl2, wx.StaticText):
                    line_sizer.Add(ctrl, prop, wx.ALL | wx.EXPAND, 5)
                    ctrls.append(ctrl)
                    line_sizer.Add(
                        ctrl2,
                        prop,
                        wx.ALL | wx.ALIGN_CENTER_VERTICAL,
                        5
                    )
                else:
                    line_sizer.Add(ctrl, prop, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    ctrls.append(ctrl2)

                    line_sizer.Add(
                        ctrl2,
                        prop,
                        wx.ALL | wx.EXPAND,
                        5
                    )

            return line_sizer

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        center_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        top_sizer.Add(h_sizer(text.editText, editTextCtrl, prop=1), 1, wx.EXPAND)
        bottom_sizer.Add(left_sizer)
        bottom_sizer.Add(center_sizer)
        bottom_sizer.Add(right_sizer)

        del ctrls[:]

        left_sizer.Add(h_sizer(text.alignment, alignmentChoice))
        left_sizer.Add(h_sizer(text.justification, justificationChoice))
        left_sizer.Add(h_sizer(text.display, displayChoice))
        left_sizer.Add(h_sizer(text.osdFont, fontButton))

        eg.EqualizeWidths(tuple(sts))

        del sts[:]

        center_sizer.Add(
            h_sizer(text.outlineFont, outlineCheck, backgroundColourButton)
        )
        center_sizer.Add(
            h_sizer(text.skin, skinCheck, skinChoice)
        )

        center_sizer.Add(
            h_sizer(text.scroll, scrollCheck, scrollCtrl)
        )

        eg.EqualizeWidths(tuple(sts))
        del sts[:]

        wait_suffix = panel.StaticText('sec')
        timeCtrl.numCtrl.SetToolTipString(text.wait2)
        timeCtrl.spinbutton.SetToolTipString(text.wait2)
        right_sizer.Add(h_sizer(text.xOffset, xOffsetCtrl))
        right_sizer.Add(h_sizer(text.yOffset, yOffsetCtrl))
        right_sizer.Add(h_sizer(text.wait1, timeCtrl, wait_suffix))
        right_sizer.Add(h_sizer(text.osdColour, foregroundColourButton))

        eg.EqualizeWidths(tuple(sts))
        eg.EqualizeWidths(tuple(ctrls))

        panel.sizer.Add(top_sizer, 1, wx.EXPAND)
        panel.sizer.Add(bottom_sizer)

        def OnCheckBoxBGColour(event):
            backgroundColourButton.Enable(outlineCheck.IsChecked())
            event.Skip()
        outlineCheck.Bind(wx.EVT_CHECKBOX, OnCheckBoxBGColour)

        def OnCheckBoxSkin(event):
            skinChoice.Enable(skinCheck.IsChecked())
            event.Skip()
        skinCheck.Bind(wx.EVT_CHECKBOX, OnCheckBoxSkin)

        def OnCheckBoxScroll(event):
            scrollCtrl.Enable(scrollCheck.IsChecked())
            event.Skip()
        scrollCheck.Bind(wx.EVT_CHECKBOX, OnCheckBoxScroll)

        while panel.Affirmed():
            if outlineCheck.IsChecked():
                outlineColour = backgroundColourButton.GetValue()
            else:
                outlineColour = None

            if skinCheck.IsChecked():
                skin = skinChoice.GetStringSelection()
            else:
                skin = None

            if scrollCheck.IsChecked():
                scroll = scrollCtrl.GetValue()
            else:
                scroll = 0

            panel.SetResult(
                editTextCtrl.GetValue(),
                fontButton.GetValue(),
                foregroundColourButton.GetValue(),
                outlineColour,
                alignmentChoice.GetValue(),
                (xOffsetCtrl.GetValue(), yOffsetCtrl.GetValue()),
                displayChoice.GetValue(),
                timeCtrl.GetValue(),
                skin,
                justificationChoice.GetSelection(),
                scroll
            )

    def GetLabel(self, osdText, *dummyArgs):
        return self.text.label % osdText.replace("\n", r"\n")

    @classmethod
    def OnAddAction(cls):
        def MakeOSD():
            cls.osdFrame = OSDFrame(None)

            def CloseOSD():
                cls.osdFrame.timer.cancel()
                cls.osdFrame.Close()

            eg.app.onExitFuncs.append(CloseOSD)

        wx.CallAfter(MakeOSD)

    @eg.LogIt
    def OnClose(self):
        # self.osdFrame.timer.cancel()
        # wx.CallAfter(self.osdFrame.Close)
        self.osdFrame = None


class OSDFrame(wx.Frame):
    """
    A shaped frame to display the OSD.
    """

    @eg.LogIt
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            -1,
            "OSD Window",
            size=(0, 0),
            style=(
                wx.FRAME_SHAPED |
                wx.NO_BORDER |
                wx.FRAME_NO_TASKBAR |
                wx.STAY_ON_TOP
            )
        )
        self.hwnd = self.GetHandle()
        self.bitmap = wx.EmptyBitmap(0, 0)
        # we need a timer to possibly cancel it
        self.timer = threading.Timer(0.0, eg.DummyFunc)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    if eg.debugLevel:
        @eg.LogIt
        def __del__(self):
            pass

    @staticmethod
    def GetSkinnedBitmap(
            textLines,
            textWidths,
            textHeights,
            textWidth,
            textHeight,
            memoryDC,
            textColour,
            skinName,
            justification
    ):
        image = wx.Image(join(SKIN_DIR, skinName + ".png"))
        option = eg.Bunch()

        def Setup(minWidth, minHeight, xMargin, yMargin,
                  transparentColour=None):
            width = textWidth + 2 * xMargin
            if width < minWidth:
                width = minWidth
            height = textHeight + 2 * yMargin
            if height < minHeight:
                height = minHeight
            option.xMargin = xMargin
            option.yMargin = yMargin
            option.transparentColour = transparentColour
            bitmap = wx.EmptyBitmap(width, height)
            option.bitmap = bitmap
            memoryDC.SelectObject(bitmap)
            return width, height

        def Copy(x, y, width, height, toX, toY):
            bmp = wx.BitmapFromImage(image.GetSubImage((x, y, width, height)))
            memoryDC.DrawBitmap(bmp, toX, toY)

        def Scale(x, y, width, height, toX, toY, toWidth, toHeight):
            subImage = image.GetSubImage((x, y, width, height))
            subImage.Rescale(toWidth, toHeight, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.BitmapFromImage(subImage)
            memoryDC.DrawBitmap(bmp, toX, toY)

        scriptGlobals = dict(Setup=Setup, Copy=Copy, Scale=Scale)
        eg.ExecFile(join(SKIN_DIR, skinName + ".py"), scriptGlobals)

        bitmap = option.bitmap
        memoryDC.SelectObject(wx.NullBitmap)
        bitmap.SetMask(wx.Mask(bitmap, option.transparentColour))
        memoryDC.SelectObject(bitmap)
        memoryDC.SetTextForeground(textColour)
        memoryDC.SetTextBackground(textColour)
        DrawTextLines(
            memoryDC,
            textLines,
            textHeights,
            textWidth,
            justification,
            option.xMargin,
            option.yMargin
        )
        memoryDC.SelectObject(wx.NullBitmap)
        return bitmap

    def OnClose(self, dummyEvent=None):
        # BUGFIX: Just hooking this event makes sure that nothing happens
        # when this OSD window is closed
        pass

    @eg.LogIt
    def OnPaint(self, dummyEvent=None):
        wx.BufferedPaintDC(self, self.bitmap)

    @eg.LogIt
    def OnTimeout(self):
        wx.CallAfter(
            SetWindowPos, self.hwnd, 0, 0, 0, 0, 0, HWND_FLAGS | SWP_HIDEWINDOW
        )

    @eg.LogIt
    def ShowOSD(
            self,
            osdText="",
            fontInfo=None,
            textColour=(255, 255, 255),
            outlineColour=(0, 0, 0),
            alignment=0,
            offset=(0, 0),
            displayNumber=0,
            timeout=3.0,
            event=None,
            skin=None,
            justification=0,
            scroll=0
    ):
        self.timer.cancel()
        if osdText.strip() == "":
            self.bitmap = wx.EmptyBitmap(0, 0)
            SetWindowPos(self.hwnd, 0, 0, 0, 0, 0, HWND_FLAGS | SWP_HIDEWINDOW)
            SetEvent(event)
            return

        # self.Freeze()
        memoryDC = wx.MemoryDC()

        # make sure the mask colour is not used by foreground or
        # background colour
        forbiddenColours = (textColour, outlineColour)
        maskColour = (255, 0, 255)
        if maskColour in forbiddenColours:
            maskColour = (0, 0, 2)
            if maskColour in forbiddenColours:
                maskColour = (0, 0, 3)
        maskBrush = wx.Brush(maskColour, wx.SOLID)
        memoryDC.SetBackground(maskBrush)

        if fontInfo is None:
            fontInfo = DEFAULT_FONT_INFO
        font = wx.FontFromNativeInfoString(fontInfo)
        memoryDC.SetFont(font)

        textLines = osdText.splitlines()
        sizes = [memoryDC.GetTextExtent(line or " ") for line in textLines]
        textWidths, textHeights = zip(*sizes)
        textWidth = max(textWidths)
        textHeight = sum(textHeights)

        if skin:
            bitmap = self.GetSkinnedBitmap(
                textLines,
                textWidths,
                textHeights,
                textWidth,
                textHeight,
                memoryDC,
                textColour,
                skin,
                justification
            )
            width, height = bitmap.GetSize()
        elif outlineColour is None:
            width, height = textWidth, textHeight
            bitmap = wx.EmptyBitmap(width, height)
            memoryDC.SelectObject(bitmap)

            # fill the DC background with the maskColour
            memoryDC.Clear()

            # draw the text with the foreground colour
            memoryDC.SetTextForeground(textColour)
            DrawTextLines(
                memoryDC,
                textLines,
                textHeights,
                textWidth,
                justification
            )

            # mask the bitmap, so we can use it to get the needed
            # region of the window
            memoryDC.SelectObject(wx.NullBitmap)
            bitmap.SetMask(wx.Mask(bitmap, maskColour))

            # fill the anti-aliased pixels of the text with the foreground
            # colour, because the region of the window will add these
            # half filled pixels also. Otherwise we would get an ugly
            # border with mask-coloured pixels.
            memoryDC.SetBackground(wx.Brush(textColour, wx.SOLID))
            memoryDC.SelectObject(bitmap)
            memoryDC.Clear()
            memoryDC.SelectObject(wx.NullBitmap)
        else:
            width, height = textWidth + 5, textHeight + 5
            outlineBitmap = wx.EmptyBitmap(width, height, 1)
            outlineDC = wx.MemoryDC()
            outlineDC.SetFont(font)
            outlineDC.SelectObject(outlineBitmap)
            outlineDC.Clear()
            outlineDC.SetBackgroundMode(wx.SOLID)
            DrawTextLines(
                outlineDC,
                textLines,
                textHeights,
                textWidth,
                justification
            )
            outlineDC.SelectObject(wx.NullBitmap)
            outlineBitmap.SetMask(wx.Mask(outlineBitmap))
            outlineDC.SelectObject(outlineBitmap)

            bitmap = wx.EmptyBitmap(width, height)
            memoryDC.SetTextForeground(outlineColour)
            memoryDC.SelectObject(bitmap)
            memoryDC.Clear()

            Blit = memoryDC.Blit
            logicalFunc = wx.COPY
            for x in xrange(5):
                for y in xrange(5):
                    Blit(
                        x, y, width, height, outlineDC, 0, 0, logicalFunc, True
                    )
            outlineDC.SelectObject(wx.NullBitmap)
            memoryDC.SetTextForeground(textColour)
            DrawTextLines(
                memoryDC,
                textLines,
                textHeights,
                textWidth,
                justification,
                2,
                2
            )
            memoryDC.SelectObject(wx.NullBitmap)
            bitmap.SetMask(wx.Mask(bitmap, maskColour))

        region = wx.RegionFromBitmap(bitmap)
        self.SetShape(region)
        self.bitmap = bitmap
        monitorDimensions = GetMonitorDimensions()
        try:
            displayRect = monitorDimensions[displayNumber]
        except IndexError:
            displayRect = monitorDimensions[0]
        xOffset, yOffset = offset
        xFunc, yFunc = ALIGNMENT_FUNCS[alignment]
        x = displayRect.x + xFunc((displayRect.width - width), xOffset)
        y = displayRect.y + yFunc((displayRect.height - height), yOffset)
        deviceContext = wx.ClientDC(self)
        deviceContext.DrawBitmap(self.bitmap, 0, 0, False)
        SetWindowPos(
            self.hwnd, 0, x, y, width, height, HWND_FLAGS | SWP_SHOWWINDOW
        )

        if timeout > 0.0:
            self.timer = threading.Timer(timeout, self.OnTimeout)
            self.timer.start()
        eg.app.Yield(True)
        SetEvent(event)


def AlignLeft(width, offset):
    return offset


def AlignCenter(width, offset):
    return (width / 2) + offset


def AlignRight(width, offset):
    return width - offset


ALIGNMENT_FUNCS = (
    (AlignLeft, AlignLeft),  # Top Left
    (AlignRight, AlignLeft),  # Top Right
    (AlignLeft, AlignRight),  # Bottom Left
    (AlignRight, AlignRight),  # Bottom Right
    (AlignCenter, AlignCenter),  # Screen Center
    (AlignCenter, AlignRight),  # Bottom Center
    (AlignCenter, AlignLeft),  # Top Center
    (AlignLeft, AlignCenter),  # Left Center
    (AlignRight, AlignCenter),  # Right Center
)


def DrawTextLines(deviceContext, textLines, textHeights, textWidth, justification, xOffset=0, yOffset=0):
    print textWidth
    if justification == 0:
        for i, textLine in enumerate(textLines):
            print 0, 'offset', xOffset
            deviceContext.DrawText(textLine, xOffset, yOffset)
            yOffset += textHeights[i]

    elif justification == 1:
        for i, line in enumerate(textLines):
            offset = (
                (textWidth - deviceContext.GetTextExtent(line)[0]) / 2
            ) + xOffset

            print 1, 'offset', offset

            deviceContext.DrawText(line, offset, yOffset)
            yOffset += textHeights[i]
    else:
        for i, line in enumerate(textLines):
            offset = textWidth - deviceContext.GetTextExtent(line)[0] + xOffset
            print 2, 'offset', offset
            deviceContext.DrawText(line, offset, yOffset)
            yOffset += textHeights[i]

