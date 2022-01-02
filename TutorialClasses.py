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


class ActionRecorder(QtCore.QObject):
    '''
    Records user inputs to put into steps of tutorial using Qt event filter
    '''
    def __init__(self, parent=None):
        super(ActionRecorder, self).__init__(parent)
        print("init instance")
        
    def __del__(self):
        print("delete instance")
        
    def eventFilter(self, obj, event):
        '''
        Listens in to user input, copies & sends on to be saved as steps
        The name of this function needs to be _exactly_ what it currently is
        and have as little functionality as possible or it won't work.
        '''
        events = [QtCore.QEvent.Shortcut,QtCore.QEvent.KeyPress,
                  QtCore.QEvent.KeyRelease,QtCore.QEvent.MouseButtonDblClick,
                  QtCore.QEvent.MouseButtonPress,QtCore.QEvent.MouseButtonRelease,
                  ]
        if event.type() in events:
            #Keeping eventFilter lightweight
            ActionRecorder.handle_filter(event)
        #keeps events from getting eaten by filter
        return False

    def handle_filter(event):
        #may want to map some of these to the same function
        events = {
            QtCore.QEvent.Shortcut: ActionRecorder.record_shortcut,
            QtCore.QEvent.KeyPress: ActionRecorder.record_keypress,
            QtCore.QEvent.KeyRelease: ActionRecorder.record_keyrelease,
            QtCore.QEvent.MouseButtonDblClick: ActionRecorder.record_dblclick,
            QtCore.QEvent.MouseButtonPress: ActionRecorder.record_mouse_press,
            QtCore.QEvent.MouseButtonRelease: ActionRecorder.record_mouse_release,
            #'QEvent.MouseMove': record_mouse_move
            }
        events.get(event.type())(event)

    def record_shortcut(event):
        print('a')
        key3=event.key()
        command = {
            'Type': 'Shortcut',
            'Value': keys,
            'Value2': key2,
            'Value3': key3,
            }
        return command

    def record_keypress(event):
        print('b')
        focus=QtWidgets.QApplication.focusWidget()
        key=event.key()
        command = {
            'Type': 'Keypress',
            'Value': key,
            'Focus': focus,
            }
        return command

    def record_keyrelease(event):
        print('c')
        focus=QtWidgets.QApplication.focusWidget()
        key=event.key()
        command = {
            'Type': 'Keyrelease',
            'Value': key,
            'Focus': focus,
            }
        return command

    def record_dblclick(event):
        print('d')
        print("record double click called")

    def record_mouse_press(event):
        print('f')
        focus=QtWidgets.QApplication.focusWidget()
        localPos=event.localPos()
        button=event.button()
        command = {
            'Type': 'Mousepress',
            'Position': localPos,
            'Focus': focus,
            }

    def record_mouse_release(event):
        print("mouse release called")
        focus=QtWidgets.QApplication.focusWidget()
        #Unclear which is needed right now
        localPos=event.localPos()
        windowPos=event.windowPos()
        button=event.button()
        command = {
            'Type': 'Mousepress',
            'Position': localPos,
            'Focus': focus,
            }

    def record_mouse_move(event):
        print("mouse moved. Did not leave forwarding address")
        focus=QtWidgets.QApplication.focusWidget()
        localPos=event.localPos()
        button=event.button()
        command = {
            'Type': 'Mousepress',
            'Position': localPos,
            'Focus': focus,
            }

    
def make_recorder():
    recorder=ActionRecorder()
    QtWidgets.QApplication.instance().installEventFilter(recorder)
    print("Recorder installed")
    return recorder

def delete_recorder(recorder):
    QtWidgets.QApplication.instance().removeEventFilter(recorder)
