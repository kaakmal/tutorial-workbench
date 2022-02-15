import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtCore, QtWidgets, QtGui
from FreeCAD import Qt

import time

#FreeCAD.Console.PrintMessage(translate("context", "My text") + "\n")

def QT_TRANSLATE_NOOP(context, text):
    return text


class Step:
    '''
    Holds all the information for a step of the tutorial. Centered around a command–will not create
    without one.
    '''
    def __init__(self,obj,command):
        obj.Label = Qt.translate('TutorialWB','Step')
        obj.addProperty(
            'App::PropertyString',
            'Instruction',
            'Step',
            QT_TRANSLATE_NOOP(
                'App::Property',
                'Instructions to user for this step')).Instruction=''
        obj.addProperty(
            'App::PropertyPythonObject',
            'Command',
            'Step',
            QT_TRANSLATE_NOOP(
                'App::Property',
                'Gui or console command user should enter')).Command=command
        obj.addProperty(
            'App::PropertyString',
            'Cluster',
            'Step',
            QT_TRANSLATE_NOOP(
                'App::Property',
                'Indicates step belongs to group of related steps')).Cluster=''
        obj.Proxy = self

    def create(command):
        obj = App.ActiveDocument.addObject('App::FeaturePython','Step')
        Step(obj,command)
        return obj


class Tutorial:
    '''
    Container for the tutorial. Holds all steps and hints
    plus some overall information (e.g., author, version).
    '''
    def __init__(self,obj):
        obj.Label = Qt.translate('TutorialWB','Tutorial')
        obj.addProperty(
            'App::PropertyString',
            'Author',
            'Tutorial',
            QT_TRANSLATE_NOOP(
                'App::Property',
                'Name of author of tutorial')).Author=''
        obj.addProperty(
            'App::PropertyString',
            'Language',
            'Tutorial',
            QT_TRANSLATE_NOOP(
                'App::Property',
                'Language of tutorial text')).Language=''
        obj.addProperty(
            'App::PropertyString',
            'Version',
            'Tutorial',
            QT_TRANSLATE_NOOP(
                'App::Property',
                'FreeCAD version used to create tutorial')).Version=''
        obj.addProperty(
            'App::PropertyString',
            'Title',
            'Tutorial',
            QT_TRANSLATE_NOOP(
                'App::Property',
                'Title of tutorial')).Title=''
        obj.addProperty(
            'App::PropertyStringList',
            'RequiredModules',
            'Tutorial',
            QT_TRANSLATE_NOOP(
                'App::Property',
                'List of modules imported by author & required for model'
                )).RequiredModules=['FreeCAD']
        obj.Proxy = self

    def create(obj_name='newtutorial'):
        '''
        Creates new tutorial object
        '''
        obj = App.ActiveDocument.addObject('App::DocumentObjectGroupPython',obj_name)
        Tutorial(obj)

    def add_step(command):
        '''
        Adds step to selected tutorial, will add step to all selected tutorials if
        multiple are selected.
        '''
        step = Step.create(command)
        if Gui.Selection.hasSelection():
            selected=Gui.Selection.getSelection()
            for obj in selected:
                if hasattr(obj,'addObject'):
                    obj.addObject(step)
        else:
            #FreeCAD.Console.PrintError(Qt.translate('No tutorial selected'))
            App.Console.PrintMessage(Qt.translate('TutorialWB','No tutorial selected \n'))


