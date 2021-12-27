import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui
from FreeCAD import Qt

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
            #allow selecting object to 
            #FreeCAD.Console.PrintError(Qt.translate('No tutorial selected'))
            App.Console.PrintMessage(Qt.translate('TutorialWB','No tutorial selected \n'))

class ActionRecorder(QtCore.QObject):
    '''
    Records user inputs to put into steps of tutorial using Qt event filter
    '''

    def EventFilter(self, obj, event):
        '''
        Listens in to user input, copies & sends on to be saved as steps
        '''
        #may want to map some of these to the same function
        events = {
            'QEvent.Shortcut': record_shortcut,
            'QEvent.KeyPress': record_keypress,
            'QEvent.KeyRelease': record_keyrelease,
            'QEvent.MouseButtonDblClick': record_dblclick,
            'QEvent.MouseButtonPress': record_mouse_press,
            'QEvent.MouseButtonRelease': record_mouse_release,
            'QEvent.MouseMove': record_mouse_move
            }
        handler = events.get(event.type())
        print(handler)
        handler(object, event)
        #keeps events from getting eaten by filter
        return False

    def record_shortcut(obj, event):
        keys=QtGui.QShortcutEvent.key()
        key2=QtGui.QShortcutEvent.key(event)
        key3=event.key
        command = {
            'Type': 'Shortcut',
            'Value': keys,
            'Value2': key2,
            'Value3': key3,
            }
        return command

    def record_keypress(obj, event):
        focus=QtGui.QApplication.focusWidget()
        key=QtGui.QKeyEvent.key()
        command = {
            'Type': 'Keypress',
            'Value': key,
            'Focus': focus,
            }
        return command

    def record_keyrelease(obj, event):
        focus=QtGui.QApplication.focusWidget()
        key=QtGui.QKeyEvent.key()
        command = {
            'Type': 'Keyrelease',
            'Value': key,
            'Focus': focus,
            }
        return command

    def record_dblclick(obj,event):
        print("record double click called")

    def record_mousepress(obj,event):
        focus=QtGui.QApplication.focusWidget()
        localPos=QtGui.QMouseEvent.position()
        button=QtGui.QMouseEvent
        command = {
            'Type': 'Mousepress',
            'Position': localPos,
            'Focus': focus,
            }

    def record_mouse_release(obj,event):
        print("mouse release called")

    def record_mouse_move(obj, event):
        print("mouse moved. Did not leave forwarding address")

def make_recorder():
    recorder=ActionRecorder()
    Gui.getMainWindow().installEventFilter(recorder)
