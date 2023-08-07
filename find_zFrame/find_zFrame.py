# -*- coding: latin-1 -*-
import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# find_zFrame
#

class find_zFrame(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Leksell Frame localization"
        self.parent.categories = ["Navigation"]
        self.parent.dependencies = []
        self.parent.contributors = ["Dorian Vogel (FHNW, LiU), Marc Jermann (FHNW)"] # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = u"""
This module helps segmenting the Z fiducial created by the Leskell frame in MR/CT. The segmented frame can then be registered to an ideal frame, in order to obtain the transformation between the slicer reference space and the stereotactic space in the patient's image.
"""
        #self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = u"""
This file was originally developed by Dorian Vogel, (Fachhochschule Nordwestschweitz, Muttenz, Switzerland; Linköping University, Linköping, Sweden). Financial support: FHNW, SSF, VR.
"""

#
# find_zFrameWidget
#

class find_zFrameWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Instantiate and connect widgets ...

        #
        # Segmentation area
        #
        segmentationCollapsibleButton = ctk.ctkCollapsibleButton()
        segmentationCollapsibleButton.text = "Frame segmentation"
        self.layout.addWidget(segmentationCollapsibleButton)

        # Layout within the dummy collapsible button
        segmentationFormLayout = qt.QFormLayout(segmentationCollapsibleButton)

        #
        # input volume selector
        #
        self.inputSelector = slicer.qMRMLNodeComboBox()
        self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.inputSelector.selectNodeUponCreation = True
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False
        self.inputSelector.noneEnabled = False
        self.inputSelector.showHidden = False
        self.inputSelector.showChildNodeTypes = False
        self.inputSelector.setMRMLScene( slicer.mrmlScene )
        self.inputSelector.setToolTip( "Pick the input to the algorithm." )
        segmentationFormLayout.addRow("Input Volume: ", self.inputSelector)

        #
        # output volume selector
        #
        self.outSegmentSelector = slicer.qMRMLNodeComboBox()
        self.outSegmentSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.outSegmentSelector.selectNodeUponCreation = True
        self.outSegmentSelector.addEnabled = True
        self.outSegmentSelector.editEnabled = True
        self.outSegmentSelector.removeEnabled = True
        self.outSegmentSelector.noneEnabled = False
        self.outSegmentSelector.showHidden = False
        self.outSegmentSelector.showChildNodeTypes = False
        self.outSegmentSelector.setMRMLScene( slicer.mrmlScene )
        self.outSegmentSelector.setToolTip( "Pick the output to the algorithm." )
        segmentationFormLayout.addRow("Output Segmentation image: ", self.outSegmentSelector)
        
        #
        # output model selector
        #
        self.outSegmtModelSelector = slicer.qMRMLNodeComboBox()
        self.outSegmtModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.outSegmtModelSelector.selectNodeUponCreation = True
        self.outSegmtModelSelector.addEnabled = True
        self.outSegmtModelSelector.editEnabled = True
        self.outSegmtModelSelector.removeEnabled = True
        self.outSegmtModelSelector.noneEnabled = False
        self.outSegmtModelSelector.showHidden = False
        self.outSegmtModelSelector.showChildNodeTypes = False
        self.outSegmtModelSelector.setMRMLScene( slicer.mrmlScene )
        self.outSegmtModelSelector.setToolTip( "Output model of the ZFrame" )
        segmentationFormLayout.addRow("Output Segmentation model: ", self.outSegmtModelSelector)


        #
        # Image type radios
        #
        self.imgType='CT'
        self.imgTypeHBox = qt.QHBoxLayout()
        self.ctTypRadio =    qt.QRadioButton("CT")
        self.MRTypRadio =    qt.QRadioButton("MR (experimental)")
        self.ctTypRadio.setChecked(True)
        self.MRTypRadio.setChecked(False)
        self.imgTypeHBox.addWidget(self.MRTypRadio)
        self.imgTypeHBox.addWidget(self.ctTypRadio)
        segmentationFormLayout.addRow("Image modality: ", self.imgTypeHBox)
        
        self.inputSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onInputSelectorChanged)
        self.onInputSelectorChanged(self.inputSelector.currentNode())
        
        #
        # Apply Button
        #
        self.segmentButton = qt.QPushButton("Segment")
        self.segmentButton.toolTip = "Run the algorithm."
        self.segmentButton.enabled = False
        segmentationFormLayout.addRow(self.segmentButton)

        # connections
        self.segmentButton.connect('clicked(bool)', self.onsegmentButton)
        self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        self.outSegmentSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        self.MRTypRadio.connect('toggled(bool)', self.onMRTypeToggle)
        self.ctTypRadio.connect('toggled(bool)', self.onctTypeToggle)

        self.onSelect()

        ###################################################################################################
        
        #
        # Frame Generation area
        #
        frameGenerationCollapsibleButton = ctk.ctkCollapsibleButton()
        frameGenerationCollapsibleButton.text = "Reference Frame"
        self.layout.addWidget(frameGenerationCollapsibleButton)

        frameGenFormLayout = qt.QFormLayout(frameGenerationCollapsibleButton)

        #
        # checkboxes for the presence of fiducials
        #
        self.checkboxesGridLayout = qt.QGridLayout()
        # Anterior
        self.anteriorCheck = qt.QCheckBox('Anterior')
        self.checkboxesGridLayout.addWidget(self.anteriorCheck, 0,1, qt.Qt.AlignCenter)
        # Posterior
        self.posteriorCheck = qt.QCheckBox('Posterior')
        self.checkboxesGridLayout.addWidget(self.posteriorCheck, 2,1, qt.Qt.AlignCenter)
        # Left
        self.leftCheck = qt.QCheckBox('Left')
        self.checkboxesGridLayout.addWidget(self.leftCheck, 1,0, qt.Qt.AlignRight)
        # Right
        self.rightCheck = qt.QCheckBox('Right')
        self.checkboxesGridLayout.addWidget(self.rightCheck, 1,2, qt.Qt.AlignLeft)
        # Superior
        self.superiorCheck = qt.QCheckBox('Superior')
        self.checkboxesGridLayout.addWidget(self.superiorCheck, 1,1, qt.Qt.AlignCenter)
        
        frameGenFormLayout.addRow('fiducials present:', self.checkboxesGridLayout)
        
        self.outIdealModelSelector = slicer.qMRMLNodeComboBox()
        self.outIdealModelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.outIdealModelSelector.selectNodeUponCreation = True
        self.outIdealModelSelector.addEnabled = True
        self.outIdealModelSelector.removeEnabled = True
        self.outIdealModelSelector.noneEnabled = False
        self.outIdealModelSelector.showHidden = False
        self.outIdealModelSelector.showChildNodeTypes = False
        self.outIdealModelSelector.setMRMLScene( slicer.mrmlScene )
        self.outIdealModelSelector.setToolTip( "Pick the output model." )
        self.outIdealModelSelector.baseName = 'zFrameIdeal'
        frameGenFormLayout.addRow("Output model: ", self.outIdealModelSelector)
        
        self.genModel = qt.QPushButton('Generate Model')
        self.genModel.enabled = False
        frameGenFormLayout.addRow(self.genModel)
        
        self.fiducialsPresent_list = list()
        self.anteriorCheck.connect('stateChanged(int)', self.onAnteriorChanged)
        self.posteriorCheck.connect('stateChanged(int)', self.onPosteriorChanged)
        self.leftCheck.connect('stateChanged(int)', self.onLeftChanged)
        self.rightCheck.connect('stateChanged(int)', self.onRightChanged)
        self.superiorCheck.connect('stateChanged(int)', self.onSuperiorChanged)
        self.genModel.connect('clicked(bool)', self.onGenerateButton)
                
        ###################################################################################################
        
        frameRegistrationCollapsibleButton = ctk.ctkCollapsibleButton()
        frameRegistrationCollapsibleButton.text = 'Register Z Frames'
        self.layout.addWidget(frameRegistrationCollapsibleButton)
        
        frameRegFormLayout = qt.QFormLayout(frameRegistrationCollapsibleButton)
        
        self.movingZselector = slicer.qMRMLNodeComboBox()
        self.movingZselector.nodeTypes = ['vtkMRMLModelNode']
        self.movingZselector.selectNodeUponCreation = True
        self.movingZselector.addEnabled = False
        self.movingZselector.removeEnabled = False
        self.movingZselector.noneEnabled = False
        self.movingZselector.showHidden = False
        self.movingZselector.showChildNodeTypes = False
        self.movingZselector.setMRMLScene( slicer.mrmlScene )
        self.movingZselector.setToolTip( "pick the model of the moving Z" )
        frameRegFormLayout.addRow("Moving: ", self.movingZselector)
        
        self.fixedZselector = slicer.qMRMLNodeComboBox()
        self.fixedZselector.nodeTypes = ['vtkMRMLModelNode']
        self.fixedZselector.selectNodeUponCreation = True
        self.fixedZselector.addEnabled = False
        self.fixedZselector.removeEnabled = False
        self.fixedZselector.noneEnabled = False
        self.fixedZselector.showHidden = False
        self.fixedZselector.showChildNodeTypes = False
        self.fixedZselector.setMRMLScene( slicer.mrmlScene )
        self.fixedZselector.setToolTip( "pick the model of the fixed Z" )
        frameRegFormLayout.addRow("Fixed: ", self.fixedZselector)
        
        self.outputTransformSelector = slicer.qMRMLNodeComboBox()
        self.outputTransformSelector.nodeTypes = ['vtkMRMLTransformNode']
        self.outputTransformSelector.selectNodeUponCreation = True
        self.outputTransformSelector.addEnabled = True
        self.outputTransformSelector.removeEnabled = True
        self.outputTransformSelector.noneEnabled = False
        self.outputTransformSelector.showHidden = False
        self.outputTransformSelector.showChildNodeTypes = False
        self.outputTransformSelector.setMRMLScene( slicer.mrmlScene )
        self.outputTransformSelector.baseName = "zFrame_registration"
        self.outputTransformSelector.setToolTip( "transform that alignes moving to fixed" )
        frameRegFormLayout.addRow("Output transform: ", self.outputTransformSelector)
        
        self.registerPushButton = qt.QPushButton('Register')
        self.registerPushButton.enabled = False
        frameRegFormLayout.addRow(self.registerPushButton)
        
        self.movingZselector.connect("currentNodeChanged(vtkMRMLNode*)", self.onMovingZselectionChanged)
        self.fixedZselector.connect("currentNodeChanged(vtkMRMLNode*)", self.onfixedZselectionChanged)
        
        self.registerPushButton.connect('clicked(bool)', self.onRegisterPushButtonClicked)
        
        ###################################################################################################

        # Add vertical spacer
        self.layout.addStretch(1)
        
        #### instantiate the logic
        self.logic = find_zFrameLogic()
    #########################################################################################################

        
    def onInputSelectorChanged(self, newNode):
        if type(newNode)==type(slicer.vtkMRMLScalarVolumeNode()):
            self.outSegmentSelector.baseName = "ZFrame_"+newNode.GetName() + '_img'
            self.outSegmtModelSelector.baseName = "ZFrame_"+newNode.GetName() + '_model'


    def onSelect(self):
        self.segmentButton.enabled = self.inputSelector.currentNode() and self.outSegmentSelector.currentNode()
    
    def onMRTypeToggle(self, checked):
            if checked: self.imgType = 'MR'
            #print("imgType: %s"%self.imgType)
    def onctTypeToggle(self, checked):
            if checked: self.imgType = 'CT'
            #print("imgType: %s"%self.imgType)
    
    def onsegmentButton(self):
        self.logic.run_leksellFiducialsSegmentation(self.inputSelector.currentNode(), self.outSegmentSelector.currentNode(), self.imgType, self.outSegmtModelSelector.currentNode())
        slicer.util.setSliceViewerLayers(background=self.inputSelector.currentNode())

        #self.outSegmtModelSelector.currentNode().SetDisplayVisibility(True)
        self.outSegmtModelSelector.currentNode().GetDisplayNode().SetColor(1,0,0)
    #########################################################################################################
    
    def onAnteriorChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['A']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='A']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
    
    def onPosteriorChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['P']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='P']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
        
    def onLeftChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['L']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='L']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
        
    def onRightChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['R']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='R']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
        
    def onSuperiorChanged(self, newState):
        if newState == 2:
            self.fiducialsPresent_list = list(set(self.fiducialsPresent_list + ['S']))
            self.genModel.enabled = True
        else:
            self.fiducialsPresent_list = [i for i in self.fiducialsPresent_list if i!='S']
        #print("fiducials present: %s"%str(self.fiducialsPresent_list))
    
    def onGenerateButton(self):
        self.logic.run_generateIdealLeksellFiducials(self.fiducialsPresent_list, self.outIdealModelSelector.currentNode())

    #########################################################################################################

    def onMovingZselectionChanged(self, newNode):
        if newNode != self.fixedZselector.currentNode() and type(newNode) == type(slicer.vtkMRMLModelNode()):
            self.registerPushButton.enabled = True
        else:
            self.registerPushButton.enabled = False
    
    def onfixedZselectionChanged(self, newNode):
        if newNode != self.movingZselector.currentNode() and type(newNode) == type(slicer.vtkMRMLModelNode()):
            self.registerPushButton.enabled = True
        else:
            self.registerPushButton.enabled = False
        
    def onRegisterPushButtonClicked(self):
        self.logic.run_zFrameRegistration(self.movingZselector.currentNode(),
                                          self.fixedZselector.currentNode(),
                                          self.outputTransformSelector.currentNode())
        slicer.util.loadTransform(os.path.join(os.path.split(__file__)[0], 'Ressources/Leksell_Frame/leksell2RAS.h5'))
    
    #########################################################################################################

    def cleanup(self):
        pass


#
# find_zFrameLogic
#

class find_zFrameLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.    The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def hasImageData(self,volumeNode):
        """This is an example logic method that
        returns true if the passed in volume
        node has valid image data
        """
        if not volumeNode:
            logging.debug('hasImageData failed: no volume node')
            return False
        if volumeNode.GetImageData() is None:
            logging.debug('hasImageData failed: no image data in volume node')
            return False
        return True

    def isValidInputOutputData(self, inputVolumeNode, outputLabelMapNode):
        """Validates if the output is not the same as input
        """
        if not inputVolumeNode:
            logging.debug('isValidInputOutputData failed: no input volume node defined')
            return False
        if not outputLabelMapNode:
            logging.debug('isValidInputOutputData failed: no output volume node defined')
            return False
        if inputVolumeNode.GetID()==outputLabelMapNode.GetID():
            logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
            return False
        return True

    def run_leksellFiducialsSegmentation(self, inputVolume, outputVolume, imgType, outputModel):
        """
        Run the actual algorithm
        """

        if not self.isValidInputOutputData(inputVolume, outputVolume):
            slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
            return False

        logging.info('Fiducial segmentation started')

        # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
        from Ressources.segmentZframe import segment_zFrame_slicer
        segment_zFrame_slicer(inputVolume, outputVolume, imgType)
        
        # create a segmentation to show the frame in 3d
        zFrameSegmentationNode = slicer.vtkMRMLSegmentationNode()
        zFrameSegmentationNode.SetName("zFrame_seg")
        slicer.mrmlScene.AddNode(zFrameSegmentationNode)
        zFrameSegmentationNode.CreateDefaultDisplayNodes()  # only needed for display
        zFrameSegmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(outputVolume)
        zFrameSegmentationNode.GetSegmentation().AddEmptySegment('zFrame')
        
        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
        slicer.mrmlScene.AddNode(segmentEditorNode)
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(zFrameSegmentationNode)
        segmentEditorWidget.setSourceVolumeNode(outputVolume)

        segmentEditorWidget.setActiveEffectByName("Threshold")
        effect = segmentEditorWidget.activeEffect()
        maxVal = slicer.util.arrayFromVolume(outputVolume).max()
        effect.setParameter("MinimumThreshold",str(1.1))
        effect.setParameter("MaximumThreshold",str(maxVal))
        effect.self().onApply()
        
        #https://www.slicer.org/wiki/Documentation/Nightly/ScriptRepository
        import vtkSegmentationCorePython as vtkSegmentationCore
        segmentation = zFrameSegmentationNode.GetSegmentation()

        # Turn of surface smoothing
        segmentation.SetConversionParameter('Smoothing factor','0.0')

        # Recreate representation using modified parameters (and default conversion path)
        segmentation.CreateRepresentation(vtkSegmentationCore.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())
        
        
        framePoly = vtk.vtkPolyData()
        zFrameSegmentationNode.GetClosedSurfaceRepresentation(zFrameSegmentationNode.GetSegmentation().GetNthSegmentID(0), framePoly)
        outputModel.SetAndObservePolyData(framePoly)
        outputModel.CreateDefaultDisplayNodes()
        zFrameSegmentationNode.SetDisplayVisibility(False)
        
        logging.info('Fiducial segmentation finished')

        return True
        
    def run_generateIdealLeksellFiducials(self, fiducialList, outputModelNode):
        
        logging.info('Ideal frame generation started')
        
        import vtk, os
        fileNames = [os.path.join(os.path.split(__file__)[0], 'Ressources/Leksell_Frame/ZFrame_'+i+'.stl') for i in fiducialList]
        readers = [vtk.vtkSTLReader() for i in fileNames]
        appender = vtk.vtkAppendPolyData()
        for (thisReader,thisFile) in zip(readers, fileNames):
            thisReader.SetFileName(thisFile)
            appender.AddInputConnection(thisReader.GetOutputPort())
        appender.Update()
        #writer = vtk.vtkXMLPolyDataWriter()
        #writer.SetFileName(os.path.join(os.path.split(__file__)[0], 'test.vtp'))
        #writer.SetInputConnection(appender.GetOutputPort())
        #writer.Update()
        outputModelNode.SetPolyDataConnection(appender.GetOutputPort())
        outputModelNode.CreateDefaultDisplayNodes()
        outputModelNode.SetDisplayVisibility(True)
        outputModelNode.GetDisplayNode().SetColor(0,1,0)
        
        logging.info('Ideal frame generation done')
        
        return True

    ## Iterative Closest Point surface to suface registration, based on https://github.com/DCBIA-OrthoLab/CMFreg/blob/b5898deaf8e2017cefcaf03d61aba78e625fc924/SurfaceRegistration/SurfaceRegistration.py#L707
    def run_zFrameRegistration(self, movingZ, referenceZ, outputTransform):
        """Run the actual algorithm"""
        
        logging.info('ICP registration started')
        
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(movingZ.GetPolyData())
        icp.SetTarget(referenceZ.GetPolyData())
        icp.GetLandmarkTransform().SetModeToRigidBody()
        #icp.SetMaximumNumberOfIterations(1000)
        #icp.SetMaximumMeanDistance(0.001)
        #icp.SetMaximumNumberOfLandmarks(numberOfLandmarks)
        #icp.SetCheckMeanDistance(int(checkMeanDistance))
        icp.CheckMeanDistanceOn()
        icp.SetStartByMatchingCentroids(True)
        icp.Update()
        outputMatrix = vtk.vtkMatrix4x4()
        icp.GetMatrix(outputMatrix)
        outputTransform.SetMatrixTransformToParent(outputMatrix)
        
        logging.info('ICP registration done')

        return True

class find_zFrameTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_find_zFrame1()

    def test_find_zFrame1(self):
        """ Ideally you should have several levels of tests.    At the lowest level
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
            nodeNames='FA',
            fileNames='FA.nrrd',
            uris='http://slicer.kitware.com/midas3/download?items=5767')
        self.delayDisplay('Finished with download and loading')

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = find_zFrameLogic()
        self.assertIsNotNone( logic.hasImageData(volumeNode) )
        self.delayDisplay('Test passed!')
