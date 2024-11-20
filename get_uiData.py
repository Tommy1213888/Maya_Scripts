import maya.cmds as cmds
import baseCommand
import maya_reload
maya_reload.refresh(baseCommand)

class data:
    def __init__(self) -> None:
        self.base = baseCommand.base_commmand()

    def get_muscle_name(self):
        '''
        Description:get munscle name from ui with user input
        Parme:
        '''
        mus_name = cmds.textFieldGrp('mus_name', query = True, text = True)
        if mus_name:
            return mus_name
        else:
            cmds.error('Plese input muscle name!')
            return
        
    def get_start_joint(self):
        '''
        Description:get munscle name from ui with user input
        Parme:
        '''
        start_joint = cmds.textFieldGrp('mus_start', query = True, text = True)
        if start_joint:
            return start_joint
        else:
            cmds.warning('have no start joint to loaded!')
            return None
    def get_end_joint(self):
        '''
        Description:get munscle name from ui with user input
        Parme:
        '''
        end_joint = cmds.textFieldGrp('mus_end', query = True, text = True)
        if end_joint:
            return end_joint
        else:
            cmds.warning('have no start joint to loaded!')
            return None
        
    def get_muscle_height(self):

        start_joint = self.get_start_joint()
        end_joint = self.get_end_joint()

        if start_joint == None and end_joint == None:
            mus_height = cmds.textFieldGrp('mus_hei', query = True, tx=True)
        else:
            start_loc = cmds.spaceLocator(name = 'distance_start_loc')[0]
            end_loc = cmds.spaceLocator(name = 'distance_end_loc')[0]
            cmds.matchTransform(start_loc, start_joint)
            cmds.matchTransform(end_loc, end_joint)

            distanceNode, distanceTrans = self.base.create_distanceDim(name='distance_temp', start=start_loc, end=end_loc)
            mus_height = cmds.getAttr('{}.distance'.format(distanceNode))

            cmds.delete(start_loc)
            cmds.delete(end_loc)

        return mus_height
    
    def get_muscle_width(self):

        return cmds.textFieldGrp('mus_wid', query = True, tx=True)
    
    def get_joints_count(self):
        return int(cmds.textFieldGrp('jnt_count', query = True, tx=True))
    
    def get_selected_driver(self):

        value0 = cmds.checkBox('translate', query = True, value = True)
        value1 = cmds.checkBox('rotate', query = True, value = True)
        value2 = cmds.checkBox('scale', query = True, value = True)

        value_dict = {}
        if value0 == True:
            value_dict['translate'] = 'True'
        else:
            value_dict['translate'] = 'False'
        
        if value1 == True:
            value_dict['rotate'] = 'True'
        else:
            value_dict['rotate'] = 'False'
        
        if value2 == True:
            value_dict['scale'] = 'True'
        else:
            value_dict['scale'] = 'False'

        return value_dict

    def get_mirror_name(self):

        serach_letter = cmds.textFieldGrp('mirror_search', query = True, tx = True)
        replace_letter = cmds.textFieldGrp('mirror_replace', query = True, tx = True)

        return serach_letter, replace_letter