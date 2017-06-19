from __main__ import vtk, qt, ctk, slicer

import os
import math
import vtk.util.numpy_support, numpy
import vtkSegmentationCorePython as vtkSegmentationCore

class ModelUndercutRemoval:
    def __init__(self, parent):
        parent.title = "Model Undercut Removal"
        parent.categories = ["Examples"]
        parent.dependencies = []
        parent.contributors = ["Patrick Moore"] # replace with "Firstname Lastname (Org)"
        parent.helpText = """
        Example of scripted loadable extension for the HelloPython tutorial.
        """
        parent.acknowledgementText = """Independently developed for the good of the world""" # replace with organization, grant and thanks.
        self.parent = parent

#
# qHelloPythonWidget
#

class ModelUndercutRemovalWidget:
    def __init__(self, parent = None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):
        # Instantiate and connect widgets ...

        # Collapsible button
        self.sampleCollapsibleButton = ctk.ctkCollapsibleButton()
        self.sampleCollapsibleButton.text = "A collapsible button"
        self.layout.addWidget(self.sampleCollapsibleButton)

        # Layout within the sample collapsible button
        self.sampleFormLayout = qt.QFormLayout(self.sampleCollapsibleButton)

        # HelloWorld button
        helloWorldButton = qt.QPushButton("Remove Undercuts")
        helloWorldButton.toolTip = "Print 'Hello world' in standard output."
        self.sampleFormLayout.addWidget(helloWorldButton)
        helloWorldButton.connect('clicked(bool)', self.onHelloWorldButtonClicked)
    
        # Add vertical spacer
        self.layout.addStretch(1)

        #Input Model
        # the volume selectors
        self.inputFrame = qt.QFrame(self.sampleCollapsibleButton)
        self.inputFrame.setLayout(qt.QHBoxLayout())
        self.sampleFormLayout.addWidget(self.inputFrame)
        self.inputSelector = qt.QLabel("Input Model: ", self.inputFrame)
        self.inputFrame.layout().addWidget(self.inputSelector)
        self.inputSelector = slicer.qMRMLNodeComboBox(self.inputFrame)
        self.inputSelector.nodeTypes = ( ("vtkMRMLModelNode"), "" )
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False
        self.inputSelector.setMRMLScene( slicer.mrmlScene )
        self.inputFrame.layout().addWidget(self.inputSelector) 
        
        # Set local var as instance attribute
        self.helloWorldButton = helloWorldButton

        #TODO, model selector
        #TODO, slice Z thickness
        #TODO, slice X,Y thickness
        
    def onHelloWorldButtonClicked(self):
        
        scene = slicer.mrmlScene
        inputModel = self.inputSelector.currentNode() 
        
        bounds = [0,0,0,0,0,0]
        inputModel.GetBounds(bounds)
        
        print('Model Name is:')
        print(inputModel.GetName())
        
        X = bounds[1] - bounds[0]
        Y = bounds[3] - bounds[2]
        Z = bounds[5] - bounds[4]
        
        mid = (bounds[0] + X/2, bounds[2] + Y/2, bounds[4] + Z/2)
                
        X_thick = .1  #TODO resolution input
        Y_thick = .1  #TODO resolution input
        Z_thick = .1  #TODO resolution input 
        
        z_slices = int(math.ceil(Z/Z_thick))
        y_slices = int(math.ceil(Y/Y_thick))
        x_slices = int(math.ceil(X/X_thick))
        
        x_thick = X/x_slices
        y_thick = Y/y_slices
        z_thick = Z/z_slices
        
        print('number of slices')
        print((x_slices, y_slices, z_slices))
        print('midpoint')
        print(mid)
        #TODO Bounding box calculation
        imageSize=[x_slices, y_slices, z_slices]
        imageSpacing=[x_thick, y_thick, z_thick]
        
        voxelType=vtk.VTK_UNSIGNED_CHAR
        
        imageData=vtk.vtkImageData()
        imageData.SetDimensions(imageSize)
        imageData.AllocateScalars(voxelType, 1)
        thresholder=vtk.vtkImageThreshold()
        thresholder.SetInputData(imageData)
        thresholder.SetInValue(1)
        thresholder.SetOutValue(1)
        # Create volume node
        volumeNode=slicer.vtkMRMLScalarVolumeNode()
        volumeNode.SetSpacing(imageSpacing)
        volumeNode.SetImageDataConnection(thresholder.GetOutputPort())
        # Add volume to scene
        slicer.mrmlScene.AddNode(volumeNode)
        displayNode=slicer.vtkMRMLScalarVolumeDisplayNode()
        slicer.mrmlScene.AddNode(displayNode)
        colorNode = slicer.util.getNode('Grey')
        displayNode.SetAndObserveColorNodeID(colorNode.GetID())
        volumeNode.SetAndObserveDisplayNodeID(displayNode.GetID())
        volumeNode.CreateDefaultStorageNode()
        
        #Transform the Volume to Fit Around the Model
        transform = slicer.vtkMRMLLinearTransformNode()
        scene.AddNode(transform) 
        volumeNode.SetAndObserveTransformNodeID(transform.GetID())
        
        vTransform = vtk.vtkTransform()
        vTransform.Translate((-X/2 + mid[0], -Y/2 + mid[1], -Z/2 + mid[2]))
        transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
        
        
        #Create a segmentation Node
        segmentationNode = slicer.vtkMRMLSegmentationNode()
        slicer.mrmlScene.AddNode(segmentationNode)
        segmentationNode.CreateDefaultDisplayNodes()
        segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(volumeNode)
        
        #Add the model as a segmentation
        #sphereSource = vtk.vtkSphereSource()
        #sphereSource.SetRadius(10)
        #sphereSource.SetCenter(6,30,28)
        #sphereSource.Update()
        #segmentationNode.AddSegmentFromClosedSurfaceRepresentation(sphereSource.GetOutput(), "Test")
      
        segmentID = segmentationNode.GetSegmentation().GenerateUniqueSegmentID("Test")
        segmentationNode.AddSegmentFromClosedSurfaceRepresentation(inputModel.GetPolyData(), 
                                                                   segmentID)
        #TODO, Unique ID
        segmentationNode.SetMasterRepresentationToBinaryLabelmap()
        
        modelLabelMap = segmentationNode.GetBinaryLabelmapRepresentation(segmentID)  #TODO Unique ID
        
        segmentationNode.SetMasterRepresentationToBinaryLabelmap()
        
        
        shape = list(modelLabelMap.GetDimensions())
        shape.reverse() #why reverse?
        labelArray = vtk.util.numpy_support.vtk_to_numpy(modelLabelMap.GetPointData().GetScalars()).reshape(shape)
        
        for n in range(1,shape[0]-1):
            labelArray[n,:,:] = numpy.maximum(labelArray[n,:,:], labelArray[n-1,:,:])
            
        outputPolyData = vtk.vtkPolyData()
        slicer.vtkSlicerSegmentationsModuleLogic.GetSegmentClosedSurfaceRepresentation(segmentationNode, segmentID, outputPolyData)
        
        # Create model node
        model = slicer.vtkMRMLModelNode()
        model.SetScene(scene)
        model.SetName(scene.GenerateUniqueName("Model_Undercuts_Removed"))

        model.SetAndObservePolyData(outputPolyData)

        # Create display node
        modelDisplay = slicer.vtkMRMLModelDisplayNode()
        modelDisplay.SetColor(1,1,0) # yellow
        modelDisplay.SetBackfaceCulling(0)
        modelDisplay.SetScene(scene)
        scene.AddNode(modelDisplay)
        model.SetAndObserveDisplayNodeID(modelDisplay.GetID())

        # Add to scene
        scene.AddNode(model) 