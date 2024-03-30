# encoding: utf-8

###########################################################################################################
#
#
# File Format Plugin
# Implementation for exporting fonts through the Export dialog
#
# Read the docs:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/File%20Format
#
# For help on the use of Interface Builder:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
from gc import callbacks
# from tkinter import OFF
import objc
import AppKit
from GlyphsApp import *
from GlyphsApp.plugins import *
from vanilla import *
# from vanilla import Window,TextBox, CheckBox,Group,Slider,Button,PopUpButton,ImageView
import os
from AppKit import NSApplication, NSApp, NSWorkspace, NSViewController, NSWindowDidBecomeKeyNotification
from datetime import datetime
import subprocess
import os
import time

randomFileNamePref = 'com.wasim.trueglyph.randomfilename'
openfilePref = 'com.wasim.trueglyph.openfile'
zoomPref = 'com.wasim.trueglyph.zoom'
zoomPreviousPref = 'com.wasim.trueglyph.zoomprevious'
exportmodePref = 'com.wasim.trueglyph.exportmode'
exportPreviewPref = 'com.wasim.trueglyph.exportpreview'
exportmodeList = ["Black White", "Glyph Look", "Current Look"]


class ExportViewController(NSViewController):

    def viewDidAppear(self):
        trueglyph.updatezoom(self, self)
        # print("__viewDidAppear",  self.view)

    def viewDidDisappear(self):
        if Glyphs.font.currentTab:
            Glyphs.font.currentTab.scale = Glyphs.defaults[zoomPreviousPref]
        else:
            print("currentTab is None")
        print("__viewDidAppear",  self.view)
        filepath = os.path.expanduser("~/Desktop/glyphsexports/LogoPDFt.pdf")


