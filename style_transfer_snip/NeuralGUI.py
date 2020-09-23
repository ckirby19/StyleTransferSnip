import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QPixmap, QImage
from imutils import paths
import SnippingTool
import cv2
import imutils
from imutils import paths
import numpy as np
import pathlib

class GUI(QMainWindow):

    def __init__(self):
        super().__init__()
        #Setting up the snipping tool
        self.original_image = None
        self.filtered_image = None
        self.original_pixmap = None
        self.filtered_pixmap = None
        self.snippingTool = SnippingTool.SnippingWidget()

        #Preparing the layout for the images
        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.canvas = QGroupBox(self)
        self.left = QLabel(self)
        self.right = QLabel(self)
        layout = QHBoxLayout(self.canvas)
        layout.addWidget(self.left)
        layout.addWidget(self.right)
        wid.setLayout(layout)

        # Box initial setup
        self.resize(400,220)
        self.center()
        QToolTip.setFont(QFont('SansSerif', 10))

        # For Neural Transfer Image
        modelPaths = paths.list_files("models", validExts=(".t7",))
        modelPaths = sorted(list(modelPaths))
        models = list(zip(range(0, len(modelPaths)), (modelPaths)))
        self.filter = models[0][1]
        
        # Exit
        exit_window = QAction('&Exit', self) #The &... allows one to press ctrl + first letter of the string to do that action (e.g &exit = ctrl + e) 
        exit_window.setShortcut('Ctrl+Q')
        exit_window.setStatusTip('Exit application')
        exit_window.triggered.connect(self.closeApp)

        # New Snip
        new_snip_action = QAction('New', self)
        new_snip_action.setShortcut('Ctrl+N')
        new_snip_action.setStatusTip('Snip!')
        new_snip_action.triggered.connect(self.snipEvent)

        # Save
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save')
        save_action.triggered.connect(self.saveFile)

        # Select Filter
        filters = QComboBox(self)
        for model in models:
            (modelID,modelPath) = model
            filters.addItem(modelPath)
        filters.activated[str].connect(self.filterSelect)

        # Create the toolbar for user interaction
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(new_snip_action)
        self.toolbar.addAction(save_action)
        self.toolbar.addAction(exit_window)
        self.toolbar.addWidget(filters)

        #Other stuff
        self.statusBar()
        self.snippingTool.capture_signal.connect(self.snipCollected)
        self.directory = pathlib.Path().absolute()

        self.show() 

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()) 

    def closeApp(self):
        reply = QMessageBox.question(self, 'Message',"Are you sure to quit?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit()
        else:
            pass
    
    def closeEvent(self,QCloseEvent): #For the windows exit button
        QCloseEvent.ignore()
        self.closeApp()

    def filterSelect(self,f):
        self.filter = f
        if self.original_image is not None:
            self.neural_transfer()
        
    def snipEvent(self):
        self.original_image = None
        self.filtered_image = None
        self.showMinimized()
        self.snippingTool.start()

    def snipCollected(self,data):
        self.showNormal()
        self.original_image = data
        self.setLeft()
        self.neural_transfer()
    
    def setRight(self):
        height, width, channel = self.filtered_image.shape
        bytesPerLine = 3 * width
        qImg = QImage(self.filtered_image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        self.filtered_pixmap = QPixmap(qImg)
        self.right.setPixmap(self.filtered_pixmap)
        QApplication.processEvents()
    
    def setLeft(self):
        height, width, channel = self.original_image.shape
        bytesPerLine = 3 * width
        qImg = QImage(self.original_image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        self.original_pixmap = QPixmap(qImg)
        self.left.setPixmap(self.original_pixmap)
        QApplication.processEvents()

    def saveFile(self):
        if self.filtered_pixmap is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Please create an image to save")
            msg.exec()
        else:
            file_path, name = QFileDialog.getSaveFileName(self, "Save file", str(self.directory), "Image Files (*.jpg *jpeg *.png)")
            if file_path:
                self.filtered_pixmap.save(file_path)
    
    def neural_transfer(self):
        """
        Image img is numpy array 
        """

        net = cv2.dnn.readNetFromTorch(self.filter)

        # resize the frame to have a width of 600 pixels (while
        # maintaining the aspect ratio), and then grab the image
        # dimensions
        original_width = self.original_image.shape[1]
        frame = imutils.resize(self.original_image, width=600)
        (h, w) = frame.shape[:2]

        # construct a blob from the frame, set the input, and then perform a
        # forward pass of the network
        # blob is used to preprocess the image. Mean subtraction and scaling
        blob = cv2.dnn.blobFromImage(frame, 1.0, (w, h),(103.939, 116.779, 123.680), swapRB=False, crop=False)
        net.setInput(blob)
        output = net.forward()

        # reshape the output tensor, add back in the mean subtraction, and
        # then swap the channel ordering
        output = output.reshape((3, output.shape[2], output.shape[3]))
        output[0] += 103.939
        output[1] += 116.779
        output[2] += 123.680
        output /= 255.0
        output = output.transpose(1, 2, 0).copy() #.copy() needed so a memoryview is not created
        output = imutils.resize(output,original_width)
        #Since we are dealing with unsigned ints, a single shift means a possible underflow/overflow, and this can corrupt the whole image, so a conversion is needed
        output = cv2.convertScaleAbs(output, alpha=(255.0)) #https://docs.opencv.org/2.4/modules/core/doc/operations_on_arrays.html?highlight=convertscale#convertscaleabs
        
        self.filtered_image = output
        self.setRight()

def main():
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())
