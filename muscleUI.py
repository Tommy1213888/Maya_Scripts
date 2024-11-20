# -*- coding: utf-8 -*-
'''
Description:
Author:	chuanqin
E-mail:	6744035640@qq.com
Version:1.0
Date:2024-08-16
'''
import maya.cmds as cmds
import muscleFunction
import muscleConnection
import maya_reload
maya_reload.refresh(muscleFunction)
maya_reload.refresh(muscleConnection)

class muscle_UI():
    def __init__(self) -> None:
        self.mus_command = muscleFunction.muscle()
        self.connect = muscleConnection.Connection()
        self.title = 'Muscle'
        self.winID = 'muscleWin'

    def muscle_ui(self):

        if cmds.window(self.winID, exists=True):
            cmds.deleteUI(self.winID)

        cmds.window(self.winID, title = self.title, widthHeight=(400, 400), rtf = True)
        cmds.columnLayout(adj = True)
        cmds.textFieldGrp('mus_name', label = 'Muscle Name:', cw2 = (120, 280))
        cmds.textFieldButtonGrp('mus_start', label = 'Start Joint:', buttonLabel = 'Load', cw3 = (120, 230, 50), buttonCommand = lambda*args:self.mus_command.load_selected_joints('start'))
        cmds.textFieldButtonGrp('mus_end', label = 'End joint:', buttonLabel = 'Load', cw3 = (120, 230, 50), buttonCommand = lambda*args:self.mus_command.load_selected_joints('end'))
        cmds.separator(h = 5, style = 'in')
        cmds.separator(h = 5, style = 'in')
        cmds.setParent('..')
        cmds.rowColumnLayout(nc = 3, cw = [(1, 130), (2, 130), (3, 130)])
        cmds.textFieldGrp('mus_wid', label = 'Muscle Width:', tx = 2, cw2 = (100, 30))
        cmds.textFieldGrp('mus_hei', label = 'Muscle Height:', tx = 10, cw2 = (100, 30))
        cmds.textFieldGrp('jnt_count', label = 'Joints Count:', tx = 6, cw2 = (100, 30))
        cmds.setParent('..')
        cmds.separator(h = 5, style = 'in')
        cmds.rowColumnLayout(nc = 4, cw = [(1, 100), (2, 100), (3, 100), (4, 100)])
        cmds.text('Driver:')
        cmds.checkBox('translate', label = 'Translate', value = True)
        cmds.checkBox('rotate', label = 'Rotate')
        cmds.checkBox('scale', label = 'Scale')
        cmds.setParent('..')
        cmds.separator(h = 5, style = 'in')
        cmds.columnLayout(adj = True)
        cmds.button(label = 'Create Muscle', h = 40, command = lambda*args:self.mus_command.create_muscle_system())
        cmds.separator(h = 5, style = 'in')
        cmds.button(label = 'Connect Muscle', h = 40, command = lambda*args:self.mus_command.connect_muscle_driver())
        cmds.setParent('..')
        cmds.separator(h = 5, style = 'in')
        cmds.rowColumnLayout(nc = 2, cw = [(1, 200), (2, 200)], cs=[(1, 0), (2, 5)])
        cmds.button(l='Set Stretch', h=40, command = lambda*args:self.mus_command.set_muscle_stretch_squeeze('stretch'))
        cmds.button(l='Set Squeeze', h=40, command = lambda*args:self.mus_command.set_muscle_stretch_squeeze('squeeze'))
        cmds.separator(h = 5, style = 'in')
        cmds.separator(h = 5, style = 'in')
        cmds.textFieldGrp('mirror_search', l = 'Search:', tx='_L', cw2=(50, 150))
        cmds.textFieldGrp('mirror_replace', l = 'Replace:', tx='_R', cw2=(50, 150))
        cmds.setParent('..')
        cmds.columnLayout(adj = 1)
        cmds.button(l='Mirror Muscle System', h = 50, command = lambda*args:self.mus_command.mirror_muscle_system())
        cmds.separator(h = 5, style = 'in')
        cmds.setParent('..')
        cmds.rowColumnLayout(nc = 2, cw = [(1, 200), (2, 200)], cs=[(1, 0), (2, 5)])
        cmds.button(l='Delete Current Muscle', h=40, command = lambda*args:self.mus_command.clear_current_muscle())
        cmds.button(l='Delete ALL Muscle', h=40,ann='此功能将不管不顾的删除当前场景中的所有模拟肌肉系统\n请慎重！！！',  command = lambda*args:self.mus_command.clear_all_muscle())
        cmds.setParent('..')


        cmds.showWindow()


if __name__ == '__main__':
    win = muscle_UI()
    win.muscle_ui()