class trueglyph(FileFormatPlugin):
    @objc.python_method
    def settings(self):
        self.name = Glyphs.localize(
            {'en': u'True Glyph', 'de': u'True Glyph'})
        self.icon = 'ExportIcon'
        self.toolbarPosition = 200
        # set default user settings for Zoom and folder
        Glyphs.registerDefaults({zoomPref: 1, zoomPreviousPref: 1, randomFileNamePref: False,
                                openfilePref: 1, exportmodePref: 0, exportPreviewPref: 0})

        # Init user preferences if not existent and set default value
        # print(Glyphs.defaults[openfilePref])
        # Build the UI
        self.w = Window((100, 100))
        self.w.group = Group("auto")
        self.viewController = ExportViewController.new()
        self.viewController.setView_(self.w.group._nsObject)

 
        self.w.group.sliderValueTextBox = TextBox("auto", "Zoom Level: 1.0")
        self.w.group.zoom2 = Slider('auto', callback=self.zoom_, minValue=0.01, maxValue=5, value=Glyphs.defaults[zoomPref])


        self.w.group.RandomFileNameCheckBox = CheckBox(
            "auto", "Random File Name", callback=self.activeRandomFileName_,  value=Glyphs.defaults[randomFileNamePref])
        self.w.group.OpenFileCheckBox = CheckBox(
            "auto", "Reveal file in Finder", callback=self.activeOpenFile_, value=Glyphs.defaults[openfilePref])
        self.w.group.sliderLabel = TextBox("auto", 'Change Handel Size')
        
        
      

        self.w.group.bannerImageView = ImageView("auto")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # self.w.group.bannerImageView.setImage(
        #     imagePath=os.path.join(dir_path, "wasim.pdf"))

        self.w.group.imageButton = ImageButton(
                    "auto",
                    imagePath=os.path.join(dir_path, "wasim.pdf"),bordered = False,imagePosition = "right",
                    callback=self.imageButtonCallback
                )

        self.w.group.exportTypeLabel = TextBox("auto", 'Select export type')
        self.w.group.exportType = PopUpButton(
            "auto", exportmodeList, callback=self.changeExportMode)
        if Glyphs.defaults[exportmodePref]:
            self.w.group.exportType.set(Glyphs.defaults[exportmodePref])
        self.w.group.zoom = Slider('auto', callback=self.zoom_, minValue=0.01,
                                   maxValue=5, tickMarkCount=None, value=Glyphs.defaults[zoomPref])
        self.w.group.FeedbackLabel = TextBox("auto", '')
        self.w.group.imageView3 = ImageView(
            'auto', horizontalAlignment="center", verticalAlignment="center", scale="proportional")
        # self.w.group.imageView3.setImage(imagePath=dir_path+'/look-current.pdf')
        self.change_preview_image()

        # for export settings dialogs, you **need** to use auto layout. https://vanilla.robotools.dev/en/latest/concepts/positioning.html?highlight=auto#auto-layout
        rules = [
            # Horizontal
            "H:|-[RandomFileNameCheckBox]-|",
            "H:|-[OpenFileCheckBox]-|",
            "H:|-[sliderLabel]-|",
            "H:|-[sliderValueTextBox]-|",
            "H:|-[zoom]-|",
            "H:|-[exportTypeLabel]-|",
            "H:|-[exportType]-|",
            "H:|-[FeedbackLabel]-|",
            "H:|-[imageView3]-|",
            # Vertical
            "V:|[imageButton(120@1000)]-[RandomFileNameCheckBox(20@999)]-[OpenFileCheckBox(20@999)]-[sliderLabel(20@300)]-[sliderValueTextBox(20@999)]-[zoom(20@999)]-[exportTypeLabel(20@300)]-[exportType(20@300)]-[FeedbackLabel(20@999)]-[imageView3(200@999)]-|"
        ]
        metrics = {}
        self.w.group.addAutoPosSizeRules(rules, metrics)

        # We only need the group, not the window. But vanilla doesn’t seem to be able to build a view outside of a window
        self.dialog = self.w.group._nsObject


    @objc.python_method
    def imageButtonCallback(self, sender):
        import webbrowser
        url = "https://wasimm.com"
        webbrowser.open(url, new=0, autoraise=True)
        webbrowser.open('https://instagram.com/wsim', new=0, autoraise=True)

    def start(self):
        self.updateFeedBackTextField()

    @objc.python_method
    def updatezoom(self,sender):
        if Glyphs.font.currentTab:
            Glyphs.defaults[zoomPreviousPref] = Glyphs.font.currentTab.scale
            Glyphs.font.currentTab.scale = float(Glyphs.defaults[zoomPref])
            return True


    # Example function. You may delete it
    def activeRandomFileName_(self, sender):
        Glyphs.defaults[randomFileNamePref] = bool(sender.get())
        self.updateFeedBackTextField()
    # Example function. You may delete it
    def zoom_(self, sender):
        if Glyphs.font.currentTab:
            self.clearFeedBack()
            Glyphs.defaults[zoomPref] = sender.get()
            Glyphs.font.currentTab.scale = Glyphs.defaults[zoomPref]
            # print('zoom ',Glyphs.defaults[zoomPref])
            slider_value = sender.get()  # Get the current value of the slider
            slider_value_text = "Zoom Level: {:.2f}".format(slider_value)  # Format the slider value as a string
            self.w.group.sliderValueTextBox.set(slider_value_text)  # Update the TextBox with the slider value

        else:
            self.w.group.zoom.set(Glyphs.defaults[zoomPref])
            self.clearFeedBack()
            self.w.group.FeedbackLabel.set('Please open any glyph First')


    @objc.python_method
    def change_preview_image(self):
        import os 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # self.w.group.imageView3.setImage(imagePath=dir_path+'/look-current.pdf')
        if str(Glyphs.defaults[exportmodePref]) == "0":
            self.w.group.imageView3.setImage(imagePath=dir_path+'/look-blackwhite.pdf')
        if Glyphs.defaults[exportmodePref] == 1:
            self.w.group.imageView3.setImage(imagePath=dir_path+'/look-glyphs.pdf')
        if Glyphs.defaults[exportmodePref] == 2:
            self.w.group.imageView3.setImage(imagePath=dir_path+'/look-current.pdf')

    def clearFeedBack(self):
        self.w.group.FeedbackLabel.set('')

        # Example function. You may delete it
    def activeOpenFile_(self, sender):
        Glyphs.defaults[openfilePref] = bool(sender.get())
        self.updateFeedBackTextField()
    
    # Example function. You may delete it
    @objc.python_method
    def updateFeedBackTextField(self):
        string = []
        if Glyphs.defaults[randomFileNamePref]:
            string.append('Random name ')
        if Glyphs.defaults[openfilePref]:
            string.append('open file after it saved')
        self.w.group.FeedbackLabel.set(', '.join(string) if len(string) else '....')

    @objc.python_method
    def changeExportMode(self, sender):
        if sender.get() or sender.get() == 0 :
            # print(sender.get())
            Glyphs.defaults[exportmodePref] = sender.get()
        self.change_preview_image()



    def cambineGlyphsTogether(self):
        if Glyphs.font.glyphs['exportedPreviewPleaseDeleteit']:
            notexist = None
        else:
            Glyphs.font.glyphs.append(GSGlyph('exportedPreviewPleaseDeleteit'))
        newLayer = Glyphs.font.glyphs['exportedPreviewPleaseDeleteit'].layers[0]
        newLayer.clear()
        currenlayersCount = len( Glyphs.font.currentTab.composedLayers)
        LastCount = len(Glyphs.font.currentTab.composedLayers)-1
        for index,glyphs in enumerate(reversed(Glyphs.font.currentTab.composedLayers)):
            newLayer.shapes.append(GSComponent(glyphs.parent.name))
            if str(LastCount) == str(index):
                while len(newLayer.components) > 0:
                    newLayer.decomposeComponents()
                    newLayer.correctPathDirection()
                    for path in newLayer.paths:
                        # tab = Glyphs.font.newTab('/exportedPreviewPleaseDeleteit')
                        Glyphs.font.tool = 'GlyphsToolDraw'
            # print('currenlayersCount:',currenlayersCount,"== index",index+1)           
            if currenlayersCount == index+1:
                # print(index, currenlayersCount)
                self.updatezoom(self)
                return True
                Glyphs.font.currentTab.close()
    @objc.python_method
    def GSEditViewController_saveToPDF(self, path, rect=None):
        if rect is None:
            rect = Glyphs.font.currentTab.viewPort
        pdf = Glyphs.font.currentTab.graphicView().dataWithPDFInsideRect_(rect)
        pdf.writeToFile_atomically_(path, True)

    @objc.python_method
    def export(self, font):
        if Glyphs.font.currentTab:
            self.cambineGlyphsTogether()
            filename = str(font.familyName)+"-"
            if Glyphs.defaults[randomFileNamePref]:
                todayDate = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
                filename = filename+str(todayDate)
            filepath = GetSaveFile("Choose export destination", filename, 'pdf')
            if filepath:
                    # 0 = Black White 1 = Glyph Look 2= Current Look
                if Glyphs.defaults[exportmodePref] ==0:
                    Glyphs.font.currentTab.textCursor = len(Glyphs.font.currentTab.composedLayers)
                    Glyphs.font.tool = 'GlyphsToolText'
                    Glyphs.font.tool = 'GlyphsToolSelect'
                    Glyphs.font.currentTab.saveToPDF(filepath)

                if Glyphs.defaults[exportmodePref] ==1:
                    # if self.cambineGlyphsTogether():
                        Glyphs.font.tool = 'GlyphsToolDraw'
                        Glyphs.font.currentTab.saveToPDF(filepath)
                        # if len(Glyphs.font.glyphs['exportedPreviewPleaseDeleteit'].layers[0].shapes) >= 0:
                        #     Glyphs.font.tool = 'GlyphsToolDraw'
                        #     Glyphs.font.currentTab.saveToPDF(filepath)

                if Glyphs.defaults[exportmodePref] ==2:
                    # if self.cambineGlyphsTogether():
                        tab = Glyphs.font.newTab('/exportedPreviewPleaseDeleteit')
                        if self.updatezoom(self):
                            Glyphs.font.currentTab.saveToPDF(filepath)
                if Glyphs.defaults[openfilePref]:
                    subprocess.call(["open", "-R", filepath])   
                Glyphs.font.currentTab.saveToPDF(filepath)
                del(Glyphs.font.glyphs['exportedPreviewPleaseDeleteit'])
                return (True, 'The export of was successful.')
            else:
                return (False, 'Active any tap First!')
        else:
            Glyphs.showNotification('Export fonts','please type some text first.')
            return (False, 'Active any tap First!')

    @objc.python_method
    def __file__(self):
        """Please leave this method unchanged"""
        return __file__
