import maya.cmds as cmds
import get_uiData

class setDriver:

    def __init__(self) -> None:
        self.data = get_uiData.data()

    def get_name_list(self, mus_name:str, joint_count:int, modality:str, transform:str):
        '''
        Description:获取当前所需要的一些名称(控制器、组、节点)
        Parme:
            mus_name：肌肉名称
            joint_count：骨骼数量
            modality：挤压或拉伸
                ['stretch', 'squeeze']
            transform:位移属性
                ['translate', 'rotate', 'scale']
        '''
        ctrl_list = []
        sdk_grps_list = []
        coeff_node_list = []

        for i in range(joint_count):
            ctrl_list.append(mus_name+'_skin_0{}_jnt_ctrl'.format(i+1))
            sdk_grps_list.append(mus_name+'_skin_0{}_jnt_ctrl_SDKgrp'.format(i+1))
            coeff_node_list.append(mus_name+'_skin_0{0}_jnt_ctrl_{1}_{2}_setCoeff_MD'.format((i+1), modality, transform))

        return ctrl_list, sdk_grps_list, coeff_node_list

    def set_translate(self, mus_name:str, joint_count:int, modality:str, old_distance:float, new_distance:float):
        ctrl_list, sdk_grps_list, coeff_node_list = self.get_name_list(mus_name, joint_count, modality, 'translate')

        selected_driver = self.data.get_selected_driver()
        attrs = ['input2X', 'input2Y', 'input2Z']
        if selected_driver['rotate'] == 'True':
            ctrl_rotate_list, sdk_rotate_list, coeff_rotate_list = self.get_name_list(mus_name, joint_count, modality, 'rotate')
        if selected_driver['scale'] == 'True':
            ctrl_scale_list, sdk_scale_list, coeff_scale_list = self.get_name_list(mus_name, joint_count, modality, 'scale')

        if selected_driver['translate'] == 'False':
            cmds.warning('当前未选中平移属性，无法设置')
            return
        
        else:
            divisor = (old_distance-new_distance)/old_distance# 获取当前的系数
            for i in range(joint_count):
                temp_loc = cmds.spaceLocator(name = 'temp_translate_loc{:02d}'.format(i+1))
                cmds.matchTransform(temp_loc, ctrl_list[i])
                cmds.setAttr('{}.input2'.format(coeff_node_list[i]), 1,1,1)
                if selected_driver['rotate'] == 'True':
                    rotate = cmds.getAttr('{}.rotate'.format(ctrl_rotate_list[i]))[0]
                    rotate_coeff = cmds.getAttr('{}.input2'.format(coeff_rotate_list[i]))[0]
                    cmds.setAttr('{}.input2'.format(coeff_rotate_list[i]), 1,1,1)
                if selected_driver['scale'] == 'True':
                    scale = cmds.getAttr('{}.scale'.format(ctrl_scale_list[i]))[0]
                    scale_coeff = cmds.getAttr('{}.input2'.format(coeff_scale_list[i]))[0]
                    cmds.setAttr('{}.input2'.format(coeff_scale_list[i]), 1,1,1)
                cmds.matchTransform(ctrl_list[i], temp_loc)
                ctrl_translate_values = cmds.getAttr('{}.translate'.format(ctrl_list[i]))[0]
                sdk_translate_values = cmds.getAttr('{}.translate'.format(sdk_grps_list[i]))[0]
                for j in range(len(ctrl_translate_values)):
                    if ctrl_translate_values[j] == 0.0:
                        continue
                    else:
                        if sdk_translate_values[j] == 0:
                            coeff = (float(ctrl_translate_values[j])/divisor)+1
                        else:
                            coeff = (float(ctrl_translate_values[j])+float(sdk_translate_values[j]))/float(sdk_translate_values[j])
                        
                        cmds.setAttr('{}.{}'.format(coeff_node_list[i], attrs[j]), coeff)
                cmds.setAttr('{}.translate'.format(ctrl_list[i]), 0,0,0)
                if selected_driver['rotate'] == 'True':
                    cmds.setAttr('{}.rotate'.format(ctrl_rotate_list[i]), rotate[0], rotate[1], rotate[2])
                    cmds.setAttr('{}.input2'.format(coeff_rotate_list[i]), rotate_coeff[0], rotate_coeff[1], rotate_coeff[2])
                
                if selected_driver['scale'] == 'True':
                    cmds.setAttr('{}.scale'.format(ctrl_scale_list[i]), scale[0], scale[1], scale[2])
                    cmds.setAttr('{}.input2'.format(coeff_scale_list[i]), scale_coeff[0], scale_coeff[1], scale_coeff[2])
                cmds.refresh(cv=True)
                cmds.delete(temp_loc)


    def set_rotate(self, mus_name:str, joint_count:int, modality:str, old_distance:float, new_distance:float):

        ctrl_list, sdk_grps_list, coeff_node_list = self.get_name_list(mus_name, joint_count, modality, 'rotate')

        selected_driver = self.data.get_selected_driver()
        attrs = ['input2X', 'input2Y', 'input2Z']
        if selected_driver['rotate'] == 'False':
            cmds.warning('当前未选中旋转属性，无法设置')
            return
        
        else:
            divisor = (old_distance-new_distance)/old_distance# 获取当前的系数
            for i in range(joint_count):
                rotate_temp_loc = cmds.spaceLocator(name = 'temp_rotate_loc{:02d}'.format(i+1))
                cmds.matchTransform(rotate_temp_loc, ctrl_list[i])
                cmds.setAttr('{}.input2'.format(coeff_node_list[i]), 1,1,1)
                cmds.matchTransform(ctrl_list[i], rotate_temp_loc)

                ctrl_rotate_values = cmds.getAttr('{}.rotate'.format(ctrl_list[i]))[0]
                # sdk_rotate_values = cmds.getAttr('{}.rotate'.format(sdk_grps_list[i]))[0]
                for j in range(len(ctrl_rotate_values)):
                    if ctrl_rotate_values[j] == 0.0:
                        continue
                    else:
                        coeff = (float(ctrl_rotate_values[j])/divisor)+1
                        
                        cmds.setAttr('{}.{}'.format(coeff_node_list[i], attrs[j]), coeff)
                cmds.setAttr('{}.rotate'.format(ctrl_list[i]), 0,0,0)
                cmds.delete(rotate_temp_loc)

    def set_scale(self, mus_name:str, joint_count:int, modality:str, old_distance:float, new_distance:float):

        ctrl_list, sdk_grps_list, coeff_node_list = self.get_name_list(mus_name, joint_count, modality, 'scale')

        selected_driver = self.data.get_selected_driver()
        attrs = ['input2X', 'input2Y', 'input2Z']
        if selected_driver['scale'] == 'False':
            cmds.warning('当前未选中缩放属性，无法设置')
            return
        
        else:
            divisor = (old_distance-new_distance)/old_distance# 获取当前的系数
            for i in range(joint_count):
                scale_temp_loc = cmds.spaceLocator(name = 'temp_scale_loc{:02d}'.format(i+1))
                cmds.matchTransform(scale_temp_loc, ctrl_list[i])
                cmds.setAttr('{}.input2'.format(coeff_node_list[i]), 1,1,1)
                cmds.matchTransform(ctrl_list[i], scale_temp_loc)

                ctrl_scale_values = cmds.getAttr('{}.scale'.format(ctrl_list[i]))[0]
                sdk_scale_values = cmds.getAttr('{}.scale'.format(sdk_grps_list[i]))[0]
                for j in range(len(ctrl_scale_values)):
                    if ctrl_scale_values[j] == 1.0:
                        continue
                    elif sdk_scale_values[j] == 1.0:
                        coeff = ((float(ctrl_scale_values[j])-1)/divisor)+1
                        cmds.setAttr('{}.{}'.format(coeff_node_list[i], attrs[j]), coeff)
                    else:
                        coeff = sdk_scale_values[j]+((float(ctrl_scale_values[j])-1)/divisor)
                        cmds.setAttr('{}.{}'.format(coeff_node_list[i], attrs[j]), coeff)
                cmds.setAttr('{}.scale'.format(ctrl_list[i]), 1,1,1)
                cmds.delete(scale_temp_loc)



