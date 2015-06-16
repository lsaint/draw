#!/usr/bin/env python

# These are only needed for Python v2 but are harmless for Python v3.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

#from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QWidget, QImage, qRgb, QPainter, QPen, QPrintDialog, QDialog, QMainWindow, QFileDialog, QColorDialog, QInputDialog, QMessageBox, QAction, QImageWriter, QMenu, QApplication
from PyQt4.QtCore import Qt, QPoint, QSize, QRect, QDir


class YYOpenPlatformPaintArea(QWidget):
    def __init__(self, parent=None):
        super(YYOpenPlatformPaintArea, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.modified = False
        self.scribbling = False
        self.myPenWidth = 1
        self.myPenColor = Qt.blue
        self.image = QImage()
        self.lastPoint = QPoint()

    #def openImage(self, fileName):
    #    loadedImage = QImage()
    #    if not loadedImage.load(fileName):
    #        return False

    #    newSize = loadedImage.size().expandedTo(self.size())
    #    self.resizeImage(loadedImage, newSize)
    #    self.image = loadedImage
    #    self.modified = False
    #    self.update()
    #    return True

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size())

        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        self.image.fill(qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            self.scribbling = False

    def paintEvent(self, event):
        painter = QPainter(self)
        #painter.drawImage(event.rect(), self.image)
        painter.drawImage(self.image.rect(), self.image)

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resizeImage(self.image, QSize(newWidth, newHeight))
            self.update()

        super(YYOpenPlatformPaintArea, self).resizeEvent(event)

    def drawLineTo(self, endPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.myPenColor, self.myPenWidth,
                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QPoint(endPoint)

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return
    
        newImage = QImage(newSize, QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), image)
        self.image = newImage

    def print_(self):
        printer = QPrinter(QPrinter.HighResolution)

        printDialog = QPrintDialog(printer, self)
        if printDialog.exec_() == QDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)
            painter.end()

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.saveAsActs = []

        self.YYOpenPlatformPaintArea = YYOpenPlatformPaintArea()
        self.setCentralWidget(self.YYOpenPlatformPaintArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("YY OpenPlatform Paint")
        #self.resize(800, 600)
        self.setFixedSize(800,600)
        
    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    #def open(self):
    #    if self.maybeSave():
    #        fileName = QFileDialog.getOpenFileName(self, "Open File",
    #                QDir.currentPath())
    #        if fileName:
    #            self.YYOpenPlatformPaintArea.openImage(fileName)

    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.saveFile(fileFormat)

    def penColor(self):
        newColor = QColorDialog.getColor(self.YYOpenPlatformPaintArea.penColor())
        if newColor.isValid():
            self.YYOpenPlatformPaintArea.setPenColor(newColor)

    def penWidth(self):
        newWidth, ok = QInputDialog.getInteger(self, "YYOpenPlatformPaint",
                "Select pen width:", self.YYOpenPlatformPaintArea.penWidth(), 1, 50, 1)
        if ok:
            self.YYOpenPlatformPaintArea.setPenWidth(newWidth)

    def about(self):
        QMessageBox.about(self, "About YYOpenPlatformPaint",
                "<p>The <b>YYOpenPlatformPaint</b> is designed and developed by YY OpenPlatform App Team</p>")

    def createActions(self):
        #self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
        #        triggered=self.open)

        for format in QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)

        self.printAct = QAction("&Print...", self,
                triggered=self.YYOpenPlatformPaintArea.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.penColorAct = QAction("&Pen Color...", self,
                triggered=self.penColor)

        self.penWidthAct = QAction("Pen &Width...", self,
                triggered=self.penWidth)

        self.clearScreenAct = QAction("&Clear Screen", self,
                shortcut="Ctrl+L", triggered=self.YYOpenPlatformPaintArea.clearImage)

        self.aboutAct = QAction("&About", self, triggered=self.about)

    def createMenus(self):
        self.saveAsMenu = QMenu("&Save As", self)
        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        fileMenu = QMenu("&File", self)
        #fileMenu.addAction(self.openAct)
        fileMenu.addMenu(self.saveAsMenu)
        fileMenu.addAction(self.printAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addSeparator()
        optionMenu.addAction(self.clearScreenAct)

        helpMenu = QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(helpMenu)

    def maybeSave(self):
        if self.YYOpenPlatformPaintArea.isModified():
            ret = QMessageBox.warning(self, "YYOpenPlatformPaint",
                        "The image has been modified.\n"
                        "Do you want to save your changes?",
                        QMessageBox.Save | QMessageBox.Discard |
                        QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QMessageBox.Cancel:
                return False

        return True

    def saveFile(self, fileFormat):
        initialPath = QDir.currentPath() + '/untitled.' + fileFormat

        fileName = QFileDialog.getSaveFileName(self, "Save As",
                initialPath,
                "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.YYOpenPlatformPaintArea.saveImage(fileName, fileFormat)

        return False


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
