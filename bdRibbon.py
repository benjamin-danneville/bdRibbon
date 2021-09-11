##########################
## BENJAMIN DANNEVILLE  ##
## Ribbon               ##
##                      ##
## Version : 1.0        ##
## Date : March 2021    ##
##########################

import maya.cmds as cmds
import maya.mel as mel
from functools import partial

#############
## GLOBALS ##
#############

#Windows_size
window_width = 300
window_height = 230

#List that contains what I create to reuse them
jointCtrl_names = []
ctrl_names = []

###############
## FUNCTIONS ##
###############

def plane(uPatchNbr, _):
    #On recupere les valeurs des sliders:
    uPatchNbr = cmds.intSliderGrp(uPatchNbr, q=1, value=1)

    if cmds.objExists(cmds.textFieldGrp("name_txt", q=True, tx=True) + "Bind_ctrl"):
        print ("Plane already exists")
    else :
        #Creation du plane
        cmds.nurbsPlane(n=cmds.textFieldGrp("name_txt", q=True, tx=True) + "Bind_ctrl", u=uPatchNbr, v=1, ax=[0,1,0])

def create(ctrlNbr, _):
    #On recupere les valeurs des sliders:
    ctrlNbr = cmds.intSliderGrp(ctrlNbr, q=1, value=1)

    #On recupere l'objet selectionne
    selection = cmds.ls(sl=True)

    #Name of the ribbon:
    global ribbon_name, ribbonBind_name, ribbonJoint_name
    ribbonBind_name = selection[0]
    ribbonJoint_name = selection[0][0:-9] + "Joint_ctrl"
    ribbon_name = selection[0][0:-9]

    if cmds.objExists(ribbonJoint_name):
        print ("Controllers already created")

    else :
        #Duppliquer et renommer selon le nombre de modifiers !
        cmds.duplicate(selection, n= ribbonJoint_name) 

        #Get numbers of patches of the plane
        Upatch = cmds.getAttr(selection[0] + ".spansU")

        #Create follicles
        cmds.select(ribbonBind_name)
        mel.eval("createHair " + str(Upatch) + " 1 10 0 0 0 0 5 0 2 2 1;")
        #cmds.CreateHair([cmds.getAttr(nodes[0] + ".patchesU"),1,10,0,0,0,0,5,0,2,2,1])
        cmds.delete("hairSystem1", "hairSystem1OutputCurves", "nucleus1")

        global follicle_grp_name
        follicle_grp_name = ribbon_name + "Follicles_grp"
        cmds.rename("hairSystem1Follicles", follicle_grp_name)

        #var useful for later
        jointDuplicate_name = []
        global joint_names, follicles_names
        joint_names = []
        follicles_names = []

        #Deleting curves and creating joints
        follicle_number = 0
        for follicles in cmds.listRelatives(follicle_grp_name):
            follicle_number += 1
            joint_names.append(ribbon_name + "_" + str(follicle_number) + "_jnt")
            follicles_names.append(follicles)
            for child  in cmds.listRelatives(follicles): 
                if cmds.nodeType(child) == "transform" :
                    cmds.delete(child)
            cmds.joint(n = joint_names[-1])
            cmds.parent(joint_names[-1], follicles)
            cmds.setAttr(joint_names[-1] + ".translate", 0, 0, 0)
            if (ctrlNbr == 3):
                if (follicle_number == 1 or follicle_number == Upatch or follicle_number == (Upatch // 2) + 1):
                    jointDuplicate_name.append(joint_names[-1])
            elif (ctrlNbr == 5):
                if (follicle_number == 1 or follicle_number == Upatch or follicle_number == (Upatch // 2) + 1 or follicle_number == (Upatch *1/4) + 1 or follicle_number == (Upatch *3/4) + 1):
                    jointDuplicate_name.append(joint_names[-1])
            elif (ctrlNbr == 7):
                if (follicle_number == 1 or follicle_number == Upatch or follicle_number == (Upatch // 2) + 1 or follicle_number == (Upatch *1/6) + 1 or follicle_number == (Upatch *2/6) + 1 or follicle_number == (Upatch *4/6) + 1 or follicle_number == (Upatch *5/6) + 1):
                    jointDuplicate_name.append(joint_names[-1])
            elif (ctrlNbr == 9):
                if (follicle_number == 1 or follicle_number == Upatch or follicle_number == (Upatch // 2) + 1 or follicle_number == (Upatch *1/8) + 1 or follicle_number == (Upatch *2/8) + 1 or follicle_number == (Upatch *3/8) + 1 or follicle_number == (Upatch *5/8) + 1 or follicle_number == (Upatch *6/8) + 1 or follicle_number == (Upatch *7/8) + 1):
                    jointDuplicate_name.append(joint_names[-1])

        #Joint bind controllers
        pC_names = []
        for i in range (ctrlNbr):
            jointCtrl_names.append(ribbon_name + "Ctrl_" + str(i + 1) + "_jnt")
            ctrl_names.append(ribbon_name + "_" + str(i + 1) + "_ctrl")
            cmds.duplicate(jointDuplicate_name[i], n = jointCtrl_names[-1])
            cmds.parent(jointCtrl_names[-1], w=True)
            cmds.sphere(n= ctrl_names[-1], r = 0.2)
            cmds.group(n= ctrl_names[-1]+ "_grp")
            pC_names.append(cmds.parentConstraint(jointCtrl_names[-1], ctrl_names[-1] + "_grp", mo=False))
            cmds.delete(pC_names[-1])

        #Skinning
        cmds.select(d=True)
        for joint in jointCtrl_names:
            cmds.select(joint, add=True)
        cmds.select(ribbonJoint_name, add=True)
        mel.eval("SmoothBindSkin;")

        global subJointCtrl_grp_name, subCtrl_grp_name
        subJointCtrl_grp_name = ribbon_name + "SubJoint_grp"
        subCtrl_grp_name = ribbon_name + "SubJointCtrl_grp"
        cmds.group(n = subJointCtrl_grp_name, em=True)
        cmds.group(n= subCtrl_grp_name, em=True)
        for i in range(len(jointCtrl_names)):
            cmds.parent(jointCtrl_names[i], subJointCtrl_grp_name)
            cmds.parent(ctrl_names[i] + "_grp", subCtrl_grp_name)

def connect(_):
    if cmds.objExists(jointCtrl_names[0] + "_parentConstraint1"):
        print ("Connection already made")
    else :
        for i in range (len(jointCtrl_names)):
            cmds.parentConstraint(ctrl_names[i], jointCtrl_names[i], mo=True)

def modifiers(_):
    cmds.select(d=True)

    global ribbonWire_name, ribbonSine_name, ribbonTwist_name
    ribbonWire_name  = ribbonBind_name[0:-9] + "Wire_ctrl"
    ribbonSine_name = ribbonBind_name[0:-9] + "Sine_ctrl"
    ribbonTwist_name = ribbonBind_name[0:-9] + "Twist_ctrl"
    #ribbonSquash_name  = ribbonBind_name[0:-9] + "Squash_ctrl"
    
    global sine_modifier_name, twist_modifier_name
    sine_modifier_name = ribbonSine_name[0:-4] + "mod"
    twist_modifier_name = ribbonTwist_name[0:-4] + "mod"
    #squash_modifier_name = ribbonSquash_name[0:-4] + "mod"
    blendshape_name = ribbon_name + "_blendshape"
    
    #On part du principe qu'on delete tout le temps la blendshape precedente, bien plus simple
    try:
        cmds.delete(blendshape_name)
    except:
        print ("Blendshapes has never been created")

    ####OPTI####
    #Duppliquer et renommer selon le nombre de modifiers !
    cmds.select(d=True)
    ribbon_list = [ribbonJoint_name, ribbonBind_name]
    global curve_name
    curve_name= ribbon_name + "Wire_cv"
    clusters_name = [ribbon_name + "_start_cluster", ribbon_name + "_mid_cluster", ribbon_name + "_end_cluster"]
    wire_ctrl_names = [ribbon_name + "Wire_1_ctrl", ribbon_name + "Wire_2_ctrl", ribbon_name + "Wire_3_ctrl"]
    if (cmds.checkBox("wireCheckbox", q=True, value=True)):
        if (cmds.objExists(ribbonWire_name)):
            print (ribbonWire_name + " already exists")
        else :
            curve_point = [(cmds.getAttr(follicles_names[0] + ".translateX"), cmds.getAttr(follicles_names[0] + ".translateY"), cmds.getAttr(follicles_names[0] + ".translateZ")),(cmds.getAttr(follicles_names[-1] + ".translateX"), cmds.getAttr(follicles_names[-1] + ".translateY"), cmds.getAttr(follicles_names[-1] + ".translateZ"))]

            cmds.duplicate(ribbonBind_name, n=ribbonWire_name)
            
            #Creation curve
            cmds.curve(n=curve_name, d=2, p=[(curve_point[0][0], curve_point[0][1], curve_point[0][2]), (((curve_point[0][0] + curve_point[1][0]) / 2), ((curve_point[0][1] + curve_point[1][1]) / 2), ((curve_point[0][2] + curve_point[1][2]) / 2)) , (curve_point[1][0], curve_point[1][1],curve_point[1][2])], k=[0,0,1,1])
            #Creation clusters
            cmds.cluster(curve_name + ".cv[0]", n=clusters_name[0])
            cmds.cluster(curve_name + ".cv[1]", n=clusters_name[1])
            cmds.cluster(curve_name + ".cv[2]", n=clusters_name[2])
            #Mise sous un grp
            global clusters_grp_name
            clusters_grp_name = ribbon_name + "Clusters_grp"
            cmds.group(n=clusters_grp_name, em=True)
            for i in range (len(clusters_name)):
                cmds.parent(clusters_name[i] + "Handle", clusters_grp_name)

            
            follicle_pC_list = [0, len(follicles_names)//2, -1]
            for i in range (3):
                cmds.circle(n = wire_ctrl_names[i])
                cmds.group(n=wire_ctrl_names[i] + "_grp")
                pC_temp = cmds.parentConstraint(follicles_names[follicle_pC_list[i]], wire_ctrl_names[i] + "_grp", mo=False)
                cmds.delete(pC_temp)
                cmds.setAttr(wire_ctrl_names[i] + "_grp.rotateZ", 90)
                cmds.makeIdentity(wire_ctrl_names[i] + "_grp", apply=True, t=1, r=1, s=1, n=0 )
                cmds.pointConstraint(wire_ctrl_names[i], clusters_name[i] + "Handle", mo=True)
            cmds.pointConstraint(wire_ctrl_names[0], wire_ctrl_names[-1], wire_ctrl_names[1])

            global wire_ctrl_grp_name
            wire_ctrl_grp_name = ribbon_name + "WireCtrl_grp"
            cmds.group(n=wire_ctrl_grp_name, em=True)
            for i in range(len(wire_ctrl_names)):
                cmds.parent(wire_ctrl_names[i] + "_grp", wire_ctrl_grp_name)

        ribbon_list.insert(1, ribbonWire_name)
    else :
        try :
            cmds.delete(ribbonWire_name)
            cmds.delete(curve_name, clusters_grp_name, wire_ctrl_grp_name)
            cmds.delete(curve_name + "BaseWire")
        except:
            print ("Ribbon Wire has never been created or not connected yet")

    #Si checkbox est coche
    if (cmds.checkBox("sineCheckbox", q=True, value=True)):
        #On verifie que l'objet n'existe pas deja
        if (cmds.objExists(ribbonSine_name)):
            print (ribbonSine_name + " already exists")
        else :
            #Duplicate ribbon
            cmds.duplicate(ribbonBind_name, n=ribbonSine_name)
            #Modifier
            cmds.select(ribbonSine_name)
            cmds.nonLinear(type="sine", n=sine_modifier_name)
            #Adding Attributes
            cmds.select(ctrl_names[len(ctrl_names)//2])
            cmds.addAttr( ln="SINE_OPTIONS", at="enum", en="--------", k=True)
            cmds.addAttr( ln="Amplitude", at = "float", min = -5, max = 5, k=True)
            cmds.addAttr( ln="Wavelength", at = "float", dv=2, min = 0, max = 10, k=True)
            cmds.addAttr( ln="Offset", at = "float", min = 0, max = 10, k=True)
            cmds.addAttr( ln="Dropoff", at = "float", min = 0, max = 1, k=True)

            #Connexion des attributs
            cmds.connectAttr(ctrl_names[len(ctrl_names)//2] + ".Amplitude", sine_modifier_name + ".amplitude", f=True)
            cmds.connectAttr(ctrl_names[len(ctrl_names)//2] + ".Wavelength", sine_modifier_name + ".wavelength", f=True)
            cmds.connectAttr(ctrl_names[len(ctrl_names)//2] + ".Offset", sine_modifier_name + ".offset", f=True)
            cmds.connectAttr(ctrl_names[len(ctrl_names)//2] + ".Dropoff", sine_modifier_name + ".dropoff", f=True)
            
            #Connexion des attributs
            cmds.connectAttr(sine_modifier_name + ".amplitude", sine_modifier_name + "HandleShape.amplitude", f=True)
            cmds.connectAttr(sine_modifier_name + ".wavelength", sine_modifier_name + "HandleShape.wavelength", f=True)
            cmds.connectAttr(sine_modifier_name + ".offset", sine_modifier_name + "HandleShape.offset", f=True)
            cmds.connectAttr(sine_modifier_name + ".dropoff", sine_modifier_name + "HandleShape.dropoff", f=True)
        #Ajout a la liste pour creer les blendshapes
        ribbon_list.insert(1, ribbonSine_name)
    #Si elle n'est pas coche, on test de supprimer si elle existait precedemment, et si ce n'est pas le cas, rien ne se passe
    else :
        try :
            #Suppression du duplicated ribbon
            cmds.delete(ribbonSine_name)
            #Suppression des attributs
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".SINE_OPTIONS")
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".Amplitude")
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".Wavelength")
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".Offset")
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".Dropoff")

        #Cas ou le modifier n'existait pas avant
        except:
            print ("Ribbon Sine has never been created")

    if (cmds.checkBox("twistCheckbox", q=True, value=True)):
        if (cmds.objExists(ribbonTwist_name)):
            print (ribbonTwist_name + " already exists")
        else :
            pma_start = ribbonTwist_name + "_start_pma"
            pma_end = ribbonTwist_name + "_end_pma"

            cmds.duplicate(ribbonBind_name, n=ribbonTwist_name)
            cmds.select(ribbonTwist_name)
            cmds.nonLinear(type="twist", n=twist_modifier_name)

            cmds.select(ctrl_names[len(ctrl_names)//2])
            cmds.addAttr( ln="TWIST_OPTIONS", at="enum", en="--------", k=True)
            cmds.addAttr( ln="Start_Twist", at = "float", k=True)
            cmds.addAttr( ln="End_Twist", at = "float", k=True)
            cmds.addAttr( ln="Roll", at = "float", k=True)

            cmds.shadingNode ("plusMinusAverage", n = pma_start, asUtility=True)
            cmds.shadingNode ("plusMinusAverage", n = pma_end, asUtility=True)

            cmds.connectAttr(ctrl_names[len(ctrl_names)//2] + ".Start_Twist", pma_start + ".input1D[0]", f=True)
            cmds.connectAttr(ctrl_names[len(ctrl_names)//2] + ".Roll", pma_start + ".input1D[1]", f=True)
            cmds.connectAttr(ctrl_names[len(ctrl_names)//2] + ".End_Twist", pma_end + ".input1D[0]", f=True)
            cmds.connectAttr(ctrl_names[len(ctrl_names)//2] + ".Roll", pma_end + ".input1D[1]", f=True)

            cmds.connectAttr(pma_start + ".output1D", twist_modifier_name + ".startAngle", f=True)
            cmds.connectAttr(pma_end + ".output1D", twist_modifier_name + ".endAngle", f=True)

            cmds.connectAttr(twist_modifier_name + ".startAngle", twist_modifier_name + "HandleShape.startAngle", f=True)
            cmds.connectAttr(twist_modifier_name + ".endAngle", twist_modifier_name + "HandleShape.endAngle", f=True)

        ribbon_list.insert(1, ribbonTwist_name)
    else :
        try :
            cmds.delete(ribbonTwist_name)
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".TWIST_OPTIONS")
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".Start_Twist")
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".End_Twist")
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".Roll")
        except:
            print ("Ribbon Twist has never been created")
    """
    if (cmds.checkBox("squashCheckbox", q=True, value=True)):
        if (cmds.objExists(ribbonSquash_name)):
            print (ribbonSquash_name + " already exists")
        else :
            cmds.duplicate(ribbonBind_name, n=ribbonSquash_name)
            cmds.select(ribbonSquash_name)
            cmds.nonLinear(type="squash", n=squash_modifier_name)
            cmds.select(ctrl_names[len(ctrl_names)//2])
            cmds.addAttr( ln="SQUASH_OPTIONS", at="enum", en="--------", k=True)
        ribbon_list.insert(1, ribbonSquash_name)
    else :
        try :
            cmds.delete(ribbonSquash_name)
            cmds.deleteAttr(ctrl_names[len(ctrl_names)//2] + ".SQUASH_OPTIONS")
        except:
            print ("Ribbon Squash has never been created")
    """
    #Creation des blendshapes
    cmds.select(d=True)
    #Selectioner des ribbons necessaires
    for i in range (len(ribbon_list)):
        cmds.select(ribbon_list[i], add=True)
    #Creation blendshape
    cmds.blendShape(n= blendshape_name)
    #Mise a 1 des influence de blendshape
    for i in range (len(ribbon_list)-1):
        cmds.setAttr(blendshape_name + "." + ribbon_list[i], 1)
    
    """
    pC_temp = cmds.parentConstraint(follicles_names[len(joint_names) // 2], sine_modifier_name + "Handle")
    cmds.delete(pC_temp)
    cmds.rotate(0, 90, 90, sine_modifier_name + "Handle", os=True, r=True)
    """

def organise(_):
    rig_system_grp_name = ribbon_name + "RigSystem_grp"
    ctrl_grp_name = ribbon_name + "Ctrl_grp"
    surface_grp_name = ribbon_name + "SurfacePlane_grp"
    mod_grp_name = ribbon_name + "SurfaceMod_grp"
    if (cmds.objExists(rig_system_grp_name)):
        print ("Organise already done !")
    else :
        cmds.group(n=rig_system_grp_name  ,em=True)
        cmds.group(n=ctrl_grp_name, em=True)

        cmds.group(n=surface_grp_name, em=True, p=rig_system_grp_name)
        cmds.group(n=mod_grp_name, em=True, p=rig_system_grp_name)

        cmds.parent(subCtrl_grp_name, ctrl_grp_name)
        cmds.parent(subJointCtrl_grp_name, rig_system_grp_name)
        cmds.parent(follicle_grp_name, rig_system_grp_name)
        cmds.parent(ribbonBind_name, surface_grp_name)
        cmds.parent(ribbonJoint_name, surface_grp_name)

        if (cmds.objExists(ribbonWire_name)):
            try:
                cmds.parent(ribbonWire_name, surface_grp_name)
                cmds.parent(curve_name, mod_grp_name)
                cmds.parent(clusters_grp_name, rig_system_grp_name)
                cmds.parent(wire_ctrl_grp_name, ctrl_grp_name)
                baseWire_name = curve_name[0:-3] + "BaseWire_cv"
                cmds.rename(curve_name + "BaseWire", baseWire_name)
                cmds.parent(baseWire_name, mod_grp_name)
            except:
                print ("Wire hasn't been connected to the surface yet !")

        if (cmds.objExists(ribbonSine_name)):
            cmds.parent(ribbonSine_name, surface_grp_name)
            cmds.parent(sine_modifier_name + "Handle", mod_grp_name)
        if (cmds.objExists(ribbonTwist_name)):
            cmds.parent(ribbonTwist_name, surface_grp_name)
            cmds.parent(twist_modifier_name + "Handle", mod_grp_name)
############
## WINDOW ##
############

try:
    cmds.deleteUI(AutoTurn, window=True)
except (NameError, RuntimeError):
    pass
Ribbon = cmds.window(title = "BD Ribbon", w=window_width, h=window_height)
cmds.rowColumnLayout (nc =1)

#Header    
cmds.text('\n',h=5)
cmds.text("BD Ribbon")
cmds.separator(style="out",h=5,w=5)
cmds.text('\n',h=5)

#Body
cmds.textFieldGrp("name_txt", label="Name :", tx="Unnamed")
cmds.text('\n',h=5)
x = cmds.intSliderGrp(l= "Segments : ", v=13, min=5, max=21, field=True)
cmds.button(label = "Plane", command=partial(plane, x))
y = cmds.intSliderGrp(l= "Number of Ctrl : ", v=5, min=3, max=9, field=True)
cmds.text('\n',h=5)
cmds.button(label = "Controllers", command=partial(create, y))
cmds.text('\n',h=5)
cmds.button(label = "Connect", command=connect)
cmds.text('\n',h=5)
cmds.checkBox("wireCheckbox" ,label="Wire", value = 1)
cmds.checkBox("sineCheckbox" ,label="Sine", value = 1)
cmds.checkBox("twistCheckbox" ,label="Twist", value = 0)
#cmds.checkBox("squashCheckbox" ,label="Squash", value = 0)
cmds.rowColumnLayout (nc =1)
cmds.button(label = "Modifiers", command=modifiers)
cmds.text('\n',h=5)
cmds.button(label = "Organise", command=organise)
cmds.text('\n',h=5)

#Credits
cmds.text("copyright Benjamin Danneville                                                 licence GNU GPL")

cmds.showWindow(Ribbon)