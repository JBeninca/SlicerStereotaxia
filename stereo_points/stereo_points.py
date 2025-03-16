# -*- coding: latin-1 -*-
import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging


#
# stereo_points
#


class stereo_points(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Stereotactic points"
        self.parent.categories = ["Stereotaxia"]
        self.parent.dependencies = []
        self.parent.contributors = [
            "Dorian Vogel (FHNW, LiU), Marc Jermann (FHNW)"
        ]  # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = """
This module allows entering target points in stereotactic coordinates and have them transformed in RAS space. 
This requires the use of the "Leksell Frame localization" first. Points are also transformed in the reference 
image ijk space and the image without ijk2ras transform can also be created.
"""
        # self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
This file was originally developed by Dorian Vogel, (Fachhochschule Nordwestschweitz, Muttenz, Switzerland; 
Linköping University, Linköping, Sweden). 
Financial support: FHNW, SSF, VR.
"""


#
# stereo_pointsWidget
#
class stereo_pointsWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        stereoPointsAdd_collbtn = ctk.ctkCollapsibleButton()
        stereoPointsAdd_collbtn.text = "Enter stereotactic points"
        self.layout.addWidget(stereoPointsAdd_collbtn)

        self.stereoPointsVBoxLayout = qt.QVBoxLayout(stereoPointsAdd_collbtn)
        self.stereoPointsFormLayout = qt.QFormLayout()
        self.pointTableView = slicer.qMRMLTableView()

        self.referenceImage_selectionCombo = slicer.qMRMLNodeComboBox()
        self.referenceImage_selectionCombo.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.referenceImage_selectionCombo.selectNodeUponCreation = True
        self.referenceImage_selectionCombo.noneEnabled = False
        self.referenceImage_selectionCombo.showHidden = False
        self.referenceImage_selectionCombo.showChildNodeTypes = False
        self.referenceImage_selectionCombo.setMRMLScene(slicer.mrmlScene)
        self.referenceImage_selectionCombo.setToolTip(
            "Select the image to transform the fiducials to:"
        )
        self.stereoPointsFormLayout.addRow(
            "Reference image", self.referenceImage_selectionCombo
        )

        self.frameTransform_selectionCombo = slicer.qMRMLNodeComboBox()
        self.frameTransform_selectionCombo.nodeTypes = ["vtkMRMLTransformNode"]
        self.frameTransform_selectionCombo.selectNodeUponCreation = True
        self.frameTransform_selectionCombo.noneEnabled = False
        self.frameTransform_selectionCombo.showHidden = False
        self.frameTransform_selectionCombo.showChildNodeTypes = False
        self.frameTransform_selectionCombo.setMRMLScene(slicer.mrmlScene)
        self.frameTransform_selectionCombo.setToolTip(
            "Transformation obtained during the ICP frame registration"
        )
        self.stereoPointsFormLayout.addRow(
            "Frame to image transform", self.frameTransform_selectionCombo
        )

        self.fiducialGroup_selectionCombo = slicer.qMRMLNodeComboBox()
        self.fiducialGroup_selectionCombo.nodeTypes = ["vtkMRMLMarkupsLineNode"]
        self.fiducialGroup_selectionCombo.selectNodeUponCreation = True
        self.fiducialGroup_selectionCombo.renameEnabled = True
        self.fiducialGroup_selectionCombo.noneEnabled = False
        self.fiducialGroup_selectionCombo.showHidden = False
        self.fiducialGroup_selectionCombo.showChildNodeTypes = False
        self.fiducialGroup_selectionCombo.setMRMLScene(slicer.mrmlScene)
        self.fiducialGroup_selectionCombo.baseName = "Stereotactic_points"
        self.fiducialGroup_selectionCombo.setToolTip(
            "Select line node for coordinates conversion"
        )
        self.stereoPointsFormLayout.addRow(
            "Trajectory", self.fiducialGroup_selectionCombo
        )

        # Create and set up widget that contains a single "place control point" button. The widget can be placed in the module GUI.
        self.placeWidget = slicer.qSlicerMarkupsPlaceWidget()
        self.placeWidget.setMRMLScene(slicer.mrmlScene)
        self.placeWidget.buttonsVisible = True
        self.placeWidget.PlaceButton.hide()
        self.placeWidget.DeleteButton.hide()
        self.placeWidget.MoreButton.show()
        self.placeWidget.PlaceMenu.hide()

        self.placeWidget.deleteAllControlPointsOptionVisible = False

        self.colorButton = slicer.util.findChild(self.placeWidget, "ColorButton")
        self.colorButton.show()

        self.lockNumberButton = self.placeWidget.children()[6]
        self.lockNumberButton.visible = False

        # add place widget to the stereoPointsFormLayout
        self.placeWidget.show()
        self.stereoPointsFormLayout.addRow("Settings", self.placeWidget)

        self.stereoPointsVBoxLayout.addLayout(self.stereoPointsFormLayout)
        self.stereoPointsVBoxLayout.addWidget(self.pointTableView)

        self.NewPointGLay = qt.QGridLayout()

        self.nameField = qt.QLineEdit()
        self.nameField.setPlaceholderText("Add new point")
        self.NewPointGLay.addWidget(self.nameField, 0, 0)

        self.paralellTraj = qt.QComboBox()
        self.paralellTraj.addItems(
            ["Central", "Anterior", "Posterior", "Left", "Right"]
        )
        self.NewPointGLay.addWidget(self.paralellTraj, 1, 0)

        self.xLabel = qt.QLabel("X")
        self.xLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.xField = qt.QDoubleSpinBox()
        self.xField.setRange(0.0, 999.99)
        self.NewPointGLay.addWidget(self.xLabel, 0, 1)
        self.NewPointGLay.addWidget(self.xField, 0, 2)

        self.yLabel = qt.QLabel("Y")
        self.yLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.yField = qt.QDoubleSpinBox()
        self.yField.setRange(0.0, 999.99)
        self.NewPointGLay.addWidget(self.yLabel, 0, 3)
        self.NewPointGLay.addWidget(self.yField, 0, 4)

        self.zLabel = qt.QLabel("Z")
        self.zLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.zField = qt.QDoubleSpinBox()
        self.zField.setRange(0.0, 999.99)
        self.NewPointGLay.addWidget(self.zLabel, 0, 5)
        self.NewPointGLay.addWidget(self.zField, 0, 6)

        self.ringLabel = qt.QLabel("Ring")
        self.ringLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.ringField = qt.QDoubleSpinBox()
        self.ringField.setRange(0.0, 180.00)
        self.NewPointGLay.addWidget(self.ringLabel, 1, 1)
        self.NewPointGLay.addWidget(self.ringField, 1, 2)

        self.arcLabel = qt.QLabel("Arc")
        self.arcLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.arcField = qt.QDoubleSpinBox()
        self.arcField.setRange(0.0, 180.00)
        self.NewPointGLay.addWidget(self.arcLabel, 1, 3)
        self.NewPointGLay.addWidget(self.arcField, 1, 4)

        self.depthLabel = qt.QLabel("Depth")
        self.depthLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.depthField = qt.QDoubleSpinBox()
        self.depthField.setRange(-999.99, 999.99)
        self.NewPointGLay.addWidget(self.depthLabel, 1, 5)
        self.NewPointGLay.addWidget(self.depthField, 1, 6)

        self.addBtn = qt.QPushButton("+")
        self.NewPointGLay.addWidget(self.addBtn, 0, 7, 2, 1)

        self.stereoPointsVBoxLayout.addLayout(self.NewPointGLay)

        self.disorient_btn = qt.QPushButton("Disorient ref image")
        self.disorient_btn.setToolTip(
            """In order to use the ijk coordinates, the IJK2RAS transform will be removed from the reference
            image selected and a new volume will be created. This volume will be of no use in Slicer, but can 
            be loaded in not medical imaging softwares (paraview, matlab...). This will also copy the 
            coordsConversion table to a new name in case you want to save it."""
        )
        self.stereoPointsVBoxLayout.addWidget(self.disorient_btn)

        self.referenceImage_selectionCombo.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onReferenceImageSelectedChanged
        )
        self.frameTransform_selectionCombo.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onFrameTransformSelectedChanged
        )
        self.fiducialGroup_selectionCombo.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onControlPointSelectedChanged
        )
        self.disorient_btn.connect("clicked(bool)", self.onDisorientBtnClicked)

        self.addBtn.connect("clicked(bool)", self.onAddBtnClicked)

        self.observers_list = []
        self.logic = stereo_pointsLogic()

    #########################################################################################################
    # connections
    #########################################################################################################
    def onReferenceImageSelectedChanged(self, newNode):
        # we only update the table if one is selected.
        if newNode is None:
            return
        if self.GetCoordTable():
            self.updatePointsCoordsFromXYZ(
                self.GetCoordTable(),
                newNode,
                self.frameTransform_selectionCombo.currentNode(),
            )
            self.disorient_btn.setText('Disorient "' + newNode.GetName() + '"')

    def onFrameTransformSelectedChanged(self, newNode):
        if (newNode is not None) and (
            self.GetCoordTable() is not None
        ):  # to not run the updatepoints when nothing is selected
            self.updatePointsCoordsFromXYZ(
                self.GetCoordTable(),
                self.referenceImage_selectionCombo.currentNode(),
                newNode,
            )

    def onControlPointSelectedChanged(self, newNode):
        # for each markupLineNode, we maintain a table with the coord conversion.
        # table nodes are names with the name of the markupLine with _coordsConversion as prefix
        if type(newNode) == slicer.vtkMRMLMarkupsLineNode:
            coordTableName = newNode.GetName() + "_coordsConversion"
        else:
            return

        coordTable_id = newNode.GetNodeReferenceID("stereotaxia_coordTable")

        # if the lineMarkup does not reference any coordtable yet, create it
        if coordTable_id is None:
            # prepare a new table
            newCoordTable = slicer.vtkMRMLTableNode()
            newCoordTable.SetName(coordTableName)
            newCoordTable.SetLocked(True)
            # columns:
            # x, y, z, r, a, d: leksell frame settings + depth
            # XYZ cartesian coordinates in leksell space
            # RAS coordinates in physical space (what slicer uses to place the points)
            # ijk coordinates in image space
            for col in [
                "Marker",
                "x",
                "y",
                "z",
                "r",
                "a",
                "d",
                "X",
                "Y",
                "Z",
                "R",
                "A",
                "S",
                "i",
                "j",
                "k",
            ]:
                c = newCoordTable.AddColumn()
                c.SetName(col)

            slicer.mrmlScene.AddNode(newCoordTable)
            # refererence the line from the table so we can get back to it
            newCoordTable.AddNodeReferenceID("stereotaxia_trajLine", newNode.GetID())
            newNode.AddNodeReferenceID("stereotaxia_coordTable", newCoordTable.GetID())
            # add an observer for both nodes, whenever one is renamed, the other one is renamed as well
            self.observers_list.append(
                [
                    newCoordTable,
                    newCoordTable.AddObserver(
                        vtk.vtkCommand.ModifiedEvent, self.onCoordTableModified
                    ),
                ]
            )
            self.observers_list.append(
                [
                    newNode,
                    newNode.AddObserver(
                        vtk.vtkCommand.ModifiedEvent, self.onControlPointNodeModified
                    ),
                ]
            )
            self.fiducialGroup_selectionCombo.setCurrentNode(newNode)
        self.pointTableView.setMRMLTableNode(self.GetCoordTable())
        self.pointTableView.setFirstRowLocked(True)
        self.pointTableView.show()

        self.placeWidget.setCurrentNode(self.fiducialGroup_selectionCombo.currentNode())

    def onCoordTableModified(self, updatedNode, eventType):
        lineNode = updatedNode.GetNodeReference("stereotaxia_trajLine")
        logging.debug(
            f"{updatedNode.GetName()} was modified. The associated line: {lineNode.GetName()} will be updated."
        )
        lineNode.SetName(updatedNode.GetName().replace("_coordsConversion", ""))

    def onControlPointNodeModified(self, updatedNode, eventType):
        coordTable = updatedNode.GetNodeReference("stereotaxia_coordTable")
        coordTable.SetName(updatedNode.GetName() + "_coordsConversion")
        self.logic.updatePointsAfterMove(
            coordTable,
            updatedNode,
            self.referenceImage_selectionCombo.currentNode(),
            self.frameTransform_selectionCombo.currentNode(),
        )

    def onAddBtnClicked(self):
        self.addPointFromStereoSetting(
            self.GetCoordTable(),
            self.xField.value,
            self.yField.value,
            self.zField.value,
            self.ringField.value,
            self.arcField.value,
            self.depthField.value,
            self.fiducialGroup_selectionCombo.currentNode().GetName()
            + "_"
            + self.nameField.text,
        )
        self.logic.table2ControlPoint(
            self.GetCoordTable(), self.fiducialGroup_selectionCombo.currentNode()
        )

        self.nameField.setText("")

    def onDisorientBtnClicked(self):
        import numpy as np

        T1_diso = slicer.vtkMRMLScalarVolumeNode()
        T1_diso.Copy(self.referenceImage_selectionCombo.currentNode())
        T1_diso.SetName(T1_diso.GetName() + "_noOrient_vtk")
        RAStoIJK = vtk.vtkMatrix4x4()
        RAStoIJK.DeepCopy(
            np.array([[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]).ravel()
        )
        T1_diso.SetRASToIJKMatrix(RAStoIJK)
        T1_diso.SetSpacing(
            self.referenceImage_selectionCombo.currentNode().GetSpacing()
        )
        T1_diso.SetOrigin([0, 0, 0])
        slicer.mrmlScene.AddNode(T1_diso)

    #########################################################################################################
    # end connections
    #########################################################################################################

    def GetCoordTable(self):
        coordTableID = (
            self.fiducialGroup_selectionCombo.currentNode().GetNodeReferenceID(
                "stereotaxia_coordTable"
            )
        )
        if coordTableID is not None:
            return slicer.mrmlScene.GetNodeByID(coordTableID)
        else:
            return None

    def addPointFromStereoSetting(self, tableNode, x, y, z, r, a, d, label):
        row = tableNode.AddEmptyRow()
        X, Y, Z, _ = self.logic.GetXYZcoordFromStereoSettings(
            x, y, z, r, a, d, paralellTraj=self.paralellTraj.currentText
        )

        trajTransform = slicer.vtkMRMLTransformNode()
        trajTransform.SetName(label)
        trajTransform.SetMatrixTransformToParent(
            slicer.util.vtkMatrixFromArray(
                self.logic.GetTrajectoryTransform(
                    x, y, z, r, a, paralellTraj=self.paralellTraj.currentText
                )
            )
        )
        slicer.mrmlScene.AddNode(trajTransform)

        tableNode.SetCellText(row, tableNode.GetColumnIndex("Marker"), label)

        tableNode.SetCellText(row, tableNode.GetColumnIndex("x"), "%.02f" % x)
        tableNode.SetCellText(row, tableNode.GetColumnIndex("y"), "%.02f" % y)
        tableNode.SetCellText(row, tableNode.GetColumnIndex("z"), "%.02f" % z)
        tableNode.SetCellText(row, tableNode.GetColumnIndex("r"), "%.02f" % r)
        tableNode.SetCellText(row, tableNode.GetColumnIndex("a"), "%.02f" % a)
        tableNode.SetCellText(row, tableNode.GetColumnIndex("d"), "%.02f" % d)

        tableNode.SetCellText(row, tableNode.GetColumnIndex("X"), "%.02f" % X)
        tableNode.SetCellText(row, tableNode.GetColumnIndex("Y"), "%.02f" % Y)
        tableNode.SetCellText(row, tableNode.GetColumnIndex("Z"), "%.02f" % Z)
        self.logic.updatePointsCoordsFromXYZ(
            tableNode,
            self.referenceImage_selectionCombo.currentNode(),
            self.frameTransform_selectionCombo.currentNode(),
        )

    ###################################################################################################
    # connection handler methods

    def cleanup(self):
        for i in self.observers_list:
            i[0].RemoveObserver(i[1])
        pass


##
# stereo_pointsLogic
#


class stereo_pointsLogic(ScriptedLoadableModuleLogic):
    def GetXYZcoordFromStereoSetings(self, x, y, z, r, a, d, paralellTraj="Central"):
        import numpy as np

        coord = self.GetTrajectoryTransform(
            x, y, z, r, a, paralellTraj=paralellTraj
        ) @ np.array([d, 0, 0, 1])
        return coord.tolist()

    def GetTrajectoryTransform(self, x, y, z, r, a, paralellTraj="Central"):
        import numpy as np

        r = (-r) * (np.pi / 180)
        ringTrans = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(r), -np.sin(r), 0],
                [0, np.sin(r), np.cos(r), 0],
                [0, 0, 0, 1],
            ]
        )

        a = (-a) * (np.pi / 180)
        arcTrans = np.array(
            [
                [np.cos(a), -np.sin(a), 0, 0],
                [np.sin(a), np.cos(a), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        cartesianTrans = np.array(
            [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]
        )

        # in the source reference space:
        # x is positive from th target onwards (minus is before the target)
        # y is positive to the left
        # z is positive front
        # --> for the Bengun:
        # center:                       [0,0,0]
        # anterior:                     [0,0,2]
        # posterior:                    [0,0,-2]
        # left lateral, right medial:   [0,2,0]
        # left medial, right lateral:   [0,-2,0]
        # for inserting paralell trajectories, the upper transform needs to be added at the end of trajTransform
        # ex for posterior: trajTrans = cartesianTrans @ ringTrans @ arcTrans @ [[1,0,0,0], [0,1,0,0], [0,0,1,-2], [0,0,0,1]]

        trajModifier = {
            "Central": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            "Anterior": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 2], [0, 0, 0, 1]],
            "Posterior": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -2], [0, 0, 0, 1]],
            "Left": [[1, 0, 0, 0], [0, 1, 0, 2], [0, 0, 1, 0], [0, 0, 0, 1]],
            "Right": [[1, 0, 0, 0], [0, 1, 0, -2], [0, 0, 1, 0], [0, 0, 0, 1]],
        }[paralellTraj]

        trajTrans = cartesianTrans @ ringTrans @ arcTrans @ trajModifier
        logging.debug("=============== trajectory transform ===============")

        logging.debug(trajTrans)

        return trajTrans

    def updatePointsCoordsFromXYZ(self, tableNode, refImage, frameTransform):
        for iRow in range(tableNode.GetNumberOfRows()):
            xyz = [
                float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex("X"))),
                float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex("Y"))),
                float(tableNode.GetCellText(iRow, tableNode.GetColumnIndex("Z"))),
            ]

            [R, A, S] = self.XYZtoRAS(xyz)
            [i, j, k] = self.RASpatToIJK(
                self.RAStoRASpat(self.XYZtoRAS(xyz), frameTransform), refImage
            )

            tableNode.SetCellText(iRow, tableNode.GetColumnIndex("R"), "%.02f" % R)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex("A"), "%.02f" % A)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex("S"), "%.02f" % S)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex("i"), "%.02f" % i)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex("j"), "%.02f" % j)
            tableNode.SetCellText(iRow, tableNode.GetColumnIndex("k"), "%.02f" % k)

    def updatePointsAfterMove(self, tableNode, fiducialNode, ref_img, frameTransform):
        XYZList = []
        RASList = []
        if fiducialNode.GetNumberOfControlPoints() == 0:
            return

        # GET XYZ Positions of all points
        for iControlPoint in range(fiducialNode.GetNumberOfControlPoints()):
            ras = [0, 0, 0]
            fiducialNode.GetNthControlPointPosition(iControlPoint, ras)
            RASList.append(ras)

            # Transform RAS to XYZ
            [X, Y, Z] = self.RAStoXYZ(ras)
            XYZList.append([X, Y, Z])

        # XYZList needs two entries
        if len(XYZList) > 1:
            # transform XYZ to xyzrad from both points
            xyzradList = self.XYZ2Leksell(XYZList)
            # logging.debug("Variable: xyzrad : %s", xyzradList)

            # store the old labels
            labels = []
            for irow in range(tableNode.GetNumberOfRows()):
                labels.append(
                    tableNode.GetCellText(irow, tableNode.GetColumnIndex("Marker"))
                )

            # Restart the whole filling
            # always remove the first
            for iRow in range(tableNode.GetNumberOfRows()):
                tableNode.RemoveRow(0)

            for irow in range(len(xyzradList)):
                label = labels[irow]
                [x, y, z, r, a, d] = xyzradList[irow]
                [X, Y, Z] = XYZList[irow]
                [R, A, S] = RASList[irow]
                [i, j, k] = self.RASpatToIJK(
                    self.RAStoRASpat([R, A, S], frameTransform), ref_img
                )

                # Refill Table
                row = tableNode.AddEmptyRow()
                tableNode.SetCellText(row, tableNode.GetColumnIndex("Marker"), label)

                tableNode.SetCellText(row, tableNode.GetColumnIndex("x"), "%.02f" % x)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("y"), "%.02f" % y)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("z"), "%.02f" % z)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("r"), "%.02f" % r)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("a"), "%.02f" % a)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("d"), "%.02f" % d)

                tableNode.SetCellText(row, tableNode.GetColumnIndex("X"), "%.02f" % X)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("Y"), "%.02f" % Y)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("Z"), "%.02f" % Z)

                tableNode.SetCellText(row, tableNode.GetColumnIndex("R"), "%.02f" % R)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("A"), "%.02f" % A)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("S"), "%.02f" % S)

                tableNode.SetCellText(row, tableNode.GetColumnIndex("i"), "%.02f" % i)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("j"), "%.02f" % j)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("k"), "%.02f" % k)
        else:
            # store the old labels
            labels = []
            for irow in range(tableNode.GetNumberOfRows()):
                labels.append(
                    tableNode.GetCellText(irow, tableNode.GetColumnIndex("Marker"))
                )

            # Restart the whole filling
            # always remove the first
            for iRow in range(tableNode.GetNumberOfRows()):
                tableNode.RemoveRow(0)

            for irow in range(len(XYZList)):
                label = labels[irow]
                [X, Y, Z] = XYZList[irow]
                [R, A, S] = RASList[irow]
                [i, j, k] = self.RASpatToIJK(
                    self.RAStoRASpat([R, A, S], frameTransform), ref_img
                )

                # Refill Table
                row = tableNode.AddEmptyRow()
                tableNode.SetCellText(row, tableNode.GetColumnIndex("Marker"), label)

                tableNode.SetCellText(row, tableNode.GetColumnIndex("X"), "%.02f" % X)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("Y"), "%.02f" % Y)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("Z"), "%.02f" % Z)

                tableNode.SetCellText(row, tableNode.GetColumnIndex("R"), "%.02f" % R)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("A"), "%.02f" % A)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("S"), "%.02f" % S)

                tableNode.SetCellText(row, tableNode.GetColumnIndex("i"), "%.02f" % i)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("j"), "%.02f" % j)
                tableNode.SetCellText(row, tableNode.GetColumnIndex("k"), "%.02f" % k)

    def XYZ2Leksell(self, XYZList):
        import math
        import numpy as np

        xyzradList = []

        # Coordinates of the two points
        x1, y1, z1 = XYZList[0]
        x2, y2, z2 = XYZList[1]

        # Define a vector as a tuple of three floats representing its XYZ components

        vector = np.array([x2 - x1, y2 - y1, z1 - z2])

        # Calculate the length of the vector
        distance = np.linalg.norm(vector)

        # Calculate the arc and ring of the vector
        # angle between the negative X-axis and the vector
        arc = math.degrees(math.acos(vector[0] / distance))

        # Calculate the angle between the Y-axis and the vector
        distYZPlane = np.linalg.norm(np.array([y2 - y1, z1 - z2]))
        ring = math.degrees(math.acos(vector[1] / distYZPlane))

        if vector[2] > 0 or arc == 180:
            arc = 180 - arc
            distance = distance * -1
        else:
            ring = 180 - ring

        xyzradList.append([x1, y1, z1, ring, arc, 0])
        xyzradList.append([x1, y1, z1, ring, arc, distance])
        return xyzradList

    def fiducial2Table(self, tableNode, fiducialNode):
        for iRow in range(tableNode.GetNumberOfRows()):
            tableNode.RemoveRow(0)  # always remove the first
        for iControlPoint in range(fiducialNode.GetNumberOfControlPoints()):
            thisPosRAS = [0, 0, 0]
            fiducialNode.GetNthControlPointPosition(iControlPoint, thisPosRAS)
            thisLabel = fiducialNode.GetNthControlPointLabel(iControlPoint)

            r = tableNode.AddEmptyRow()
            tableNode.SetCellText(r, tableNode.GetColumnIndex("Marker"), thisLabel)
            tableNode.SetCellText(
                r, tableNode.GetColumnIndex("R"), "%.02f" % thisPosRAS[0]
            )
            tableNode.SetCellText(
                r, tableNode.GetColumnIndex("A"), "%.02f" % thisPosRAS[1]
            )
            tableNode.SetCellText(
                r, tableNode.GetColumnIndex("S"), "%.02f" % thisPosRAS[2]
            )

    def table2ControlPoint(self, tableNode, fiducialNode):
        fiducialNode.RemoveAllControlPoints()

        for iRow in range(tableNode.GetNumberOfRows()):
            fiducialNode.AddControlPointWorld(
                vtk.vtkVector3d(
                    [
                        float(
                            tableNode.GetCellText(iRow, tableNode.GetColumnIndex("R"))
                        ),
                        float(
                            tableNode.GetCellText(iRow, tableNode.GetColumnIndex("A"))
                        ),
                        float(
                            tableNode.GetCellText(iRow, tableNode.GetColumnIndex("S"))
                        ),
                    ]
                ),
                tableNode.GetCellText(iRow, tableNode.GetColumnIndex("Marker")),
            )
            fiducialNode.SetLocked(True)

    def XYZtoRAS(self, xyz):
        import numpy as np

        return np.dot(self.GetXYZtoRASTrans(), np.array(xyz + [1])).tolist()[:3]

    def GetXYZtoRASTrans(self):
        if slicer.mrmlScene.GetNodesByName("leksell2RAS").GetNumberOfItems() == 0:
            slicer.util.loadTransform(
                os.path.join(os.path.split(__file__)[0], "Resources", "leksell2RAS.h5")
            )

        return self.transformNode_to_numpy4x4(
            [
                i
                for i in slicer.mrmlScene.GetNodesByClass("vtkMRMLTransformNode")
                if i.GetName().startswith("leksell2RAS")
            ][0]
        )

    def RAStoXYZ(self, ras):
        import numpy as np

        return np.dot(self.GetRAStoXYZTrans(), np.array(ras + [1])).tolist()[:3]

    def GetRAStoXYZTrans(self):
        import numpy as np

        if slicer.mrmlScene.GetNodesByName("leksell2RAS").GetNumberOfItems() == 0:
            slicer.util.loadTransform(
                os.path.join(os.path.split(__file__)[0], "Resources", "leksell2RAS.h5")
            )

        XYZ2RAStransformation = self.transformNode_to_numpy4x4(
            [
                i
                for i in slicer.mrmlScene.GetNodesByClass("vtkMRMLTransformNode")
                if i.GetName().startswith("leksell2RAS")
            ][0]
        )
        RAS2XYZtransformation = np.linalg.inv(XYZ2RAStransformation)
        return RAS2XYZtransformation

    def GetRAStoRASpatTrans(self, currentFrameTransform):
        import numpy as np

        return self.transformNode_to_numpy4x4(currentFrameTransform)

    def RAStoRASpat(self, xyz, frametransform):
        import numpy as np

        res = np.dot(
            self.GetRAStoRASpatTrans(frametransform), np.array(xyz + [1])
        ).tolist()[:3]
        return res

    def GetRASpatToIJKtrans(self, ref_img):
        import numpy as np

        parentTransformNode = ref_img.GetParentTransformNode()
        if type(parentTransformNode) not in [
            type(None),
            slicer.vtkMRMLLinearTransformNode,
        ]:
            raise ValueError("The reference image can only be linearly transformed")

        rasToVolumeRas = vtk.vtkMatrix4x4()
        slicer.vtkMRMLTransformNode.GetMatrixTransformBetweenNodes(
            None, ref_img.GetParentTransformNode(), rasToVolumeRas
        )
        # convert the transform to a vtkMatrix4x4

        volumeRasToIjk = vtk.vtkMatrix4x4()
        ref_img.GetRASToIJKMatrix(volumeRasToIjk)

        rasToIjk = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Multiply4x4(volumeRasToIjk, rasToVolumeRas, rasToIjk)
        IJKtoPatRAS = np.array(
            [rasToIjk.GetElement(i, j) for i in range(4) for j in range(4)]
        ).reshape([4, 4])

        return IJKtoPatRAS

    def RASpatToIJK(self, xyz, ref_img):
        import numpy as np

        return np.dot(self.GetRASpatToIJKtrans(ref_img), np.array(xyz + [1])).tolist()[
            :3
        ]

    def GetLeksell2IJKtrans(self, x, y, z, r, a, ref_img):
        import numpy as np

        return np.dot(
            self.GetRASpatToIJKtrans(ref_img),
            np.dot(
                self.GetRAStoRASpatTrans(),
                np.dot(
                    self.GetXYZtoRASTrans(), self.GetTrajectoryTransform(x, y, z, r, a)
                ),
            ),
        )

    def GetLeksell2RAStrans(self, x, y, z, r, a):
        import numpy as np

        return np.dot(
            self.GetXYZtoRASTrans(), self.GetTrajectoryTransform(x, y, z, r, a)
        )

    def transformNode_to_numpy4x4(self, node):
        import numpy as np
        from vtk import vtkMatrix4x4

        vtkMat = vtkMatrix4x4()
        node.GetMatrixTransformFromWorld(vtkMat)

        return np.array(
            [vtkMat.GetElement(i, j) for i in range(4) for j in range(4)]
        ).reshape([4, 4])


class stereo_pointsTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_stereo_points1()

    def test_stereo_points1(self):
        """Ideally you should have several levels of tests.    At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).    At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.    For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")
        #
        # first, get some data
        #
        import SampleData

        SampleData.downloadFromURL(
            nodeNames="FA",
            fileNames="FA.nrrd",
            uris="http://slicer.kitware.com/midas3/download?items=5767",
        )
        self.delayDisplay("Finished with download and loading")

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = stereo_pointsLogic()
        self.assertIsNotNone(logic.hasImageData(volumeNode))
        self.delayDisplay("Test passed!")
