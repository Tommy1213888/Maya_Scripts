# -*- coding: utf-8 -*-
'''
Description:
Author:	chuanqin
E-mail:	6744035640@qq.com
Version:1.0
Date:2024-09-05
'''
import os

try:
    import maya.cmds as cmds
    import maya.mel as mel
    thisIs_maya = True

except ImportError:
    thisIs_maya = False

def onMayaDroppedPythonFile(*args, **kwargs):

    pass

def dragToInstall():

    filePath = os.path.abspath(os.path.dirname(__file__))

    icon = os.path.join(filePath, 'icon')

    iconPath = os.path.normpath(icon)

    if not os.path.exists(iconPath):
        raise IOError('Can not find {}'.format(iconPath))
    
    command = """\
import os
import sys

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')

if r'{path}' not in sys.path:
    sys.path.append(r'{path}')

import muscleUI

muscle = muscleUI.muscle_UI()
muscle.muscle_ui()
"""

    command = command.format(path = filePath)

    shelf = mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = cmds.tabLayout(shelf, query = True, selectTab = True)

    cmds.shelfButton(
        command = command,
        ann = 'Muscle system Tools',
        sourceType = 'Python',
        image = os.path.join(iconPath, 'muscle.png'),
        parent = parent
    )

if thisIs_maya:
    dragToInstall()