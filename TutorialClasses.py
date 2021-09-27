import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui
from FreeCAD import Qt

#FreeCAD.Console.PrintMessage(Qt.translate("context", "My text") + "\n")

def QT_TRANSLATE_NOOP(context, text):
    return text

def import_macro():
    '''Gets path and reads macro as list of strings'''
    #Currently hardcoded–will fix when I learn PySide & can create dialog
    TEST_PATH='/Users/Katy/Library/Preferences/FreeCAD/Macro/Test.FCMacro'
    with open(TEST_PATH,'r') as baseMacro:
        command_strings=list(baseMacro)
    return command_strings

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
            'App::PropertyString',
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
                'Indicates step belongs to group of related steps')).Cluster='none'
        obj.Proxy = self

    def create(command):
        obj = App.ActiveDocument.addObject('App::FeaturePython','Step')
        Step(obj,command)
        return obj



class Tutorial:
    '''
    Container (Python document object group)for the tutorial. Holds all steps
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
                'List of modules imported by macro & required for model'
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
            #replace with selection dialog eventually
            FreeCAD.Console.PrintError(Qt.translate('No tutorial selected'))

    def convertMacro(macroStr):
        '''
        Converts pre-recorded macro into tutorial object
        Having a tutorial that was created by this function in your tree
        when you run it will cause the steps to add to the first tutorial
        -I have not yet determined how to fix that
        '''
        Tutorial.create('macroTutorial')
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(App.ActiveDocument.getObject('macroTutorial'))
        iterMacroStr=iter(macroStr)
        for line in iterMacroStr:
            if '### Begin' in line:
                cluster=line.split('command ')[1]
                line=next(iterMacroStr)
                while '### End' not in line:
                    step=Step.create(line)
                    step.Cluster=cluster
                    Gui.Selection.getSelection()[0].addObject(step)
                    line=next(iterMacroStr)
            elif 'import' in line:
                modName=line.split(' ')[1]
                Gui.Selection.getSelection()[0].RequiredModules.append(modName)
                line=next(iterMacroStr)
            elif '#' not in line and len(line) > 1:
                step=Step.create(line)
                Gui.Selection.getSelection()[0].addObject(step)
