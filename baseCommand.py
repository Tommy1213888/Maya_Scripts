from turtle import shapesize
import maya.cmds as cmds

class base_commmand:

    def __init__(self) -> None:
        self.knot = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21, 22, 23, 24, 25, 26,
                     27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52]
        
        self.point = [(0, 1, 0),(0, 0.92388000000000003, 0.382683),(0, 0.70710700000000004, 0.70710700000000004),(0, 0.382683, 0.92388000000000003),(0, 0, 1),\
                    (0, -0.382683, 0.92388000000000003),(0, -0.70710700000000004, 0.70710700000000004),(0, -0.92388000000000003, 0.382683),(0, -1, 0),\
                    (0, -0.92388000000000003, -0.382683),(0, -0.70710700000000004, -0.70710700000000004),(0, -0.382683, -0.92388000000000003),(0, 0, -1),\
                    (0, 0.382683, -0.92388000000000003),(0, 0.70710700000000004, -0.70710700000000004),(0, 0.92388000000000003, -0.382683),(0, 1, 0),\
                    (0.382683, 0.92388000000000003, 0),(0.70710700000000004, 0.70710700000000004, 0),(0.92388000000000003, 0.382683, 0),(1, 0, 0),\
                    (0.92388000000000003, -0.382683, 0),(0.70710700000000004, -0.70710700000000004, 0),(0.382683, -0.92388000000000003, 0),(0, -1, 0),\
                    (-0.382683, -0.92388000000000003, 0),(-0.70710700000000004, -0.70710700000000004, 0),(-0.92388000000000003, -0.382683, 0),(-1, 0, 0),\
                    (-0.92388000000000003, 0.382683, 0),(-0.70710700000000004, 0.70710700000000004, 0),(-0.382683, 0.92388000000000003, 0),(0, 1, 0),\
                    (0, 0.92388000000000003, -0.382683),(0, 0.70710700000000004, -0.70710700000000004),(0, 0.382683, -0.92388000000000003),(0, 0, -1),\
                    (-0.382683, 0, -0.92388000000000003),(-0.70710700000000004, 0, -0.70710700000000004),(-0.92388000000000003, 0, -0.382683),(-1, 0, 0),\
                    (-0.92388000000000003, 0, 0.382683),(-0.70710700000000004, 0, 0.70710700000000004),(-0.382683, 0, 0.92388000000000003),(0, 0, 1),\
                    (0.382683, 0, 0.92388000000000003),(0.70710700000000004, 0, 0.70710700000000004),(0.92388000000000003, 0, 0.382683),(1, 0, 0),\
                    (0.92388000000000003, 0, -0.382683),(0.70710700000000004, 0, -0.70710700000000004),(0.382683, 0, -0.92388000000000003),(0, 0, -1)]

    def create_joints(self, jointName:str):
        '''
        Description:创建骨骼函数，判断场景中是否有同名物体，若没有则创建骨骼
        Parme:
            jointName: str , 指定骨骼名称
        '''
        if cmds.objExists(jointName):
            cmds.error('{} are already exists, plese use another name!'.format(jointName))
            return
        else:
            joint_name = cmds.joint(name = jointName, position = (0,0,0))
            cmds.select(cl = True)
            return joint_name
        
    def create_empty_group(self, groupName:str):

        if cmds.objExists(groupName):
            cmds.warning('{0} already exists, skip it!'.format(groupName))
        else:
            group = cmds.group(empty = True, name = groupName)
            return group
        
    def create_FK_ctrl(self, joints:list, ctrlSize:float, color:str):

        ctrl_list = []
        offest_grps_list = []
        sdk_grps_list = []
        for joint in joints:
            ctrlName = self.create_ctrl(ctrlSize)
            ctrl = cmds.rename(ctrlName, '{}_ctrl'.format(joint))
            grp1 = cmds.group(ctrl,n='%s_Extragrp'%ctrl)
            grp2 = cmds.group(grp1 , n = '%s_SDKgrp'%ctrl)
            grp3 = cmds.group(grp2 , n = '%s_offestgrp'%ctrl)
            cmds.matchTransform(grp3, joint)
            ctrl_list.append(ctrl)
            offest_grps_list.append(grp3)
            sdk_grps_list.append(grp2)
            self.cerate_parentConstrain(parent=ctrl, child=joint)
            self.cerate_scaleConstrain(parent=ctrl, child=joint)
            self.create_ctrl_color(ctrl, color)
            cmds.refresh()
        
        return ctrl_list, offest_grps_list, sdk_grps_list
    
    def create_ctrl(self, ctrlSize:float):

        ctrl = cmds.curve(degree = 1, knot = self.knot, point = self.point)
        ctrlShape = cmds.listRelatives(ctrl, shapes = True)[0]
        ctrlShape = cmds.listRelatives(ctrl, shapes = True)
        ctrlShapeCV = cmds.select('{}.cv[0:7000]'.format(ctrlShape))
        cmds.scale(ctrlSize, ctrlSize, ctrlSize, ctrlShapeCV, relative = True, absolute = True)
        cmds.select(cl = True)

        return ctrl
    
    def cerate_parentConstrain(self, parent:str, child:str, mo:bool = True):

        if cmds.objExists(parent) and cmds.objExists(child):
            cmds.parentConstraint(parent, child, mo = mo)
        else:
            cmds.error('{} or {} is not exists! plese check it!'.format(parent, child))

    def cerate_scaleConstrain(self, parent:str, child:str):

        if cmds.objExists(parent) and cmds.objExists(child):
            cmds.scaleConstraint(parent, child, mo=True)
        else:
            cmds.error('{} or {} is not exists! plese check it!'.format(parent, child))

    def create_ctrl_color(self, obj:str, color:str):

        if color == 'Red':color_index = 13
        if color == 'Blue':color_index = 6
        if color == 'Yellow':color_index = 17

        if cmds.objExists(obj):
            shape = cmds.listRelatives(obj, s = True)[0]
            cmds.setAttr('{}.overrideEnabled'.format(shape), 1)
            cmds.setAttr('{}.overrideColor'.format(shape), color_index)
        else:
            cmds.error('No object named {}!'.format(obj))

    def create_distanceDim(self, name:str, start:str, end:str):

        node_name = name+'_disDimShape'
        dimNode = cmds.createNode('distanceDimShape', name = node_name)
        dimNode_parent = cmds.listRelatives(dimNode, parent = True)[0]
        cmds.setAttr('{}.visibility'.format(dimNode_parent), 0)

        start_shape = cmds.listRelatives(start, s = True)[0]
        end_shape = cmds.listRelatives(end, s = True)[0]

        cmds.connectAttr('{}.worldPosition[0]'.format(start_shape), '{}.startPoint'.format(dimNode), f = True)
        cmds.connectAttr('{}.worldPosition[0]'.format(end_shape), '{}.endPoint'.format(dimNode), f = True)

        return dimNode, dimNode_parent
    
    def add_smooth_skin(self, mesh:str, influence_joints:list, max_inffluences:int):
        '''
        Description:给指定的模型与关节添加蒙皮
        Parme:
            mesh：str， 模型名称
            influence_joints：list， 参与蒙皮的骨骼
            max_inffluences：int， 最大骨骼影响
        '''
        deformer = cmds.findDeformers(mesh)
        if deformer:
            skinCluster = cmds.ls(deformer, type = 'skinCluster')[0]
            if skinCluster:
                skin = skinCluster
            else:
                cmds.select(influence_joints, r = True)
                cmds.select(mesh, add = True)
                skin = cmds.skinCluster(name = '{}_skinCluster'.format(mesh), toSelectedBones = True, maximumInfluences = max_inffluences, skinMethod = 0, obeyMaxInfluences = True)
        else:
            cmds.select(influence_joints, r = True)
            cmds.select(mesh, add = True)
            skin = cmds.skinCluster(name = '{}_skinCluster'.format(mesh), toSelectedBones = True, maximumInfluences = max_inffluences, skinMethod = 0, obeyMaxInfluences = True)

        return skin
    
    def create_ikHandle(self, startJoint:str, endJoint:str, solverType:str):
        '''
        Description:根据给定的骨骼，创建指定的ik解算器
        Parme:
            startJoint：ik的起始关节
            endJoint：ik的endeffector
            solverType：解算器类型
        '''
        if cmds.objExists(startJoint) and cmds.objExists(endJoint):
            ikHandle = cmds.ikHandle(name = startJoint+'_ikHandle', startJoint = startJoint, endEffector = endJoint, solver = solverType)
        else:
            cmds.error('{} or {} is not exists! plese check it!'.format(startJoint, endJoint))
        
        return ikHandle[0]
    
    def create_follicle(self, mesh:str, uValue:float, vValue:float, i:int = None):
        '''
        Description:创建毛囊基础函数,模型的uv需要先分好，不能有重叠
        Parme:
            mesh: str, 创建毛囊所需要的模型的shape节点名称
            uValue：模型uv上面的u坐标
            vValue：模型uv上面的v坐标
            i：int，如果批量创建，则i为创建的序号
        '''
        focShape = cmds.createNode('follicle', name = '{}_base_focShape{}'.format(mesh, i))
        focTrans = cmds.listRelatives(focShape, parent = True)[0]

        cmds.connectAttr('{}.outTranslate'.format(focShape), '{}.translate'.format(focTrans), f = True)
        cmds.connectAttr('{}.outRotate'.format(focShape), '{}.rotate'.format(focTrans), f = True)

        cmds.connectAttr('{}.local'.format(mesh), '{}.inputSurface'.format(focShape),f=True)
        cmds.connectAttr('{}.worldMatrix[0]'.format(mesh), '{}.inputWorldMatrix'.format(focShape),f=True)

        cmds.setAttr('{}.parameterU'.format(focShape), uValue)
        cmds.setAttr('{}.parameterV'.format(focShape), vValue)
        cmds.select(cl = True)
        return focShape, focTrans





# if __name__ == '__main__':
#     cc = base_commmand()
#     cc.create_joints()