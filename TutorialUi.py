import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtCore, QtWidgets, QtGui
from FreeCAD import Qt

import os
import TutorialClasses

def getpath():
    print(os.path.dirname(QtCore.__file__))

def QT_TRANSLATE_NOOP(context,text):
    return text


class TutorialUi(QtWidgets.QWizard):
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
    class PassCommand(QtCore.QObject):
        newItem=QtCore.Signal(dict)
    
    def __init__(self, parent=None):
        super(ActionRecorder,self).__init__(parent)
        signal=self.PassCommand()
        self.newItem=signal.newItem
        signal.newItem.connect(CommandSelection.add_command)
        App.Console.PrintLog("init ActionRecorder \n")
        
    def __del__(self):
        super(ActionRecorder,self).__del__(parent)
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
            ActionRecorder.handle_filter(event,self.newItem)
        #keeps events from getting eaten by filter
        return False

    def handle_filter(event,signal):
        #may want to map some of these to the same function
        App.Console.PrintLog(event)
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
        print(command['Type'])
        signal.emit(command)
        

    def record_shortcut(event):
        #print('a')
        key3=event.key()
        command = {
            'Type': 'Shortcut',
            'Value': keys,
            'Value2': key2,
            'Value3': key3,
            }
        return command

    def record_keypress(event):
        #print('kp /n')
        focus=QtWidgets.QApplication.focusWidget()
        key=event.key()
        command = {
            'Type': 'Keypress',
            'Value': key,
            'Focus': focus,
            }
        return command

    def record_keyrelease(event):
        #print('kr /n')
        focus=QtWidgets.QApplication.focusWidget()
        key=event.key()
        command = {
            'Type': 'Keyrelease',
            'Value': key,
            'Focus': focus,
            }
        App.Console.PrintLog('kr() \n')
        return command

    def record_dblclick(event):
        #print('d /n')
        command = {
            'Type': 'Dblclick',
            }
        return command

    def record_mouse_press(event):
        #print('mp /n')
        focus=QtWidgets.QApplication.focusWidget()
        localPos=event.localPos()
        button=event.button()
        command = {
            'Type': 'Mousepress',
            'Position': localPos,
            'Focus': focus,
            }
        return command

    def record_mouse_release(event):
        #print("mouse release called /n")
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
        return command

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
        return command
    
def make_recorder():
    '''Creates/installs qevent filter to record ui input. Calling this function
    without assigning it to a variable crashes FreeCAD'''
    recorder=ActionRecorder(Gui.getMainWindow())
    Gui.getMainWindow().installEventFilter(recorder)
    #QtWidgets.QApplication.instance().installEventFilter(recorder)
    App.Console.PrintLog("Recorder installed \n")
    return recorder

def delete_recorder(recorder):
    Gui.getMainWindow().removeEventFilter(recorder)
    #QtWidgets.QApplication.instance().removeEventFilter(recorder)


class CommandSelection:
    def __init__(self):
        ui_path = os.path.join(os.path.dirname(__file__), "CommandSelection.ui")
        self.form = Gui.PySideUic.loadUi(ui_path)
        self.form.addCommand.clicked.connect(CommandSelection.command_to_step)
        self.form.addStep.clicked.connect(CommandSelection.step_to_tutorial)


    def record_commands():
        '''Starts recording ui commands. Calling this function without assigning
        it to a variable crashes FreeCAD'''
        ui=CommandSelection()
        ui.form.show()
        recorder=make_recorder()
        App.Console.PrintLog("ui up \n")

        #This line might be removable but is currently needed to ease testing
        return recorder

    @QtCore.Slot(dict)
    def add_command(self,command):
        self.form.Commands.addItem(command)
        print('ac')
        print(command)
        
    def command_to_step(self):
        print(self)
        stepCommands=self.form.Commands.selectedItems()
        step=TutorialClasses.Step.create(stepCommands)
        self.form.Steps.addItem(step)

    def step_to_tutorial(self):
        stepList=self.form.Steps.selectedItems()
        for step in stepList:
            TutorialClasses.add_step(step)
        
#cs=CommandSelection.record_commands()
#sdkgj
