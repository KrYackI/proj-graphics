from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import *
from PyQGLViewer import *
from OpenGL.GL import *
import random
import os
from typing import Final
from math import *
import argparse

# def gen_sqr(color, i):
N_FACTOR: int
DIRNAME: Final = os.path.join('.', 'vertexBuffers')

def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--n_factor',
                        help='n_factor definition',
                        type=int,
                        default=5,
                        dest='n_factor')
    
    return parser.parse_args()

class Viewer(QGLViewer):
    def __init__(self,parent = None):
        QGLViewer.__init__(self,parent)
        self.__wireframe = False
        self.__clr = False
        self.__draw_type = 0

    def __draw_grad_triangle(self):
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0 , 0.0)
        glVertex3f(-0.7, 0.0, 0.0)
        glColor3f(0.0, 1.0 , 0.0)
        glVertex3f(0.7, 0.0, 0.0)
        glColor3f(0.0, 0.0 , 1.0)
        glVertex3f(0.0, 1.0, 0.0)
        glEnd()

    def __clear(self):
        glClear(GL_COLOR_BUFFER_BIT)       
    
    def __gen_model(self) -> list[float]:
        vertexArray = list()
        filename: str
        if self.__draw_type == 1:
            filename = os.path.join(DIRNAME, "sqr_vert.txt")
        elif self.__draw_type == 2:
            filename = os.path.join(DIRNAME, "in_sqr_vert.txt")
        elif self.__draw_type == 3:
            filename = os.path.join(DIRNAME, "circle_vert.txt")
        elif self.__draw_type == 4:
            filename = os.path.join(DIRNAME, "sphere_vert.txt")

        if os.path.exists(filename):
            vertexArray = self.__read_model(filename)
            if len(vertexArray) == N_FACTOR**3:
                return vertexArray
            else:
                vertexArray.clear()
        with open(filename, "w") as file:
            if self.__draw_type == 1:
                for i in range(N_FACTOR):
                    for j in range(N_FACTOR):
                        for k in range(N_FACTOR):
                            x = float(i) / (N_FACTOR - 1) - 0.5
                            y = float(j) / (N_FACTOR - 1) - 0.5
                            z = float(k) / (N_FACTOR - 1) - 0.5
                            vertexArray.append([x, y, z])
                            file.write(str(x) + ' ' + str(y) + ' ' + str(z) + '\n')
            elif self.__draw_type == 2:
                for i in range(N_FACTOR**3):
                    x, y, z = random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)
                    vertexArray.append([x, y, z])
                    file.write(str(x) + ' ' + str(y) + ' ' + str(z) + '\n')
            elif self.__draw_type == 3:
                for i in range(N_FACTOR**3):
                    x = random.uniform(-0.5, 0.5)
                    y = random.uniform(-sqrt(0.25 - x**2), sqrt(0.25 - x**2))
                    z = random.uniform(-sqrt(0.25 - x**2 - y**2), sqrt(0.25 - x**2 - y**2))
                    vertexArray.append([x, y, z])
                    file.write(str(x) + ' ' + str(y) + ' ' + str(z) + '\n')
            elif self.__draw_type == 4:
                for i in range(N_FACTOR**3):
                    x_exp = random.uniform(-0.5, 0.5)
                    y_exp = random.uniform(-sqrt(0.25 - x_exp**2), sqrt(0.25 - x_exp**2))
                    z_exp = sqrt(0.25 - x_exp**2 - y_exp**2) * (random.randint(0, 1) * 2 - 1)
                    x = random.gauss(x_exp, random.uniform(0, 0.1) - 0.05)
                    y = random.gauss(y_exp, random.uniform(0, 0.1) - 0.05)
                    z = random.gauss(z_exp, random.uniform(0, 0.1) - 0.05)
                    vertexArray.append([x, y, z])
                    file.write(str(x) + ' ' + str(y) + ' ' + str(z) + '\n')
        return vertexArray

    def __read_model(self, filename: str) -> list[float]:
        with open(filename, "r") as file:
            return [[float(y) for y in x.split()] for x in file.readlines()]


    def draw(self):
        if self.__clr:
            self.__clear()
        else:
            glEnable(GL_PROGRAM_POINT_SIZE)
            glPointSize(10)
            if self.__wireframe:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            if self.__draw_type == 0: self.__draw_grad_triangle()
            else:
                vertexes = self.__gen_model()
                glColor3f(0.0, 1.0, 0.0)
                glEnableClientState(GL_VERTEX_ARRAY)
                glVertexPointer(3, GL_FLOAT, 0, vertexes)
                glDrawArrays(GL_POINTS, 0, N_FACTOR**3)
                glDisableClientState(GL_VERTEX_ARRAY)

    def keyPressEvent(self,e):
        if e.nativeVirtualKey()==Qt.Key_W:
            self.__wireframe = not self.__wireframe
            self.update()
        if e.nativeVirtualKey()==Qt.Key_X:
            self.__clr = not self.__clr
            self.update()
        if e.nativeVirtualKey()==Qt.Key_R:
            self.__draw_type = (self.__draw_type + 1) % 5
            self.update()
        else:
            QGLViewer.keyPressEvent(self, e)



def main():
    n = parse_cli_args().n_factor
    global N_FACTOR
    N_FACTOR = n if n >=0 else -n
    if not os.path.exists(DIRNAME):
        os.mkdir(DIRNAME)
    qapp = QApplication([])
    viewer = Viewer()
    viewer.show()
    qapp.exec_()
    for file in os.listdir(DIRNAME):
        os.remove(os.path.join(DIRNAME, file))

if __name__ == '__main__':
    main()
