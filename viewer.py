from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import *
from PyQGLViewer import *
from OpenGL.GL import *

class Viewer(QGLViewer):
    def __init__(self,parent = None):
        QGLViewer.__init__(self,parent)
        self.__wireframe = False

    def __draw_grad_triangle(self):
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0 , 0.0)
        glVertex3f(-0.7, 0.0, 0.0)
        glColor3f(0.0, 1.0 , 0.0)
        glVertex3f(0.7, 0.0, 0.0)
        glColor3f(0.0, 0.0 , 1.0)
        glVertex3f(0.0, 1.0, 0.0)
        glEnd()

    def draw(self):
        if self.__wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        self.__draw_grad_triangle()

    def keyPressEvent(self,e):
        modifiers = e.modifiers()
        if e.nativeVirtualKey()==Qt.Key_W:
            self.__wireframe = not self.__wireframe
            handled = True
            self.update()
        else:
            QGLViewer.keyPressEvent(self, e)
        # self.update()



def main():
    qapp = QApplication([])
    viewer = Viewer()
    viewer.show()
    qapp.exec_()

if __name__ == '__main__':
    main()
