import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# probeView
#

class probeView(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Probe View" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Navigation"]
    self.parent.dependencies = []
    self.parent.contributors = ["Dorian Vogel (FHNW, LiU), Marc Jermann (FHNW)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = u"""
This file was originally developed by Dorian Vogel, (Fachhochschule Nordwestschweitz, Muttenz, Switzerland; Linköping University, Linköping, Sweden). Financial support: FHNW, SSF, VR.
""" # replace with organization, grant and thanks.

#
# probeViewWidget
#

class probeViewWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLMarkupsLineNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "line placed along the trajectory." )
    parametersFormLayout.addRow("trajectory: ", self.inputSelector)

    self.enableRed = qt.QCheckBox()
    self.enableRed.checked = 1
    self.enableRed.setToolTip("If checked, the red view will be changed to probe view.")
    parametersFormLayout.addRow("Enable for Red", self.enableRed)

    self.enableYellow = qt.QCheckBox()
    self.enableYellow.checked = 1
    self.enableYellow.setToolTip("If checked, the yellow view will be changed to probe view.")
    parametersFormLayout.addRow("Enable for Yellow", self.enableYellow)    
    
    self.enableGreen = qt.QCheckBox()
    self.enableGreen.checked = 1
    self.enableGreen.setToolTip("If checked, the green view will be changed to probe view.")
    parametersFormLayout.addRow("Enable for Green", self.enableGreen)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)
    
    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode()

  def onApplyButton(self):
    logic = probeViewLogic()
    #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    #imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.enableRed.checked, self.enableYellow.checked, self.enableGreen.checked)

#
# probeViewLogic
#

class probeViewLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
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

  def isValidInputOutputData(self, inputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    return True

  def run(self, inputLine, en_Red, en_Yellow, en_Green):
    """
    Run the actual algorithm
    """
    import numpy as np
    start = inputLine.GetLineStartPosition()
    end = inputLine.GetLineEndPosition()
    normalVect = np.array(end) - np.array(start)

    normalVector_unit = normalVect/ np.linalg.norm(normalVect)

    d=np.linalg.norm(normalVector_unit[-2:])

    R = np.matmul(\
      np.array([  [1, 0                       ,0                       ],  \
                  [0, normalVector_unit[2]/d  , normalVector_unit[1]/d ],  \
                  [0, -normalVector_unit[1]/d , normalVector_unit[2]/d ]   \
                  ])\
      , \
      np.array([  [d                    , 0, normalVector_unit[0] ], \
                  [0                    , 1, 0                    ], \
                  [-normalVector_unit[0], 0, d                    ]  \
                  ])\
      )

    #based on https://www.slicer.org/wiki/Documentation/Nightly/ScriptRepository#Manipulating_objects_in_the_slice_viewer
    def setSlicePoseFromSliceNormalAndPosition(sliceNode, sliceNormal, slicePosition, defaultViewUpDirection=None, backupViewRightDirection=None):
      """
      Set slice pose from the provided plane normal and position. View up direction is determined automatically,
      to make view up point towards defaultViewUpDirection.
      :param defaultViewUpDirection Slice view will be spinned in-plane to match point approximately this up direction. Default: patient superior.
      :param backupViewRightDirection Slice view will be spinned in-plane to match point approximately this right direction
          if defaultViewUpDirection is too similar to sliceNormal. Default: patient left.
      """
      # Fix up input directions
      if defaultViewUpDirection is None:
          defaultViewUpDirection = [0,0,1]
      if backupViewRightDirection is None:
          backupViewRightDirection = [-1,0,0]
      if sliceNormal[1]>=0:
          sliceNormalStandardized = sliceNormal
      else:
          sliceNormalStandardized = [-sliceNormal[0], -sliceNormal[1], -sliceNormal[2]]
      # Compute slice axes
      sliceNormalViewUpAngle = vtk.vtkMath.AngleBetweenVectors(sliceNormalStandardized, defaultViewUpDirection)
      angleTooSmallThresholdRad = 0.25 # about 15 degrees
      if sliceNormalViewUpAngle > angleTooSmallThresholdRad and sliceNormalViewUpAngle < vtk.vtkMath.Pi() - angleTooSmallThresholdRad:
          viewUpDirection = defaultViewUpDirection
          sliceAxisY = viewUpDirection
          sliceAxisX = [0, 0, 0]
          vtk.vtkMath.Cross(sliceAxisY, sliceNormalStandardized, sliceAxisX)
      else:
          sliceAxisX = backupViewRightDirection
      # Set slice axes
      sliceNode.SetSliceToRASByNTP(sliceNormalStandardized[0], sliceNormalStandardized[1], sliceNormalStandardized[2],
          sliceAxisX[0], sliceAxisX[1], sliceAxisX[2],
          slicePosition[0], slicePosition[1], slicePosition[2], 0)
    
    if en_Red:
      sliceNode = slicer.mrmlScene.GetNodesByName("Red").GetItemAsObject(0)
      setSlicePoseFromSliceNormalAndPosition(sliceNode, R[:,2].tolist(), start)
    if en_Yellow:
      sliceNode = slicer.mrmlScene.GetNodesByName("Yellow").GetItemAsObject(0)
      setSlicePoseFromSliceNormalAndPosition(sliceNode, R[:,0].tolist(), start)
    if en_Green:
      sliceNode = slicer.mrmlScene.GetNodesByName("Green").GetItemAsObject(0)
      setSlicePoseFromSliceNormalAndPosition(sliceNode, R[:,1].tolist(), start)
    
    if not self.isValidInputOutputData(inputLine):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputFiducials': inputLine.GetID()}
    
    ## Capture screenshot
    #if enableScreenshots:
      #self.takeScreenshot('probeViewTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class probeViewTest(ScriptedLoadableModuleTest):
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
    self.test_probeView1()

  def test_probeView1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
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
    logic = probeViewLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
