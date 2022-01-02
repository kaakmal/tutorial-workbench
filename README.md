# tutorial-workbench
Create and run tutorials in FreeCAD

Uses scripted python objects to record tutorial and step information. Recording user events and playing a created tutorial are done with PySide/Qt. 
This is very much a work in progress at the moment. It does technically work now, but it's not at a level to make it worth seriously using for a tutorial yet.  

## Current State:
* Base classes for tutorial functionality established
* Can add new steps to tutorials
* Can add information to tutorial via tree (eg, instructions, author name, FreeCAD version)
* Can convert tutorial to QWizard that is playable
* Can play QWizard
* Multi-command steps now possible
* Can record user events
## Next Steps:
* Create workbench buttons/interface
* Create interface to allow manipulation/selection of commands to go into steps
* Make GUI elements highlight
## Later Steps:
* Automatically record version/language info
* Have tutorial highlight part features (e.g., faces, edges)
* Show where to click with cursor
* Have option to show keyboard shortcuts
* Add hints
* Make hints show up conditionally based on user actions
* Be able to export PDF of tutorial
* Make tutorial automatically advance when step successfully completed

