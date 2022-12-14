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
    
    def __init__(self):
        #Makes window top level window
        super(ActionRecorder, self).__init__(Gui.getMainWindow())
        self.cs=CommandSelection(self)
        self.cs.form.show()
        App.Console.PrintLog("init ActionRecorder \n")
        
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
            ActionRecorder.handle_filter(self,event)
        #keeps events from getting eaten by filter
        return False

    def handle_filter(self,event):
        '''Adds command to command list based on event type'''
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
        commandDictItem=self.cs.add_command(command)
        self.cs.commands[commandDictItem[0]]=commandDictItem[1]
        

    def record_shortcut(event):
        '''Creates command dict for keyboard shortcut event'''
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
        '''Creates command dict for keypress event'''
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
        '''Creates command dict for key release event'''
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
        '''Creates command dict for double click event'''
        #print('d /n')
        command = {
            'Type': 'Dblclick',
            }
        return command

    def record_mouse_press(event):
        '''Creates command dict for mouse press event'''
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
        '''Creates command dict for mouse release event'''
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
        '''Creates command dict for mouse move event'''
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
    recorder=ActionRecorder()
    Gui.getMainWindow().installEventFilter(recorder)
    #QtWidgets.QApplication.instance().installEventFilter(recorder)
    App.Console.PrintLog("Recorder installed \n")
    return recorder

def delete_recorder(recorder):
    #currently failing to remove recorder ???
    Gui.getMainWindow().removeEventFilter(recorder)
    #QtWidgets.QApplication.instance().removeEventFilter(recorder)


class CommandSelection:
    '''Creates UI for command selection'''
    def __init__(self,recorder):
        self.commands={}
        self.recorder=recorder
        ui_path = os.path.join(os.path.dirname(__file__), "CommandSelection.ui")
        self.form = Gui.PySideUic.loadUi(ui_path)
        self.form.addCommand.clicked.connect(CommandSelection.command_to_step)
        self.form.addStep.clicked.connect(CommandSelection.step_to_tutorial)
        self.form.Close.clicked.connect(delete_recorder(self.recorder))
        self.form.show()

    def add_command(self,command):
        '''Adds command dict to list of commands'''
        commandName=str(command['Type'])+str(command['Focus'])
        commandData=[commandName,command]
        self.form.Commands.addItem(commandName)
        print("command added")
        return commandData
        
    def command_to_step(self):
        '''Makes tutorial step out of selected command'''
        print(self)
        stepCommands=self.form.Commands.selectedItems()
        step=TutorialClasses.Step.create(stepCommands)
        self.form.Steps.addItem(step)

    def step_to_tutorial(self):
        '''Adds step to tutorial'''
        stepList=self.form.Steps.selectedItems()
        for step in stepList:
            TutorialClasses.add_step(step)
        
#cs=CommandSelection.record_commands()
#sdkgj
