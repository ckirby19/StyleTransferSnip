import tkinter as tk
import numpy as np
import cv2
from PIL import ImageGrab, Image
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
import screeninfo
from ctypes import windll, c_int, c_uint, c_char_p, c_buffer
from struct import calcsize, pack

class SnippingWidget(QtWidgets.QWidget):
    is_snipping = False
    capture_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.output = None

        root = tk.Tk()
        screen_width = 0
        for monitor in screeninfo.get_monitors():
            screen_width += monitor.width
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

    def start(self):
        self.output = None
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        SnippingWidget.is_snipping = True
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.show()

    def paintEvent(self, event):
        if SnippingWidget.is_snipping:
            brush_color = (128, 128, 255, 100)
            lw = 3
            opacity = 0.3
        else:
            # reset points, so the rectangle won't show up again.
            self.begin = QtCore.QPoint()
            self.end = QtCore.QPoint()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0

        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), lw))
        qp.setBrush(QtGui.QColor(*brush_color))
        rect = QtCore.QRectF(self.begin, self.end)
        qp.drawRect(rect)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            print('Quit')
            self.close()
        event.accept()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    @QtCore.pyqtSlot()
    def mouseReleaseEvent(self, event):
        """
        Emits signal of captured image when mouse is released. Signalled output image is numpy array
        """
        SnippingWidget.is_snipping = False
        QtWidgets.QApplication.restoreOverrideCursor()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        self.repaint() #needed so blue box thing does not appear on the actual snip
        QtWidgets.QApplication.processEvents()
        img = self.grab_screen(bbox=(x1,y1,x2,y2))
        img = np.array(img)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB) #Required to change colour output so image is displayed normally
        QtWidgets.QApplication.processEvents()
        self.capture_signal.emit(img)
        


    def grab_screen(self,bbox=None):
        """
        Grabs a screenshot. This is a replacement for PIL's ImageGrag.grab() method
        that supports multiple monitors. (SEE: https://github.com/python-pillow/Pillow/issues/1547)

        Returns a PIL Image, so PIL library must be installed.

        Usage:
            im = grab_screen() # grabs a screenshot of the primary monitor
            im = grab_screen([-1600, 0, -1, 1199]) # grabs a 1600 x 1200 screenshot to the left of the primary monitor
            im.save('screencap.jpg')
        """
        gdi32 = windll.gdi32

        # Win32 functions
        CreateDC = gdi32.CreateDCA
        CreateCompatibleDC = gdi32.CreateCompatibleDC
        GetDeviceCaps = gdi32.GetDeviceCaps
        CreateCompatibleBitmap = gdi32.CreateCompatibleBitmap
        BitBlt = gdi32.BitBlt
        SelectObject = gdi32.SelectObject
        GetDIBits = gdi32.GetDIBits
        DeleteDC = gdi32.DeleteDC
        DeleteObject = gdi32.DeleteObject

        # Win32 constants
        NULL = 0
        HORZRES = 8
        VERTRES = 10
        SRCCOPY = 13369376
        HGDI_ERROR = 4294967295
        ERROR_INVALID_PARAMETER = 87
        try:
            screen = CreateDC(c_char_p(b'DISPLAY'), NULL, NULL, NULL)
            
            screen_copy = CreateCompatibleDC(screen)
            
            if bbox:
                left,top,x2,y2 = bbox
                width = x2 - left + 1
                height = y2 - top + 1
            else:
                left = 0
                top = 0
                width = GetDeviceCaps(screen, HORZRES)
                height = GetDeviceCaps(screen, VERTRES)
            bitmap = CreateCompatibleBitmap(screen, width, height)
            
            if bitmap == NULL:
                print('grab_screen: Error calling CreateCompatibleBitmap. Returned NULL')
                return

            hobj = SelectObject(screen_copy, bitmap)
            
            if hobj == NULL or hobj == HGDI_ERROR:
                print('grab_screen: Error calling SelectObject. Returned {0}.'.format(hobj))
                return
            if BitBlt(screen_copy, 0, 0, width, height, screen, left, top, SRCCOPY) == NULL:
                print('grab_screen: Error calling BitBlt. Returned NULL.')
                return
            
            bitmap_header = pack('LHHHH', calcsize('LHHHH'), width, height, 1, 24)
            bitmap_buffer = c_buffer(bitmap_header)
            shifted_width = width*3+3
            bitmap_bits = c_buffer(b' ' * (height * (shifted_width & -4))) #Binary AND Operator that copies a bit to the result if it exists in both operands.
            got_bits = GetDIBits(screen_copy, bitmap, 0, height, bitmap_bits, bitmap_buffer, 0)
            
            if got_bits == NULL or got_bits == ERROR_INVALID_PARAMETER:
                print('grab_screen: Error calling GetDIBits. Returned {0}.'.format(got_bits))
                return

            image = Image.frombuffer('RGB', (width, height), bitmap_bits, 'raw', 'BGR', (width * 3 + 3) & -4, -1)
            DeleteObject(bitmap)
            DeleteDC(screen_copy)
            DeleteDC(screen)
            return image

        except Exception as e:
            return e