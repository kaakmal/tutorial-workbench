import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui
from FreeCAD import Qt

def QT_TRANSLATE_NOOP(context,text):
    return text

class TutorialUi(QtGui.QWizard):
    '''Creates QWizard that will function as tutorial instructions'''
    def __init__(self):
        super(TutorialUi,self).__init__()
        self.HaveHelpButton()

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

ui=TutorialUi.create(Gui.Selection.getSelection()[0],QtGui.QWizard())
ui.exec()
