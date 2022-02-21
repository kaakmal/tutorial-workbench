import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtCore, QtWidgets, QtGui
from FreeCAD import Qt

import TutorialClasses

import os
def QT_TRANSLATE_NOOP(context,text):
    return text


class TutorialUi(QtGui.QWizard):
    '''Creates QWizard that will function as tutorial instructions'''
    def __init__(self):
        super(TutorialUi,self).__init__()
        setOption(HaveHelpButton,True)

    def create(tutorial,qwizard):
        stepList=[]
        if Gui.Selection.hasSelection():
            selected=Gui.Selection.getSelection()
            for obj in selected:
                if obj.OutList != []:
                    stepList=obj.OutList
                    break
        for step in stepList:
            page=QtGui.QWizardPage()
            if step.Cluster != '':
                page.setTitle(step.Cluster)
            else:
                page.setTitle(tutorial.Title)
            page.setSubTitle(step.Instruction)
            qwizard.addPage(page)
        return qwizard

    def showHelp(self):
        message = Qt.translate('TutorialWB',
                               'You have ventured beyond the Lands We Know')
def run_tutorial():
    '''Creates then opens QWizard that is the tutorial'''
    try:
        ui=TutorialUi.create(Gui.Selection.getSelection()[0],QtGui.QWizard())
        ui.exec()
    except IndexError:
        App.Console.PrintMessage(Qt.translate('TutorialWB','No tutorial selected'))


class ActionRecorder(QtCore.QObject):
    '''
    Records user inputs to put into steps of tutorial using Qt event filter
    '''
    newItem=QtCore.Signal(dict)
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

    def handle_filter(self, event):
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
        command=events.get(event.type())(event)
        self.newItem.emit(command)
        

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


class CommandSelection:
    ui_path = os.path.join(os.path.dirname(__file__), "CommandSelection.ui")
    self.form = FreeCADGui.PySideUic.loadUi(ui_path)

    def record_commands():
        ui=CommandSelection()
        recorder=make_recorder()

    @QtCore.Slot(dict)
    def add_command(command):
        self.form.Commands.addItem(command)
        print(command)
        
    def command_to_step():
        stepCommands=self.form.Commands.selectedItems()
        step=TutorialClasses.Step.create(stepCommands)
        self.form.Steps.addItem(step)
