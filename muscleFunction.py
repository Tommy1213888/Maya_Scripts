# -*- coding: utf-8 -*-
'''
Description:
Author:	chuanqin
E-mail:	6744035640@qq.com
Version:1.0
Date:2024-08-18
'''

import maya.cmds as cmds
import maya.mel as mel
import get_uiData
import baseCommand
import muscleConnection
import setStretch
import maya_reload
maya_reload.refresh(baseCommand)
maya_reload.refresh(muscleConnection)
maya_reload.refresh(setStretch)
maya_reload.refresh(get_uiData)

class muscle:

    def __init__(self) -> None:
        self.data = get_uiData.data()
        self.base = baseCommand.base_commmand()
        self.connect = muscleConnection.Connection()
        self.set = setStretch.setDriver()
        self.rootGrp = 'Muscle_system_grp'

    def load_selected_joints(self, jointName:str):

        '''
        Description:load selected joints from sence
        Parme:str
            {start, end}
        '''
        sel = cmds.ls(sl = True)[0]
        if jointName == 'start':
            joint_tfb = 'mus_start'
        if jointName == 'end':
            joint_tfb = 'mus_end'

        if cmds.objectType(sel) != 'joint':
            cmds.error('Plese select joint to load!')
        else:
            cmds.textFieldButtonGrp(joint_tfb, edit = True, text = sel)

    def create_muscle_surfaces(self, mus_name:str):
        '''
        Description:
        Parme:
        '''
        # self.create_muscle_grps(mus_name)
        mus_grp = mus_name+'_grp'
        mus_surface_grp = mus_name+'_surface_grp'
        self.base.create_empty_group(mus_grp)
        self.base.create_empty_group(mus_surface_grp)
        parent_grp = cmds.listRelatives(mus_surface_grp, parent = True)
        if parent_grp != mus_grp:
            cmds.parent(mus_surface_grp, mus_grp)

        mus_width = self.data.get_muscle_width()
        mus_height = self.data.get_muscle_height()
        mus_split = self.data.get_joints_count()-1

        mus_surfaces = [mus_name + '_base_surface', mus_name + '_driver_surface']

        surface_name_list = []
        for surface in mus_surfaces:
            if cmds.objExists(surface):
                cmds.warning('Name {} surface are already exits! skip it!'.format(surface))
                continue
            else:
                surface_name = cmds.nurbsPlane(name = surface, ax = (0,1,0), degree = 3, width = float(mus_height), patchesU = mus_split, patchesV = 1, lr=float(mus_width)/float(mus_height))[0]
                cmds.parent(surface_name, mus_surface_grp)
                cmds.DeleteHistory()
                surface_name_list.append(surface_name)

        # cmds.setAttr('{}.visibility'.format(surface_name_list[0]), 0)
        return surface_name_list

    def create_muscle_grps(self, mus_name:str):
        '''
        Description:
        Parme:
        '''
        if not cmds.objExists(self.rootGrp):
            self.base.create_empty_group(self.rootGrp)

        grps_name = [mus_name + '_grp', mus_name+'_surface_grp', mus_name+'_driver_system_grp', mus_name+'_IK_joint_grp', mus_name+'_IKHandle_grp',
                     mus_name+'_ctrl_loc_grp', mus_name+'_Distance_grp', mus_name+'_follicle_grp', mus_name+'_driver_joints_grp', mus_name+'_driver_ctrls_grp',
                     mus_name+'_skin_system_grp', mus_name+'_skin_joints_grp', mus_name+'_skin_ctrls_grp']
        grp_list = []
        for grp in grps_name:
            groups = self.base.create_empty_group(grp)
            cmds.select(cl = True)
            cmds.parent(groups, self.rootGrp)
            grp_list.append(groups)
        
        return grp_list
    
    def get_surface_boundingBox(self, surface:str):
        '''
        Description:获取当前指定的模型边界信息
        Parme:surface，模型名称
        '''
        bbox = cmds.exactWorldBoundingBox(surface, calculateExactly = 1, ignoreInvisible = 1)
        print('给定的模型长度为{},宽度为{}'.format((bbox[3]-bbox[0]), (bbox[5]-bbox[2])))
        return bbox[0], bbox[3], bbox[2], bbox[5]
    
    def get_interval(self, mesh:str, count:int):
        '''
        Description:获取当前surface的边界，并通过骨骼数量来计算当创建骨骼等物体时的间隔参数
        Parme:
            mesh:str， 当前的模型
            count:int， 需要创建的数量
        '''
        xMin, xMax, zMin, zMax = self.get_surface_boundingBox(mesh)
        interval = (xMax-xMin)/(count-1)
        return interval
    
    def create_IK_joints(self, mus_name:str, base_mesh:str, joint_count:int):
        '''
        Description:
        Parme:
            mus_name: str
            base_mesh: str, 基础蒙皮模型，用来拉伸骨骼
            joint_count: int, 设置创建多少个关节
        '''
        # 创建IK组，并整理一下层级
        driver_system_grp = mus_name+'_driver_system_grp'
        ik_joints_grp = mus_name+'_IK_joint_grp'
        ikHandle_grp = mus_name+'_IKHandle_grp'
        muscle_loc_grp = mus_name+'_ctrl_loc_grp'
        ikDistance_grp = mus_name+'_Distance_grp'
        muscle_grp = mus_name + '_grp'
        for grp in [driver_system_grp, ik_joints_grp, ikHandle_grp,muscle_loc_grp,ikDistance_grp,muscle_grp]:
            self.base.create_empty_group(grp)

        # 隐藏ikjoints组
        cmds.setAttr('{}.visibility'.format(ik_joints_grp), 0)

        cmds.parent(driver_system_grp, muscle_grp)
        for hi_grp in [ik_joints_grp, ikHandle_grp, muscle_loc_grp, ikDistance_grp]:
            cmds.parent(hi_grp, driver_system_grp)

        joints_sideL_list = []
        joints_sideR_list = []
        joints_list = []

        for i in range(joint_count*2):
            if i < joint_count:
                side = 'sideL'
                index = i+1
            else:
                side = 'sideR'
                index = i-joint_count+1

            joint_name = self.base.create_joints(jointName='{}_{}_0{}_IK_jnt'.format(mus_name, side, str(index)))
            joints_list.append(joint_name)
        
        joints_sideL_list = joints_list[0:joint_count]
        joints_sideR_list = joints_list[joint_count:]

        xMin, xMax, zMin, zMax = self.get_surface_boundingBox(base_mesh)
        interval = (xMax-xMin)/(joint_count-1)
        print(interval)
        # 创建左边关节，并整理层级
        for l in range(len(joints_sideL_list)):
            cmds.setAttr('{}.translate'.format(joints_sideL_list[l]), xMin+(interval*l), 0, zMin)
            if l < 1:continue
            else:cmds.parent(joints_sideL_list[l], joints_sideL_list[l-1])
        # 创建右边关节，并整理层级
        for r in range(len(joints_sideR_list)):
            cmds.setAttr('{}.translate'.format(joints_sideR_list[r]), xMin+(interval*r), 0, zMax)
            if r < 1:continue
            else:
                cmds.parent(joints_sideR_list[r], joints_sideR_list[r-1])

        self.base.add_smooth_skin(base_mesh, joints_list, 3)

        cmds.parent(joints_sideL_list[0], ik_joints_grp)
        cmds.parent(joints_sideR_list[0], ik_joints_grp)

        # 创建SCikHandle
        side_L_ikHandle = self.base.create_ikHandle(joints_sideL_list[0], joints_sideL_list[-1], 'ikSCsolver')
        side_R_ikHandle = self.base.create_ikHandle(joints_sideR_list[0], joints_sideR_list[-1], 'ikSCsolver')
        # 设置ikHandle不可见
        cmds.setAttr('{}.visibility'.format(side_L_ikHandle), 0)
        cmds.setAttr('{}.visibility'.format(side_R_ikHandle), 0)
        # 整理层级
        cmds.parent(side_L_ikHandle, ikHandle_grp)
        cmds.parent(side_R_ikHandle, ikHandle_grp)

        # 创建loc用来约束ikHandle
        side_L_start_loc = cmds.spaceLocator(name = mus_name+'_side_L_ik_start_loc')[0]
        side_L_end_loc = cmds.spaceLocator(name = mus_name+'_side_L_ik_end_loc')[0]
        side_R_start_loc = cmds.spaceLocator(name = mus_name+'_side_R_ik_start_loc')[0]
        side_R_end_loc = cmds.spaceLocator(name = mus_name+'_side_R_ik_end_loc')[0]

        muscle_start_loc = cmds.spaceLocator(name = mus_name+'_start_loc')[0]
        muscle_end_loc = cmds.spaceLocator(name = mus_name+'_end_loc')[0]
        # 整理loc层级
        loc_grp_list = []
        for loc in [side_L_start_loc, side_L_end_loc, side_R_start_loc, side_R_end_loc, muscle_start_loc, muscle_end_loc]:
            if loc == muscle_start_loc or loc == muscle_end_loc:
                self.base.create_ctrl_color(loc, 'Red')
            else:
                self.base.create_ctrl_color(loc, 'Blue')

            grp = self.base.create_empty_group('{}_grp'.format(loc))
            cmds.parent(loc, grp)
            cmds.parent(grp, muscle_loc_grp)
            loc_grp_list.append(grp)
        # 匹配loc位置
        cmds.matchTransform(loc_grp_list[0], joints_sideL_list[0])
        cmds.matchTransform(loc_grp_list[1], joints_sideL_list[-1])
        cmds.matchTransform(loc_grp_list[2], joints_sideR_list[0])
        cmds.matchTransform(loc_grp_list[3], joints_sideR_list[-1])
        cmds.setAttr('{}.translate'.format(loc_grp_list[4]), xMin, 0, 0)
        cmds.setAttr('{}.translate'.format(loc_grp_list[5]), xMax, 0, 0)

        cmds.parent(loc_grp_list[0], loc_grp_list[4])
        cmds.parent(loc_grp_list[2], loc_grp_list[4])
        cmds.parent(loc_grp_list[1], loc_grp_list[5])
        cmds.parent(loc_grp_list[3], loc_grp_list[5])

        # 创建距离接电脑，用来计算骨骼缩放系数
        distence_start_loc_L = cmds.spaceLocator(name = mus_name+'_distance_L_start_loc')[0]
        distence_end_loc_L = cmds.spaceLocator(name = mus_name+'_distance_L_end_loc')[0]
        distence_start_loc_R = cmds.spaceLocator(name = mus_name+'_distance_R_start_loc')[0]
        distence_end_loc_R = cmds.spaceLocator(name = mus_name+'_distance_R_end_loc')[0]

        for dis_loc in [distence_start_loc_L, distence_end_loc_L, distence_start_loc_R, distence_end_loc_R]:
            cmds.setAttr('{}.visibility'.format(dis_loc), 0)

        cmds.matchTransform(distence_start_loc_L, side_L_start_loc)
        cmds.matchTransform(distence_end_loc_L, side_L_end_loc)
        cmds.matchTransform(distence_start_loc_R, side_R_start_loc)
        cmds.matchTransform(distence_end_loc_R, side_R_end_loc)

        cmds.parent(distence_start_loc_L, side_L_start_loc)
        cmds.parent(distence_end_loc_L, side_L_end_loc)
        cmds.parent(distence_start_loc_R, side_R_start_loc)
        cmds.parent(distence_end_loc_R, side_R_end_loc)

        # 创建距离节点
        side_L_distance_shape, side_L_distance_node = self.base.create_distanceDim(name = mus_name+'_side_L_dis', start=distence_start_loc_L, end=distence_end_loc_L)
        side_R_distance_shape, side_R_distance_node = self.base.create_distanceDim(name = mus_name+'_side_R_dis', start=distence_start_loc_R, end=distence_end_loc_R)

        cmds.parent(side_L_distance_node, ikDistance_grp)
        cmds.parent(side_R_distance_node, ikDistance_grp)

        # 设置IK伸缩
        dis_L_md = cmds.createNode('multiplyDivide', name = mus_name+'_side_L_IK_disMD')
        dis_R_md = cmds.createNode('multiplyDivide', name = mus_name+'_side_R_IK_disMD')

        distance_L = cmds.getAttr('{}.distance'.format(side_L_distance_shape))
        distance_R = cmds.getAttr('{}.distance'.format(side_R_distance_shape))
        cmds.setAttr('{}.input2'.format(dis_L_md), distance_L,distance_L,distance_L)
        cmds.setAttr('{}.input2'.format(dis_R_md), distance_R,distance_R,distance_R)
        cmds.setAttr('{}.operation'.format(dis_L_md), 2)
        cmds.setAttr('{}.operation'.format(dis_R_md), 2)

        cmds.connectAttr('{}.distance'.format(side_L_distance_shape), '{}.input1X'.format(dis_L_md), f = True)
        cmds.connectAttr('{}.distance'.format(side_R_distance_shape), '{}.input1X'.format(dis_R_md), f = True)

        for sideL in joints_sideL_list[0:-1]:
            cmds.connectAttr('{}.outputX'.format(dis_L_md), '{}.scaleX'.format(sideL), f = True)
        for sideR in joints_sideR_list[0:-1]:
            cmds.connectAttr('{}.outputX'.format(dis_R_md), '{}.scaleX'.format(sideR), f = True)

        # 约束ikHandle
        cmds.parentConstraint(side_L_start_loc, joints_sideL_list[0])
        cmds.parentConstraint(side_L_end_loc, side_L_ikHandle)
        cmds.parentConstraint(side_R_start_loc, joints_sideR_list[0])
        cmds.parentConstraint(side_R_end_loc, side_R_ikHandle)

        # 创建空组，用来约束ikHandle的控制loc
        empty_L_start_grp = self.base.create_empty_group(side_L_start_loc+'_constrain_grp')
        empty_L_end_grp = self.base.create_empty_group(side_L_end_loc+'_constrain_grp')
        empty_R_start_grp = self.base.create_empty_group(side_R_start_loc+'_constrain_grp')
        empty_R_end_grp = self.base.create_empty_group(side_R_end_loc+'_constrain_grp')

        cmds.matchTransform(empty_L_start_grp, side_L_start_loc)
        cmds.matchTransform(empty_L_end_grp, side_L_end_loc)
        cmds.matchTransform(empty_R_start_grp, side_R_start_loc)
        cmds.matchTransform(empty_R_end_grp, side_R_end_loc)

        cmds.parent(empty_L_start_grp, muscle_start_loc)
        cmds.parent(empty_R_start_grp, muscle_start_loc)
        cmds.parent(empty_L_end_grp, muscle_end_loc)
        cmds.parent(empty_R_end_grp, muscle_end_loc)

        cmds.pointConstraint(empty_L_start_grp, loc_grp_list[0])
        cmds.pointConstraint(empty_L_end_grp, loc_grp_list[1])
        cmds.pointConstraint(empty_R_start_grp, loc_grp_list[2])
        cmds.pointConstraint(empty_R_end_grp, loc_grp_list[3])

        cmds.orientConstraint(empty_L_start_grp, loc_grp_list[0])
        cmds.orientConstraint(empty_L_end_grp, loc_grp_list[1])
        cmds.orientConstraint(empty_R_start_grp, loc_grp_list[2])
        cmds.orientConstraint(empty_R_end_grp, loc_grp_list[3])

        return loc_grp_list
    
    def create_base_follicle(self, mus_name:str, base_mesh:str, follicle_count:int):
        '''
        Description:
        Parme:
        '''
        # 检查是否毛囊组被创建以及层级整理
        follicle_grp = mus_name+'_follicle_grp'
        muscle_driver_grp = mus_name+'_driver_system_grp'

        if cmds.objExists(follicle_grp) and cmds.objExists(muscle_driver_grp):
            parent = cmds.listRelatives(follicle_grp, parent = True)
            if muscle_driver_grp in parent:pass
            else:
                cmds.parent(follicle_grp, muscle_driver_grp)
        else:
            self.base.create_empty_group(follicle_grp)
            self.base.create_empty_group(muscle_driver_grp)
            cmds.parent(follicle_grp, muscle_driver_grp)
        cmds.setAttr('{}.visibility'.format(follicle_grp), 0)

        # 创建毛囊
        focShape_list = []
        focTrans_list = []
        for i in range(follicle_count*2):
            if i < follicle_count:
                uValue = (1/(follicle_count-1))*i
                vValue = 1
            else:
                uValue = (1/(follicle_count-1))*(i-follicle_count)
                vValue = 0
            focShape, focTrans = self.base.create_follicle(base_mesh, uValue, vValue, i+1)
            cmds.parent(focTrans, follicle_grp)
            focShape_list.append(focShape)
            focTrans_list.append(focTrans)
        
        return focShape_list, focTrans_list
    
    def create_skin_follicle(self, mus_name:str, driver_mesh:str, follicle_count:int):

        follicle_grp = mus_name+'_skin_follicle_grp'
        muscle_skin_grp = mus_name+'_skin_system_grp'

        if cmds.objExists(follicle_grp) and cmds.objExists(muscle_skin_grp):
            parent = cmds.listRelatives(follicle_grp, parent = True)
            if muscle_skin_grp in parent:pass
            else:
                cmds.parent(follicle_grp, muscle_skin_grp)
        else:
            self.base.create_empty_group(follicle_grp)
            self.base.create_empty_group(muscle_skin_grp)
            cmds.parent(follicle_grp, muscle_skin_grp)
        cmds.setAttr('{}.visibility'.format(follicle_grp), 0)

        vValue = 0.5
        # 创建毛囊
        focShape_list = []
        focTrans_list = []
        for i in range(follicle_count):
            uValue = (1/(follicle_count-1))*i
            focShape, focTranns = self.base.create_follicle(driver_mesh, uValue, vValue, i+1)
            cmds.parent(focTranns, follicle_grp)
            focShape_list.append(focShape)
            focTrans_list.append(focTranns)
        cmds.select(cl = True)
        return focShape_list, focTrans_list

    def create_driver_joints(self, mus_name:str,base_mesh:str, driver_mesh:str, joint_count:int):
        '''
        Description:
        Parme:
        '''
        focShape_list, focTrans_list = self.create_base_follicle(mus_name, base_mesh, joint_count)
        driver_joints_grp = mus_name+'_driver_joints_grp'
        muscle_driver_grp = mus_name+'_driver_system_grp'
        driver_ctrls_grp = mus_name+'_driver_ctrls_grp'

        if cmds.objExists(driver_joints_grp) and cmds.objExists(driver_ctrls_grp) and cmds.objExists(muscle_driver_grp):
            parent1 = cmds.listRelatives(driver_joints_grp, parent = True)
            parent2 = cmds.listRelatives(driver_ctrls_grp, parent = True)
            if muscle_driver_grp in parent1 and muscle_driver_grp in parent2:pass
            else:
                cmds.parent(driver_joints_grp, muscle_driver_grp)
                cmds.parent(driver_ctrls_grp, muscle_driver_grp)
        else:
            self.base.create_empty_group(driver_joints_grp)
            self.base.create_empty_group(driver_ctrls_grp)
            self.base.create_empty_group(muscle_driver_grp)
            cmds.parent(driver_joints_grp, muscle_driver_grp)
            cmds.parent(driver_ctrls_grp, muscle_driver_grp)
        cmds.setAttr('{}.visibility'.format(driver_joints_grp), 0)

        xMin, xMax, zMin, zMax = self.get_surface_boundingBox(driver_mesh)
        interval = (xMax-xMin)/(joint_count-1)

        driver_joints_list = []
        for i in range(joint_count*2):
            if i < joint_count:
                side = '_L'
            else:
                side = '_R'
            drvJoint = self.base.create_joints(mus_name+'_driver_0'+str(i+1)+'_jnt'+side)
            driver_joints_list.append(drvJoint)

        for j in range(len(driver_joints_list)):
            if j < len(driver_joints_list)/2:
                cmds.setAttr('{}.translateX'.format(driver_joints_list[j]),  xMin+(interval*j))
                cmds.setAttr('{}.translateY'.format(driver_joints_list[j]), 0)
                cmds.setAttr('{}.translateZ'.format(driver_joints_list[j]), zMin)
            else:
                cmds.setAttr('{}.translateX'.format(driver_joints_list[j]),  xMin+(interval*(j-len(driver_joints_list)/2)))
                cmds.setAttr('{}.translateY'.format(driver_joints_list[j]), 0)
                cmds.setAttr('{}.translateZ'.format(driver_joints_list[j]), zMax)
        
        ctrl_list, offest_grps_list, sdk_grps_list = self.base.create_FK_ctrl(driver_joints_list, 0.3, 'Yellow')
        cmds.parent(driver_joints_list, driver_joints_grp)
        cmds.parent(offest_grps_list, driver_ctrls_grp)

        for s in range(len(offest_grps_list)):
            self.base.cerate_parentConstrain(focTrans_list[s], offest_grps_list[s])

        self.base.add_smooth_skin(driver_mesh, driver_joints_list, 3)

    def create_skin_joints(self, mus_name:str, driver_mesh:str, joint_count:int):

        muscle_grp = mus_name+'_grp'
        skin_sys_grp = mus_name+'_skin_system_grp'
        skin_joints_grp = mus_name+'_skin_joints_grp'
        skin_ctrl_grp = mus_name+'_skin_ctrls_grp'
        if cmds.objExists(skin_sys_grp) and cmds.objExists(skin_joints_grp) and cmds.objExists(skin_ctrl_grp) and cmds.objExists(muscle_grp):
            parent1 = cmds.listRelatives(skin_joints_grp, parent = True)
            parent2 = cmds.listRelatives(skin_ctrl_grp, parent = True)
            parent3 = cmds.listRelatives(skin_sys_grp, parent = True)
            if skin_sys_grp in parent1 and skin_sys_grp in parent2:pass
            elif muscle_grp in parent3:pass
            else:
                cmds.parent(skin_joints_grp, skin_sys_grp)
                cmds.parent(skin_ctrl_grp, skin_sys_grp)
                cmds.parent(skin_sys_grp, muscle_grp)   
        else:
            self.base.create_empty_group(muscle_grp)
            self.base.create_empty_group(skin_sys_grp)
            self.base.create_empty_group(skin_joints_grp)
            self.base.create_empty_group(skin_ctrl_grp)
            cmds.parent(skin_joints_grp, skin_sys_grp)
            cmds.parent(skin_ctrl_grp, skin_sys_grp)
            cmds.parent(skin_sys_grp, muscle_grp)

        focShape_list, focTrans_list = self.create_skin_follicle(mus_name, driver_mesh, joint_count)

        xMin, xMax, zMin, zMax = self.get_surface_boundingBox(driver_mesh)
        interval = (xMax-xMin)/(joint_count-1)
        skin_joints_list = []
        for i in range(joint_count):
            skinJoint = self.base.create_joints(mus_name+'_skin_0'+str(i+1)+'_jnt')
            cmds.setAttr('{}.translateX'.format(skinJoint), xMin+(interval*i))
            skin_joints_list.append(skinJoint)
            cmds.select(cl=True)

        ctrl_list, off_grps_list, sdk_grp_list = self.base.create_FK_ctrl(skin_joints_list, 0.8, 'Red')
        cmds.parent(off_grps_list, skin_ctrl_grp)
        cmds.parent(skin_joints_list, skin_joints_grp)

        assert len(off_grps_list) == len(focTrans_list), '毛囊数量与控制器数量不一致，请检查'
        for s in range(len(off_grps_list)):
            # self.base.cerate_parentConstrain(focTrans_list[s], off_grps_list[s])
            cmds.parentConstraint(focTrans_list[s], off_grps_list[s], mo = True)
        # for g, f in zip(off_grps_list, focTrans_list):
        #     self.base.cerate_parentConstrain(f, g)

    def creare_final_skin_joints(self, mus_name, joint_counnt, skin_joints):

        final_joints_grp = mus_name + '_final_joints_grp'
        skin_system_grp = mus_name+'_skin_system_grp'
        if not cmds.objExists(final_joints_grp):
            self.base.create_empty_group(final_joints_grp)
            cmds.parent(final_joints_grp, skin_system_grp)
        
        cmds.select(cl=True)

        final_joints_list = []

        for i in range(joint_counnt):
            final = self.base.create_joints('{}_final_skin_{:02d}_jnt'.format(mus_name, i+1))
            cmds.select(cl=True)
            cmds.parent(final, final_joints_grp)
            cmds.matchTransform(final, skin_joints[i])
            final_joints_list.append(final)

        for jnt in final_joints_list:
            cmds.select(jnt, r = True)
            mel.eval('channelBoxCommand -freezeRotate')
            cmds.select(cl=True)

        for parent, child in zip(skin_joints, final_joints_list):
            cmds.parentConstraint(parent, child, mo=True)
            cmds.scaleConstraint(parent, child, mo=True)
            cmds.setAttr('{}.visibility'.format(parent), 0)


    def create_muscle_system(self):

        mus_name = self.data.get_muscle_name()
        self.create_muscle_grps(mus_name)
        joint_count = self.data.get_joints_count()
        surface_name_list = self.create_muscle_surfaces(mus_name)
        loc_grps_list = self.create_IK_joints(mus_name, surface_name_list[0], joint_count)
        # self.create_base_follicle(mus_name, surface_name_list[0], 6)
        self.create_driver_joints(mus_name, surface_name_list[0], surface_name_list[1], joint_count)
        # self.create_skin_follicle(mus_name, surface_name_list[1], 6)
        self.create_skin_joints(mus_name, surface_name_list[1], joint_count)
        cmds.setAttr('{}.visibility'.format(surface_name_list[0]), 0)

        start_joint = cmds.textFieldGrp('mus_start', query = True, tx = True)
        end_joint = cmds.textFieldGrp('mus_end', query = True, tx = True)
        if start_joint != '' and end_joint != '':
            cmds.matchTransform(loc_grps_list[-2], start_joint, position = True)
            cmds.matchTransform(loc_grps_list[-1], end_joint, position = True)
            cmds.parentConstraint(start_joint, loc_grps_list[-2], mo = True)
            cmds.parentConstraint(end_joint, loc_grps_list[-1], mo = True)

    def connect_muscle_driver(self):

        mus_name = self.data.get_muscle_name()
        joint_count = self.data.get_joints_count()
        skin_joints = [mus_name+'_skin_0'+str(i+1)+'_jnt' for i in range(joint_count)]
        sdk_grps = [jnt+'_ctrl_SDKgrp' for jnt in skin_joints]
        start_loc = mus_name+'_start_loc'
        end_loc = mus_name+'_end_loc'
        distance_grp = mus_name+'_Distance_grp'

        final_distance_node = mus_name+'_final_dimShape_disDim'
        if cmds.objExists(final_distance_node):
            cmds.warning('{} 节点已存在，跳过创建！'.format(final_distance_node))
        else:
            distance_shape, distance_trans = self.base.create_distanceDim(final_distance_node, start_loc, end_loc)
            cmds.parent(distance_trans, distance_grp)

        selected_driver = self.data.get_selected_driver()

        if selected_driver['translate'] == 'True':
            connected_trans = cmds.listConnections('{}.translate'.format(sdk_grps[0]), c = True)
            if connected_trans:
                cmds.warning('{} 平移属性已经被连接上！跳过！'.format(mus_name))
            else:
                self.connect.connect_translation(mus_name, distance_shape, joint_count, sdk_grps)
        
        if selected_driver['rotate'] == 'True':
            connected_rotate = cmds.listConnections('{}.rotate'.format(sdk_grps[0]), c = True)
            if connected_rotate:
                cmds.warning('{} 旋转属性已经被连接上！跳过！'.format(mus_name))
            else:
                self.connect.connect_rotate(mus_name, distance_shape, joint_count, sdk_grps)

        if selected_driver['scale'] == 'True':
            connected_scale = cmds.listConnections('{}.scale'.format(sdk_grps[0]), c = True)
            if connected_scale:
                cmds.warning('{} 缩放属性已经被连接上！跳过！'.format(mus_name))
            else:
                self.connect.connect_scale(mus_name, distance_shape, joint_count, sdk_grps)

        self.create_final_distance_dimShape(mus_name, start_loc, end_loc)
        self.creare_final_skin_joints(mus_name, joint_count, skin_joints)

    def create_final_distance_dimShape(self, mus_name:str, start_loc, end_loc):
        distance_grp = mus_name+'_Distance_grp'
        start_loc_grp = mus_name+'_start_loc_grp'
        final_loc_grp = mus_name+'_final_loc_grp'

        if not cmds.objExists(final_loc_grp):
            self.base.create_empty_group(final_loc_grp)
            cmds.matchTransform(final_loc_grp, start_loc_grp)
            cmds.parent(final_loc_grp, start_loc_grp)

        final_start_loc = mus_name+'_final_start_loc'
        final_end_loc = mus_name+'_final_end_loc'
        if cmds.objExists(final_start_loc) and cmds.objExists(final_end_loc):
            cmds.warning('当前场景已存在 {} 的最终距离测算节点，跳过创建！'.format(mus_name))
        else:
            final_start_loc_name = cmds.spaceLocator(name = final_start_loc)[0]
            final_end_loc_name = cmds.spaceLocator(name = final_end_loc)[0]
            cmds.matchTransform(final_start_loc_name, start_loc)
            cmds.matchTransform(final_end_loc_name, end_loc)
            cmds.parent(final_end_loc_name, final_loc_grp)
            cmds.parent(final_start_loc_name, final_loc_grp)
            final_distanceShape, final_distanceTrans = self.base.create_distanceDim(name=mus_name+'_final_setMuscle_dimShape', start=final_start_loc_name, end=final_end_loc_name)
            cmds.parent(final_distanceTrans, distance_grp)
            cmds.setAttr('{}.visibility'.format(final_start_loc_name), 0)
            cmds.setAttr('{}.visibility'.format(final_end_loc_name), 0)
            cmds.setAttr('{}.visibility'.format(final_distanceTrans), 0)
            cmds.select(cl = True)
        
        return final_distanceShape, final_distanceTrans


    def set_muscle_stretch_squeeze(self, modality):
        mus_name = self.data.get_muscle_name()
        joint_count = self.data.get_joints_count()

        selected_driver = self.data.get_selected_driver()

        new_disShape = mus_name+'_final_dimShape_disDim_disDimShape'
        old_disShape= mus_name+'_final_setMuscle_dimShape_disDimShape'
        new_distance = cmds.getAttr('{}.distance'.format(new_disShape))
        old_distance = cmds.getAttr('{}.distance'.format(old_disShape))
        if selected_driver['translate'] == 'True':
            self.set.set_translate(mus_name, joint_count, modality, old_distance, new_distance)
        if selected_driver['rotate'] == 'True':
            self.set.set_rotate(mus_name, joint_count, modality, old_distance, new_distance)
        if selected_driver['scale'] == 'True':
            self.set.set_scale(mus_name, joint_count, modality, old_distance, new_distance)


    def mirror_muscle_system(self):

        serach_letter, replace_letter = self.data.get_mirror_name()
        mus_name = self.data.get_muscle_name()
        joint_count = self.data.get_joints_count()

        mirror_mus_name = mus_name.replace(serach_letter, replace_letter)
        self.create_muscle_grps(mirror_mus_name)

        surface_name_list = self.create_muscle_surfaces(mirror_mus_name)
        loc_grps_list = self.create_IK_joints(mirror_mus_name, surface_name_list[0], joint_count)
        self.create_driver_joints(mirror_mus_name, surface_name_list[0], surface_name_list[1], joint_count)
        self.create_skin_joints(mirror_mus_name, surface_name_list[1], joint_count)
        cmds.setAttr('{}.visibility'.format(surface_name_list[0]), 0)

        start_joint = cmds.textFieldGrp('mus_start', query = True, tx = True)
        end_joint = cmds.textFieldGrp('mus_end', query = True, tx = True)
        mirror_start_joint = start_joint.replace(serach_letter, replace_letter)
        mirror_end_joint = end_joint.replace(serach_letter, replace_letter)

        if start_joint != '' and end_joint != '':
            cmds.matchTransform(loc_grps_list[-2], mirror_start_joint, position = True)
            cmds.matchTransform(loc_grps_list[-1], mirror_end_joint, position = True)
            cmds.parentConstraint(mirror_start_joint, loc_grps_list[-2], mo = True)
            cmds.parentConstraint(mirror_end_joint, loc_grps_list[-1], mo = True)
        cmds.select(cl = True)

        start_loc = mus_name+'_start_loc'
        end_loc = mus_name+'_end_loc'
        start_side_l_loc = mus_name+'_side_L_ik_start_loc'
        start_side_r_loc = mus_name+'_side_R_ik_start_loc'
        end_side_l_loc = mus_name+'_side_L_ik_end_loc'
        end_side_r_loc = mus_name+'_side_R_ik_end_loc'
        driver_ctrl_list = []
        for i in range(joint_count*2):
            if i < joint_count:
                side = '_L'
            else:
                side = '_R'
            joint_name = mus_name+'_driver_0'+str(i+1)+'_jnt'+side+'_ctrl'
            driver_ctrl_list.append(joint_name)

        mirror_start_loc = mirror_mus_name+'_start_loc'
        mirror_end_loc = mirror_mus_name+'_end_loc'
        mirror_start_side_l_loc = mirror_mus_name+'_side_L_ik_start_loc'
        mirror_start_side_r_loc = mirror_mus_name+'_side_R_ik_start_loc'
        mirror_end_side_l_loc = mirror_mus_name+'_side_L_ik_end_loc'
        mirror_end_side_r_loc = mirror_mus_name+'_side_R_ik_end_loc'
        mirror_sdk_grps = [mirror_mus_name+'_skin_0{}_jnt_ctrl_SDKgrp'.format(i+1) for i in range(joint_count)]
        mirror_distance_grp = mirror_mus_name+'_Distance_grp'
        mirror_driver_ctrl_list = []
        for i in range(joint_count*2):
            if i < joint_count:
                mirror_side = '_L'
            else:
                mirror_side = '_R'
            mirror_joint_name = mirror_mus_name+'_driver_0'+str(i+1)+'_jnt'+mirror_side+'_ctrl'
            mirror_driver_ctrl_list.append(mirror_joint_name)
        # start loc
        cmds.setAttr('{}.translateX'.format(mirror_start_loc), -1*float(cmds.getAttr('{}.translateX'.format(start_loc))))
        cmds.setAttr('{}.translateY'.format(mirror_start_loc), float(cmds.getAttr('{}.translateY'.format(start_loc))))
        cmds.setAttr('{}.translateZ'.format(mirror_start_loc), float(cmds.getAttr('{}.translateZ'.format(start_loc))))
        cmds.setAttr('{}.rotateX'.format(mirror_start_loc), float(cmds.getAttr('{}.rotateX'.format(start_loc))))
        cmds.setAttr('{}.rotateY'.format(mirror_start_loc), -1*float(cmds.getAttr('{}.rotateY'.format(start_loc))))
        cmds.setAttr('{}.rotateZ'.format(mirror_start_loc), -1*float(cmds.getAttr('{}.rotateZ'.format(start_loc))))
        cmds.setAttr('{}.scaleX'.format(mirror_start_loc), float(cmds.getAttr('{}.scaleX'.format(start_loc))))
        cmds.setAttr('{}.scaleY'.format(mirror_start_loc), float(cmds.getAttr('{}.scaleY'.format(start_loc))))
        cmds.setAttr('{}.scaleZ'.format(mirror_start_loc), float(cmds.getAttr('{}.scaleZ'.format(start_loc))))
        # end_loc
        cmds.setAttr('{}.translateX'.format(mirror_end_loc), -1*float(cmds.getAttr('{}.translateX'.format(end_loc))))
        cmds.setAttr('{}.translateY'.format(mirror_end_loc), float(cmds.getAttr('{}.translateY'.format(end_loc))))
        cmds.setAttr('{}.translateZ'.format(mirror_end_loc), float(cmds.getAttr('{}.translateZ'.format(end_loc))))
        cmds.setAttr('{}.rotateX'.format(mirror_end_loc), 180-float(cmds.getAttr('{}.rotateX'.format(end_loc))))
        cmds.setAttr('{}.rotateY'.format(mirror_end_loc), 180-float(cmds.getAttr('{}.rotateY'.format(end_loc))))
        cmds.setAttr('{}.rotateZ'.format(mirror_end_loc), -1*float(cmds.getAttr('{}.rotateZ'.format(end_loc))))
        cmds.setAttr('{}.scaleX'.format(mirror_end_loc), float(cmds.getAttr('{}.scaleX'.format(end_loc))))
        cmds.setAttr('{}.scaleY'.format(mirror_end_loc), float(cmds.getAttr('{}.scaleY'.format(end_loc))))
        cmds.setAttr('{}.scaleZ'.format(mirror_end_loc), float(cmds.getAttr('{}.scaleZ'.format(end_loc))))
        # start_side_l_loc
        cmds.setAttr('{}.translateX'.format(mirror_start_side_l_loc), float(cmds.getAttr('{}.translateX'.format(start_side_l_loc))))
        cmds.setAttr('{}.translateY'.format(mirror_start_side_l_loc), -1*float(cmds.getAttr('{}.translateY'.format(start_side_l_loc))))
        cmds.setAttr('{}.translateZ'.format(mirror_start_side_l_loc), float(cmds.getAttr('{}.translateZ'.format(start_side_l_loc))))
        cmds.setAttr('{}.rotateX'.format(mirror_start_side_l_loc), -1*float(cmds.getAttr('{}.rotateX'.format(start_side_l_loc))))
        cmds.setAttr('{}.rotateY'.format(mirror_start_side_l_loc), float(cmds.getAttr('{}.rotateY'.format(start_side_l_loc))))
        cmds.setAttr('{}.rotateZ'.format(mirror_start_side_l_loc), -1*float(cmds.getAttr('{}.rotateZ'.format(start_side_l_loc))))
        cmds.setAttr('{}.scaleX'.format(mirror_start_side_l_loc), float(cmds.getAttr('{}.scaleX'.format(start_side_l_loc))))
        cmds.setAttr('{}.scaleY'.format(mirror_start_side_l_loc), float(cmds.getAttr('{}.scaleY'.format(start_side_l_loc))))
        cmds.setAttr('{}.scaleZ'.format(mirror_start_side_l_loc), float(cmds.getAttr('{}.scaleZ'.format(start_side_l_loc))))
        # start_side_r_loc
        cmds.setAttr('{}.translateX'.format(mirror_start_side_r_loc), float(cmds.getAttr('{}.translateX'.format(start_side_r_loc))))
        cmds.setAttr('{}.translateY'.format(mirror_start_side_r_loc), -1*float(cmds.getAttr('{}.translateY'.format(start_side_r_loc))))
        cmds.setAttr('{}.translateZ'.format(mirror_start_side_r_loc), float(cmds.getAttr('{}.translateZ'.format(start_side_r_loc))))
        cmds.setAttr('{}.rotateX'.format(mirror_start_side_r_loc), -1*float(cmds.getAttr('{}.rotateX'.format(start_side_r_loc))))
        cmds.setAttr('{}.rotateY'.format(mirror_start_side_r_loc), float(cmds.getAttr('{}.rotateY'.format(start_side_r_loc))))
        cmds.setAttr('{}.rotateZ'.format(mirror_start_side_r_loc), -1*float(cmds.getAttr('{}.rotateZ'.format(start_side_r_loc))))
        cmds.setAttr('{}.scaleX'.format(mirror_start_side_r_loc), float(cmds.getAttr('{}.scaleX'.format(start_side_r_loc))))
        cmds.setAttr('{}.scaleY'.format(mirror_start_side_r_loc), float(cmds.getAttr('{}.scaleY'.format(start_side_r_loc))))
        cmds.setAttr('{}.scaleZ'.format(mirror_start_side_r_loc), float(cmds.getAttr('{}.scaleZ'.format(start_side_r_loc))))
        # end_side_l_loc
        cmds.setAttr('{}.translateX'.format(mirror_end_side_l_loc), float(cmds.getAttr('{}.translateX'.format(end_side_l_loc))))
        cmds.setAttr('{}.translateY'.format(mirror_end_side_l_loc), -1*float(cmds.getAttr('{}.translateY'.format(end_side_l_loc))))
        cmds.setAttr('{}.translateZ'.format(mirror_end_side_l_loc), float(cmds.getAttr('{}.translateZ'.format(end_side_l_loc))))
        cmds.setAttr('{}.rotateX'.format(mirror_end_side_l_loc), -1*float(cmds.getAttr('{}.rotateX'.format(end_side_l_loc))))
        cmds.setAttr('{}.rotateY'.format(mirror_end_side_l_loc), float(cmds.getAttr('{}.rotateY'.format(end_side_l_loc))))
        cmds.setAttr('{}.rotateZ'.format(mirror_end_side_l_loc), -1*float(cmds.getAttr('{}.rotateZ'.format(end_side_l_loc))))
        cmds.setAttr('{}.scaleX'.format(mirror_end_side_l_loc), float(cmds.getAttr('{}.scaleX'.format(end_side_l_loc))))
        cmds.setAttr('{}.scaleY'.format(mirror_end_side_l_loc), float(cmds.getAttr('{}.scaleY'.format(end_side_l_loc))))
        cmds.setAttr('{}.scaleZ'.format(mirror_end_side_l_loc), float(cmds.getAttr('{}.scaleZ'.format(end_side_l_loc))))
        # end_side_r_loc
        cmds.setAttr('{}.translateX'.format(mirror_end_side_r_loc), float(cmds.getAttr('{}.translateX'.format(end_side_r_loc))))
        cmds.setAttr('{}.translateY'.format(mirror_end_side_r_loc), -1*float(cmds.getAttr('{}.translateY'.format(end_side_r_loc))))
        cmds.setAttr('{}.translateZ'.format(mirror_end_side_r_loc), float(cmds.getAttr('{}.translateZ'.format(end_side_r_loc))))
        cmds.setAttr('{}.rotateX'.format(mirror_end_side_r_loc), -1*float(cmds.getAttr('{}.rotateX'.format(end_side_r_loc))))
        cmds.setAttr('{}.rotateY'.format(mirror_end_side_r_loc), float(cmds.getAttr('{}.rotateY'.format(end_side_r_loc))))
        cmds.setAttr('{}.rotateZ'.format(mirror_end_side_r_loc), -1*float(cmds.getAttr('{}.rotateZ'.format(end_side_r_loc))))
        cmds.setAttr('{}.scaleX'.format(mirror_end_side_r_loc), float(cmds.getAttr('{}.scaleX'.format(end_side_r_loc))))
        cmds.setAttr('{}.scaleY'.format(mirror_end_side_r_loc), float(cmds.getAttr('{}.scaleY'.format(end_side_r_loc))))
        cmds.setAttr('{}.scaleZ'.format(mirror_end_side_r_loc), float(cmds.getAttr('{}.scaleZ'.format(end_side_r_loc))))

        for s in range(len(driver_ctrl_list)):
            cmds.setAttr('{}.translateX'.format(mirror_driver_ctrl_list[s]), float(cmds.getAttr('{}.translateX'.format(driver_ctrl_list[s]))))
            cmds.setAttr('{}.translateY'.format(mirror_driver_ctrl_list[s]), -1*float(cmds.getAttr('{}.translateY'.format(driver_ctrl_list[s]))))
            cmds.setAttr('{}.translateZ'.format(mirror_driver_ctrl_list[s]), float(cmds.getAttr('{}.translateZ'.format(driver_ctrl_list[s]))))
            cmds.setAttr('{}.rotateX'.format(mirror_driver_ctrl_list[s]), -1*float(cmds.getAttr('{}.rotateX'.format(driver_ctrl_list[s]))))
            cmds.setAttr('{}.rotateY'.format(mirror_driver_ctrl_list[s]), float(cmds.getAttr('{}.rotateY'.format(driver_ctrl_list[s]))))
            cmds.setAttr('{}.rotateZ'.format(mirror_driver_ctrl_list[s]), -1*float(cmds.getAttr('{}.rotateZ'.format(driver_ctrl_list[s]))))
            cmds.setAttr('{}.scaleX'.format(mirror_driver_ctrl_list[s]), float(cmds.getAttr('{}.scaleX'.format(driver_ctrl_list[s]))))
            cmds.setAttr('{}.scaleY'.format(mirror_driver_ctrl_list[s]), float(cmds.getAttr('{}.scaleY'.format(driver_ctrl_list[s]))))
            cmds.setAttr('{}.scaleZ'.format(mirror_driver_ctrl_list[s]), float(cmds.getAttr('{}.scaleZ'.format(driver_ctrl_list[s]))))

        final_distance_node = mirror_mus_name+'_final_dimShape_disDim'
        if cmds.objExists(final_distance_node):
            cmds.warning('{} 节点已存在，跳过创建！'.format(final_distance_node))
        else:
            distance_shape, distance_trans = self.base.create_distanceDim(final_distance_node, mirror_start_loc, mirror_end_loc)
            cmds.parent(distance_trans, mirror_distance_grp)

        selected_driver = self.data.get_selected_driver()

        if selected_driver['translate'] == 'True':
            connected_trans = cmds.listConnections('{}.translate'.format(mirror_sdk_grps[0]), c = True)
            if connected_trans:
                cmds.warning('{} 平移属性已经被连接上！跳过！'.format(mirror_mus_name))
            else:
                self.connect.connect_translation(mirror_mus_name, distance_shape, joint_count, mirror_sdk_grps)
        
        if selected_driver['rotate'] == 'True':
            connected_rotate = cmds.listConnections('{}.rotate'.format(mirror_sdk_grps[0]), c = True)
            if connected_rotate:
                cmds.warning('{} 旋转属性已经被连接上！跳过！'.format(mirror_mus_name))
            else:
                self.connect.connect_rotate(mirror_mus_name, distance_shape, joint_count, mirror_sdk_grps)

        if selected_driver['scale'] == 'True':
            connected_scale = cmds.listConnections('{}.scale'.format(mirror_sdk_grps[0]), c = True)
            if connected_scale:
                cmds.warning('{} 缩放属性已经被连接上！跳过！'.format(mirror_mus_name))
            else:
                self.connect.connect_scale(mirror_mus_name, distance_shape, joint_count, mirror_sdk_grps)
        self.create_final_distance_dimShape(mirror_mus_name, mirror_start_loc, mirror_end_loc)

        if selected_driver['translate'] == 'True':
            translate_calculate_MD = [mus_name+'_skin_0{}_jnt_ctrl_translate_calculate_MD'.format(i+1) for i in range(joint_count)]
            stretch_translate_setCoeff_MD = [mus_name+'_skin_0{}_jnt_ctrl_stretch_translate_setCoeff_MD'.format(i+1) for i in range(joint_count)]
            squeeze_translate_calculate_MD = [mus_name+'_skin_0{}_jnt_ctrl_squeeze_translate_setCoeff_MD'.format(i+1) for i in range(joint_count)]

            mirror_translate_calculate_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_translate_calculate_MD'.format(i+1) for i in range(joint_count)]
            mirror_stretch_translate_setCoeff_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_stretch_translate_setCoeff_MD'.format(i+1) for i in range(joint_count)]
            mirror_squeeze_translate_calculate_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_squeeze_translate_setCoeff_MD'.format(i+1) for i in range(joint_count)]

            for a in range(joint_count):
                cmds.setAttr('{}.input2X'.format(mirror_translate_calculate_MD[a]), float(cmds.getAttr('{}.input2X'.format(translate_calculate_MD[a]))))
                cmds.setAttr('{}.input2Y'.format(mirror_translate_calculate_MD[a]), -1*float(cmds.getAttr('{}.input2Y'.format(translate_calculate_MD[a]))))
                cmds.setAttr('{}.input2Z'.format(mirror_translate_calculate_MD[a]), float(cmds.getAttr('{}.input2Z'.format(translate_calculate_MD[a]))))

                cmds.setAttr('{}.input2X'.format(mirror_stretch_translate_setCoeff_MD[a]), float(cmds.getAttr('{}.input2X'.format(stretch_translate_setCoeff_MD[a]))))
                cmds.setAttr('{}.input2Y'.format(mirror_stretch_translate_setCoeff_MD[a]), float(cmds.getAttr('{}.input2Y'.format(stretch_translate_setCoeff_MD[a]))))
                cmds.setAttr('{}.input2Z'.format(mirror_stretch_translate_setCoeff_MD[a]), float(cmds.getAttr('{}.input2Z'.format(stretch_translate_setCoeff_MD[a]))))

                cmds.setAttr('{}.input2X'.format(mirror_squeeze_translate_calculate_MD[a]), float(cmds.getAttr('{}.input2X'.format(squeeze_translate_calculate_MD[a]))))
                cmds.setAttr('{}.input2Y'.format(mirror_squeeze_translate_calculate_MD[a]), float(cmds.getAttr('{}.input2Y'.format(squeeze_translate_calculate_MD[a]))))
                cmds.setAttr('{}.input2Z'.format(mirror_squeeze_translate_calculate_MD[a]), float(cmds.getAttr('{}.input2Z'.format(squeeze_translate_calculate_MD[a]))))

        if selected_driver['rotate'] == 'True':
            rotate_calculate_MD = [mus_name+'_skin_0{}_jnt_ctrl_rotate_calculate_MD'.format(i+1) for i in range(joint_count)]
            stretch_rotate_setCoeff_MD = [mus_name+'_skin_0{}_jnt_ctrl_stretch_rotate_setCoeff_MD'.format(i+1) for i in range(joint_count)]
            squeeze_rotate_calculate_MD = [mus_name+'_skin_0{}_jnt_ctrl_squeeze_rotate_setCoeff_MD'.format(i+1) for i in range(joint_count)]

            mirror_rotate_calculate_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_rotate_calculate_MD'.format(i+1) for i in range(joint_count)]
            mirror_stretch_rotate_setCoeff_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_stretch_rotate_setCoeff_MD'.format(i+1) for i in range(joint_count)]
            mirror_squeeze_rotate_calculate_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_squeeze_rotate_setCoeff_MD'.format(i+1) for i in range(joint_count)]

            for b in range(joint_count):
                cmds.setAttr('{}.input2X'.format(mirror_rotate_calculate_MD[b]), -1*float(cmds.getAttr('{}.input2X'.format(rotate_calculate_MD[b]))))
                cmds.setAttr('{}.input2Y'.format(mirror_rotate_calculate_MD[b]), float(cmds.getAttr('{}.input2Y'.format(rotate_calculate_MD[b]))))
                cmds.setAttr('{}.input2Z'.format(mirror_rotate_calculate_MD[b]), -1*float(cmds.getAttr('{}.input2Z'.format(rotate_calculate_MD[b]))))

                cmds.setAttr('{}.input2X'.format(mirror_stretch_rotate_setCoeff_MD[b]), float(cmds.getAttr('{}.input2X'.format(stretch_rotate_setCoeff_MD[b]))))
                cmds.setAttr('{}.input2Y'.format(mirror_stretch_rotate_setCoeff_MD[b]), float(cmds.getAttr('{}.input2Y'.format(stretch_rotate_setCoeff_MD[b]))))
                cmds.setAttr('{}.input2Z'.format(mirror_stretch_rotate_setCoeff_MD[b]), float(cmds.getAttr('{}.input2Z'.format(stretch_rotate_setCoeff_MD[b]))))

                cmds.setAttr('{}.input2X'.format(mirror_squeeze_rotate_calculate_MD[b]), float(cmds.getAttr('{}.input2X'.format(squeeze_rotate_calculate_MD[b]))))
                cmds.setAttr('{}.input2Y'.format(mirror_squeeze_rotate_calculate_MD[b]), float(cmds.getAttr('{}.input2Y'.format(squeeze_rotate_calculate_MD[b]))))
                cmds.setAttr('{}.input2Z'.format(mirror_squeeze_rotate_calculate_MD[b]), float(cmds.getAttr('{}.input2Z'.format(squeeze_rotate_calculate_MD[b]))))
        
        if selected_driver['scale'] == 'True':
            # scale_calculate_MD = [mus_name+'_skin_0{}_jnt_ctrl_scale_calculate_MD'.format(i+1) for i in range(joint_count)]
            stretch_scale_setCoeff_MD = [mus_name+'_skin_0{}_jnt_ctrl_stretch_scale_setCoeff_MD'.format(i+1) for i in range(joint_count)]
            squeeze_scale_calculate_MD = [mus_name+'_skin_0{}_jnt_ctrl_squeeze_scale_setCoeff_MD'.format(i+1) for i in range(joint_count)]

            # mirror_scale_calculate_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_scale_calculate_MD'.format(i+1) for i in range(joint_count)]
            mirror_stretch_scale_setCoeff_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_stretch_scale_setCoeff_MD'.format(i+1) for i in range(joint_count)]
            mirror_squeeze_scale_calculate_MD = [mirror_mus_name+'_skin_0{}_jnt_ctrl_squeeze_scale_setCoeff_MD'.format(i+1) for i in range(joint_count)]

            for c in range(joint_count):
                # cmds.setAttr('{}.input2X'.format(mirror_scale_calculate_MD[c]), -1*float(cmds.getAttr('{}.input2X'.format(scale_calculate_MD[c]))))
                # cmds.setAttr('{}.input2Y'.format(mirror_scale_calculate_MD[c]), float(cmds.getAttr('{}.input2Y'.format(scale_calculate_MD[c]))))
                # cmds.setAttr('{}.input2Z'.format(mirror_scale_calculate_MD[c]), -1*float(cmds.getAttr('{}.input2Z'.format(scale_calculate_MD[c]))))

                cmds.setAttr('{}.input2X'.format(mirror_stretch_scale_setCoeff_MD[c]), float(cmds.getAttr('{}.input2X'.format(stretch_scale_setCoeff_MD[c]))))
                cmds.setAttr('{}.input2Y'.format(mirror_stretch_scale_setCoeff_MD[c]), float(cmds.getAttr('{}.input2Y'.format(stretch_scale_setCoeff_MD[c]))))
                cmds.setAttr('{}.input2Z'.format(mirror_stretch_scale_setCoeff_MD[c]), float(cmds.getAttr('{}.input2Z'.format(stretch_scale_setCoeff_MD[c]))))

                cmds.setAttr('{}.input2X'.format(mirror_squeeze_scale_calculate_MD[c]), float(cmds.getAttr('{}.input2X'.format(squeeze_scale_calculate_MD[c]))))
                cmds.setAttr('{}.input2Y'.format(mirror_squeeze_scale_calculate_MD[c]), float(cmds.getAttr('{}.input2Y'.format(squeeze_scale_calculate_MD[c]))))
                cmds.setAttr('{}.input2Z'.format(mirror_squeeze_scale_calculate_MD[c]), float(cmds.getAttr('{}.input2Z'.format(squeeze_scale_calculate_MD[c]))))


    def clear_current_muscle(self):

        mus_name = self.data.get_muscle_name()
        mus_grp = mus_name + '_grp'
        joint_count = self.data.get_joints_count()
        final_skin_joints = ['{}_final_skin_{:02d}_jnt'.format(mus_name, i+1) for i in range(joint_count)]

        skinCluster_list = cmds.ls(type = 'skinCluster')

        log = []
        for skin in skinCluster_list:
            inf_joint = cmds.skinCluster(skin, query = True, inf = True)
            for jnt in final_skin_joints:
                if jnt in inf_joint:
                    text = '{} 在 {} 节点里面，请移除蒙皮再删除'.format(jnt, skin)
                    log.append(text)
                else:continue

        log_message = []
        log_message.extend(log)

        if len(log) != 0:
            cmds.confirmDialog(title = 'skinCluster', message = '以下骨骼存在蒙皮节点:\n{}'.format('\n'.join(log_message)), button = '好的')
            return
        else:
            cmds.select(mus_grp, r = True)
            cmds.delete()

    def clear_all_muscle(self):

        muscle_grp = 'Muscle_system_grp'
        cmds.select(muscle_grp, r = True)
        cmds.delete()