from __future__ import print_function
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQGLViewer import *
from OpenGL.GL import *
from math import cos,sin,sqrt

def clamp(value, minval, maxval):
    return max(minval, min(value, maxval))

class BSpline:

    def __init__(self, reference_points, discrete_num = 10, closed = False):
        self.points = reference_points
        self.d_num = int(discrete_num)
        self.closed = closed
        
        # Генерация коэффициентов для сгенеренных вершин B-сплайна 3 порядка
        self.coefs = []
        for i in range(self.d_num):
            spline_segm_coef = self.calc_spline2_coef(i/self.d_num)
            self.coefs.append(spline_segm_coef)

    def calc_spline2_coef(self, t):
        coefs = [0,0,0]
        coefs[0] = (1.0-t)*(1.0-t)/2.0
        coefs[1] = (- 2.0*t*t + 2*t + 1)/2.0
        coefs[2] = t*t/2.0
        return coefs

    def draw_vertexes(self):
        glEnable(GL_PROGRAM_POINT_SIZE)
        glPointSize(10)
        glEnableClientState(GL_VERTEX_ARRAY)
        glColor3f(0.0, 1.0, 0.0)
        glVertexPointer(3, GL_FLOAT, 0, self.points)
        glDrawArrays(GL_POINTS, 0, len(self.points))
        glColor3f(1.0, 0.0, 0.0)
        if not self.closed:
            glVertexPointer(3, GL_FLOAT, 0, [[self.points[i], self.points[i+1]] for i in range(len(self.points)-1)])
            glDrawArrays(GL_LINES, 0, 2*len(self.points)-2)
        else:
            l = len(self.points)
            glVertexPointer(3, GL_FLOAT, 0, [[self.points[i], self.points[(i+1) % l]] for i in range(l)])
            glDrawArrays(GL_LINES, 0, 2*len(self.points))
        glDisableClientState(GL_VERTEX_ARRAY)

    def draw_spline_curve(self):
        if not self.closed:     
            segmentsCount = len(self.points) - 1
            glBegin(GL_LINE_STRIP)
        else:
            segmentsCount = len(self.points) #Сегмент между первой и последней вершиной
            glBegin(GL_LINE_LOOP)  
        glColor3f(1.0, 1.0, 0.0)
        for i in range(segmentsCount):
            self.draw_glvertex_for_one_segment_of_spline(i)
        glEnd()

    def draw_glvertex_for_one_segment_of_spline(self, segment_id):
        pNum = len(self.points)
        # Вычисление номеров вершин в списке вершин для построения сплайна
        if not self.closed:
            p0 = clamp(segment_id - 1, 0, pNum - 1)
            p1 = clamp(segment_id, 0, pNum - 1)
            p2 = clamp(segment_id + 1, 0, pNum - 1)
        else:
            p0 = (segment_id - 1 + pNum) % pNum
            p1 = (segment_id + pNum) % pNum
            p2 = (segment_id + 1 + pNum) % pNum
        # По заранее вычисленным коэффициентам 
        # вычисляем промежуточные точки сплайна
        # и выводим их в OpenGL
        for i in range(self.d_num):
            x =   self.coefs[i][0] * self.points[p0][0] \
                + self.coefs[i][1] * self.points[p1][0] \
                + self.coefs[i][2] * self.points[p2][0]
            y =   self.coefs[i][0] * self.points[p0][1] \
                + self.coefs[i][1] * self.points[p1][1] \
                + self.coefs[i][2] * self.points[p2][1]
            z =   self.coefs[i][0] * self.points[p0][2] \
                + self.coefs[i][1] * self.points[p1][2] \
                + self.coefs[i][2] * self.points[p2][2]
 
            glVertex3f(x, y, z)

# Make spline
points = ((0,0,0),(0,3,0),(1,3,0),(1,1,0),(2,1,0),(3,2,0),(3,0,0))
spline =  BSpline(points, 10, True)

class Viewer(QGLViewer):

    def __init__(self,parent = None):
        QGLViewer.__init__(self,parent)
        
    def draw(self):
        spline.draw_spline_curve()
        spline.draw_vertexes()
        
  
def main():
    qapp = QApplication([])
    viewer = Viewer()
    viewer.show()
    qapp.exec_()

if __name__ == '__main__':
    main()