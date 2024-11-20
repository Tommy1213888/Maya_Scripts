import maya.cmds as cmds

import baseCommand
import get_uiData

import maya_reload
maya_reload.refresh(baseCommand)
maya_reload.refresh(get_uiData)

class Connection:
    def __init__(self) -> None:
        self.base = baseCommand.base_commmand()
        self.data = get_uiData.data()

        self.stretch = ['Stretch']
        self.squeeze = ['Squeeze']
        self.stretch_driver_translate_attr = ['stretchDriverTx', 'stretchDriverTy', 'stretchDriverTz']
        self.stretch_driver_rotate_attr = ['stretchDriverRx', 'stretchDriverRy', 'stretchDriverRz']
        self.stretch_driver_scale_attr = ['stretchDriverSx', 'stretchDriverSy', 'stretchDriverSz']
        self.squeeze_driver_translate_attr = ['squeezeDriverTx', 'squeezeDriverTy', 'squeezeDriverTz']
        self.squeeze_driver_rotate_attr = ['squeezeDriverRx', 'squeezeDriverRy', 'squeezeDriverRz']
        self.squeeze_driver_scale_attr = ['squeezeDriverSx', 'squeezeDriverSy', 'squeezeDriverSz']

    def add_attr(self, mus_name:str, joint_count:int):

        selected_attr = self.data.get_selected_driver()

        skin_ctrls = [mus_name+'_skin_0'+str(i+1)+'_jnt_ctrl' for i in range(joint_count)]

        if selected_attr['translate'] == 'True':
            drv_attrs = self.stretch+self.stretch_driver_translate_attr+self.squeeze+self.squeeze_driver_translate_attr
        if selected_attr['rotate'] == 'True':
            drv_attrs = self.stretch+self.stretch_driver_translate_attr+self.stretch_driver_rotate_attr+self.squeeze+self.squeeze_driver_translate_attr+self.squeeze_driver_rotate_attr
        if selected_attr['scale'] == 'True':
            drv_attrs = self.stretch+self.stretch_driver_translate_attr+self.stretch_driver_rotate_attr+self.stretch_driver_scale_attr+self.squeeze+self.squeeze_driver_translate_attr+self.squeeze_driver_rotate_attr+self.squeeze_driver_scale_attr

        for ctrl in skin_ctrls:
            for attr in drv_attrs:
                if not cmds.attributeQuery(attr, node = ctrl, ex = True):
                    if attr == 'Stretch' or attr == 'Squeeze':
                        cmds.addAttr(ctrl, longName=attr, attributeType='enum', en='------------------', k = True)
                    else:
                        cmds.addAttr(ctrl, longName=attr, attributeType='double', dv = 1, keyable=True)

        return skin_ctrls
    
    def connect_translation(self, mus_name:str, distance_node:str, joint_count:int, sdk_grps:list):

        skin_ctrls = self.add_attr(mus_name, joint_count)
        # 获取当前距离，并创建节点将获取到的距离数值给还原为0
        distance = cmds.getAttr('{}.distance'.format(distance_node))
        dis_md = cmds.createNode('multiplyDivide', name = '{}_translate_dis_Md'.format(mus_name))
        dis_re = cmds.createNode('reverse',  name = '{}_translate_dis_Re'.format(mus_name))

        cmds.setAttr('{}.operation'.format(dis_md), 2)
        cmds.setAttr('{}.input2'.format(dis_md), float(distance), float(distance), float(distance))

        cmds.connectAttr('{}.distance'.format(distance_node), '{}.input1X'.format(dis_md))
        cmds.connectAttr('{}.outputX'.format(dis_md), '{}.inputX'.format(dis_re))

        # 创建判断节点，判断当前是挤压还是拉伸状态
        dis_cd = cmds.createNode('condition', name = mus_name+'_translate_dis_CD')
        cmds.setAttr('{}.operation'.format(dis_cd), 2)
        cmds.connectAttr('{}.outputX'.format(dis_re), '{}.firstTerm'.format(dis_cd))

        # 计算链接
        half_count = joint_count/2
        for i in range(joint_count):
            bdc = cmds.createNode('blendColors', name = mus_name+'_translate_stretch_squeeze_BDC')
            cmds.connectAttr('{}.outColorR'.format(dis_cd), '{}.blender'.format(bdc))

            stretch_coeff_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_stretch_translate_setCoeff_MD')
            suqeeze_coeff_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_squeeze_translate_setCoeff_MD')

            cmds.setAttr('{}.operation'.format(stretch_coeff_md), 1)
            cmds.setAttr('{}.operation'.format(suqeeze_coeff_md), 1)

            cmds.connectAttr('{}.stretchDriverTx'.format(skin_ctrls[i]), '{}.input1X'.format(stretch_coeff_md))
            cmds.connectAttr('{}.stretchDriverTy'.format(skin_ctrls[i]), '{}.input1Y'.format(stretch_coeff_md))
            cmds.connectAttr('{}.stretchDriverTz'.format(skin_ctrls[i]), '{}.input1Z'.format(stretch_coeff_md))
            cmds.connectAttr('{}.squeezeDriverTx'.format(skin_ctrls[i]), '{}.input1X'.format(suqeeze_coeff_md))
            cmds.connectAttr('{}.squeezeDriverTy'.format(skin_ctrls[i]), '{}.input1Y'.format(suqeeze_coeff_md))
            cmds.connectAttr('{}.squeezeDriverTz'.format(skin_ctrls[i]), '{}.input1Z'.format(suqeeze_coeff_md))

            cmds.connectAttr('{}.outputX'.format(stretch_coeff_md), '{}.color1R'.format(bdc))
            cmds.connectAttr('{}.outputY'.format(stretch_coeff_md), '{}.color1G'.format(bdc))
            cmds.connectAttr('{}.outputZ'.format(stretch_coeff_md), '{}.color1B'.format(bdc))

            cmds.connectAttr('{}.outputX'.format(suqeeze_coeff_md), '{}.color2R'.format(bdc))
            cmds.connectAttr('{}.outputY'.format(suqeeze_coeff_md), '{}.color2G'.format(bdc))
            cmds.connectAttr('{}.outputZ'.format(suqeeze_coeff_md), '{}.color2B'.format(bdc))

            zero_re = cmds.createNode('reverse', name = skin_ctrls[i]+'_translate_setZero_RE')
            reverse_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_translate_reverse_MD')
            calculate_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_translate_calculate_MD')
            output_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_translate_output_MD')

            cmds.setAttr('{}.input2'.format(reverse_md), -1,-1,-1)
            if i+1 <= half_count:
                calculate = i+1
            else:
                calculate = joint_count-i

            cmds.setAttr('{}.input2'.format(calculate_md), 1, calculate, 1)

            if i == 0 or i == joint_count-1:
                cmds.connectAttr('{}.output'.format(bdc), '{}.input'.format(zero_re))
                cmds.connectAttr('{}.output'.format(zero_re), '{}.input1'.format(reverse_md))
                cmds.connectAttr('{}.output'.format(reverse_md), '{}.input1'.format(calculate_md))
            else:
                cmds.connectAttr('{}.outputR'.format(bdc), '{}.inputX'.format(zero_re))
                cmds.connectAttr('{}.outputG'.format(bdc), '{}.input1Y'.format(calculate_md))
                cmds.connectAttr('{}.outputB'.format(bdc), '{}.inputZ'.format(zero_re))

                cmds.connectAttr('{}.outputX'.format(zero_re), '{}.input1X'.format(reverse_md))
                cmds.connectAttr('{}.outputZ'.format(zero_re), '{}.input1Z'.format(reverse_md))

                cmds.connectAttr('{}.outputX'.format(reverse_md), '{}.input1X'.format(calculate_md))
                cmds.connectAttr('{}.outputZ'.format(reverse_md), '{}.input1Z'.format(calculate_md))

            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1X'.format(output_md))
            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1Y'.format(output_md))
            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1Z'.format(output_md))

            cmds.connectAttr('{}.output'.format(calculate_md), '{}.input2'.format(output_md))

            cmds.connectAttr('{}.output'.format(output_md), '{}.translate'.format(sdk_grps[i]))

            cmds.select(cl=True)

    def connect_rotate(self, mus_name:str, distance_node:str, joint_count:int, sdk_grps:list):

        skin_ctrls = self.add_attr(mus_name, joint_count)
        # 获取当前距离，并创建节点将获取到的距离数值给还原为0
        distance = cmds.getAttr('{}.distance'.format(distance_node))
        dis_md = cmds.createNode('multiplyDivide', name = '{}_rotate_dis_Md'.format(mus_name))
        dis_re = cmds.createNode('reverse',  name = '{}_rotate_dis_Re'.format(mus_name))

        cmds.setAttr('{}.operation'.format(dis_md), 2)
        cmds.setAttr('{}.input2'.format(dis_md), float(distance), float(distance), float(distance))

        cmds.connectAttr('{}.distance'.format(distance_node), '{}.input1X'.format(dis_md))
        cmds.connectAttr('{}.outputX'.format(dis_md), '{}.inputX'.format(dis_re))

        # 创建判断节点，判断当前是挤压还是拉伸状态
        dis_cd = cmds.createNode('condition', name = mus_name+'_rotate_dis_CD')
        cmds.setAttr('{}.operation'.format(dis_cd), 2)
        cmds.connectAttr('{}.outputX'.format(dis_re), '{}.firstTerm'.format(dis_cd))

        # 计算链接
        for i in range(joint_count):
            bdc = cmds.createNode('blendColors', name = mus_name+'_rotate_stretch_squeeze_BDC')
            cmds.connectAttr('{}.outColorR'.format(dis_cd), '{}.blender'.format(bdc))

            stretch_coeff_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_stretch_rotate_setCoeff_MD')
            suqeeze_coeff_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_squeeze_rotate_setCoeff_MD')

            cmds.setAttr('{}.operation'.format(stretch_coeff_md), 1)
            cmds.setAttr('{}.operation'.format(suqeeze_coeff_md), 1)

            cmds.connectAttr('{}.stretchDriverRx'.format(skin_ctrls[i]), '{}.input1X'.format(stretch_coeff_md))
            cmds.connectAttr('{}.stretchDriverRy'.format(skin_ctrls[i]), '{}.input1Y'.format(stretch_coeff_md))
            cmds.connectAttr('{}.stretchDriverRz'.format(skin_ctrls[i]), '{}.input1Z'.format(stretch_coeff_md))
            cmds.connectAttr('{}.squeezeDriverRx'.format(skin_ctrls[i]), '{}.input1X'.format(suqeeze_coeff_md))
            cmds.connectAttr('{}.squeezeDriverRy'.format(skin_ctrls[i]), '{}.input1Y'.format(suqeeze_coeff_md))
            cmds.connectAttr('{}.squeezeDriverRz'.format(skin_ctrls[i]), '{}.input1Z'.format(suqeeze_coeff_md))

            cmds.connectAttr('{}.outputX'.format(stretch_coeff_md), '{}.color1R'.format(bdc))
            cmds.connectAttr('{}.outputY'.format(stretch_coeff_md), '{}.color1G'.format(bdc))
            cmds.connectAttr('{}.outputZ'.format(stretch_coeff_md), '{}.color1B'.format(bdc))

            cmds.connectAttr('{}.outputX'.format(suqeeze_coeff_md), '{}.color2R'.format(bdc))
            cmds.connectAttr('{}.outputY'.format(suqeeze_coeff_md), '{}.color2G'.format(bdc))
            cmds.connectAttr('{}.outputZ'.format(suqeeze_coeff_md), '{}.color2B'.format(bdc))

            zero_re = cmds.createNode('reverse', name = skin_ctrls[i]+'_rotate_setZero_RE')
            reverse_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_rotate_reverse_MD')
            calculate_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_rotate_calculate_MD')
            output_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_rotate_output_MD')

            cmds.setAttr('{}.input2'.format(reverse_md), -1,-1,-1)

            cmds.setAttr('{}.input2'.format(calculate_md), 1, 1, 1)

            cmds.connectAttr('{}.output'.format(bdc), '{}.input'.format(zero_re))
            cmds.connectAttr('{}.output'.format(zero_re), '{}.input1'.format(reverse_md))
            cmds.connectAttr('{}.output'.format(reverse_md), '{}.input1'.format(calculate_md))

            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1X'.format(output_md))
            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1Y'.format(output_md))
            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1Z'.format(output_md))

            cmds.connectAttr('{}.output'.format(calculate_md), '{}.input2'.format(output_md))

            cmds.connectAttr('{}.output'.format(output_md), '{}.rotate'.format(sdk_grps[i]))

            cmds.select(cl=True)

    def connect_scale(self, mus_name:str, distance_node:str, joint_count:int, sdk_grps:list):

        skin_ctrls = self.add_attr(mus_name, joint_count)
        # 获取当前距离，并创建节点将获取到的距离数值给还原为0
        distance = cmds.getAttr('{}.distance'.format(distance_node))
        dis_md = cmds.createNode('multiplyDivide', name = '{}_scale_dis_Md'.format(mus_name))
        dis_re = cmds.createNode('reverse',  name = '{}_scale_dis_Re'.format(mus_name))

        cmds.setAttr('{}.operation'.format(dis_md), 2)
        cmds.setAttr('{}.input2'.format(dis_md), float(distance), float(distance), float(distance))

        cmds.connectAttr('{}.distance'.format(distance_node), '{}.input1X'.format(dis_md))
        cmds.connectAttr('{}.outputX'.format(dis_md), '{}.inputX'.format(dis_re))

        # 创建判断节点，判断当前是挤压还是拉伸状态
        dis_cd = cmds.createNode('condition', name = mus_name+'_scale_dis_CD')
        cmds.setAttr('{}.operation'.format(dis_cd), 2)
        cmds.connectAttr('{}.outputX'.format(dis_re), '{}.firstTerm'.format(dis_cd))

        # 计算链接
        for i in range(joint_count):
            bdc = cmds.createNode('blendColors', name = mus_name+'_scale_stretch_squeeze_BDC')
            cmds.connectAttr('{}.outColorR'.format(dis_cd), '{}.blender'.format(bdc))

            stretch_coeff_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_stretch_scale_setCoeff_MD')
            suqeeze_coeff_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_squeeze_scale_setCoeff_MD')

            cmds.setAttr('{}.operation'.format(stretch_coeff_md), 1)
            cmds.setAttr('{}.operation'.format(suqeeze_coeff_md), 1)

            cmds.connectAttr('{}.stretchDriverSx'.format(skin_ctrls[i]), '{}.input1X'.format(stretch_coeff_md))
            cmds.connectAttr('{}.stretchDriverSy'.format(skin_ctrls[i]), '{}.input1Y'.format(stretch_coeff_md))
            cmds.connectAttr('{}.stretchDriverSz'.format(skin_ctrls[i]), '{}.input1Z'.format(stretch_coeff_md))
            cmds.connectAttr('{}.squeezeDriverSx'.format(skin_ctrls[i]), '{}.input1X'.format(suqeeze_coeff_md))
            cmds.connectAttr('{}.squeezeDriverSy'.format(skin_ctrls[i]), '{}.input1Y'.format(suqeeze_coeff_md))
            cmds.connectAttr('{}.squeezeDriverSz'.format(skin_ctrls[i]), '{}.input1Z'.format(suqeeze_coeff_md))

            cmds.connectAttr('{}.outputX'.format(stretch_coeff_md), '{}.color1R'.format(bdc))
            cmds.connectAttr('{}.outputY'.format(stretch_coeff_md), '{}.color1G'.format(bdc))
            cmds.connectAttr('{}.outputZ'.format(stretch_coeff_md), '{}.color1B'.format(bdc))

            cmds.connectAttr('{}.outputX'.format(suqeeze_coeff_md), '{}.color2R'.format(bdc))
            cmds.connectAttr('{}.outputY'.format(suqeeze_coeff_md), '{}.color2G'.format(bdc))
            cmds.connectAttr('{}.outputZ'.format(suqeeze_coeff_md), '{}.color2B'.format(bdc))

            zero_re = cmds.createNode('reverse', name = skin_ctrls[i]+'_scale_setZero_RE')
            reverse_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_scale_reverse_MD')
            calculate_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_scale_calculate_MD')
            output_md = cmds.createNode('multiplyDivide', name = skin_ctrls[i]+'_scale_output_MD')
            output_pla = cmds.createNode('plusMinusAverage', name = skin_ctrls[i]+'_scale_output_PLA')

            cmds.setAttr('{}.input2'.format(reverse_md), -1,-1,-1)

            cmds.setAttr('{}.input2'.format(calculate_md), 1, 1, 1)

            cmds.connectAttr('{}.output'.format(bdc), '{}.input'.format(zero_re))
            cmds.connectAttr('{}.output'.format(zero_re), '{}.input1'.format(reverse_md))
            cmds.connectAttr('{}.output'.format(reverse_md), '{}.input1'.format(calculate_md))

            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1X'.format(output_md))
            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1Y'.format(output_md))
            cmds.connectAttr('{}.outputX'.format(dis_re), '{}.input1Z'.format(output_md))

            cmds.connectAttr('{}.output'.format(calculate_md), '{}.input2'.format(output_md))

            cmds.connectAttr('{}.output'.format(output_md), '{}.input3D[0]'.format(output_pla))
            cmds.setAttr('{}.input3D[1]'.format(output_pla), 1,1,1)
            cmds.connectAttr('{}.output3D'.format(output_pla), '{}.scale'.format(sdk_grps[i]))

            cmds.select(cl=True)


