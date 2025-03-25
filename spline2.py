from __future__ import print_function
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQGLViewer import *
from OpenGL.GL import *
from math import cos,sin,sqrt

def clamp(value, minval, maxval):
    return max(minval, min(value, maxval))

class myFrame(ManipulatedFrame):
    def __init__(self):
        ManipulatedFrame.__init__(self)
        self.start = None
        self._delta = QPointF(0, 0)
    def mousePressEvent(self, e, camera):
        if (e.button() == Qt.RightButton):
            self.start = e.localPos()
            ManipulatedFrame.mousePressEvent(self,e, camera)
    
    def mouseReleaseEvent(self, e, camera):
        if (e.button() == Qt.RightButton):
            self.end = e.localPos()
            self._delta = self.end - self.start
            ManipulatedFrame.mouseReleaseEvent(self,e, camera)

    def mouseMoveEvent(self, e, camera):
        if self.start == None: self.start = e.localPos()
        self.end = e.localPos()
        # self._delta = self.end - self.start
        ManipulatedFrame.mouseMoveEvent(self,e,camera)

    @property
    def delta(self):
        return self._delta

class active_point:
    def __init__(self, pt):
        self.mf = myFrame()
        self._x = pt[0]
        self._y = pt[1]
        self._z = pt[2]
    def draw(self):
        glPushMatrix()
        glMultMatrixd(self.mf.matrix())
        glBegin(GL_POINTS)
        if self.mf.grabsMouse():
            glColor3f(0.0, 0.0, 1.0)
            # self.setPosition(Vec(self._x + self.mf.delta.x(), self._y + self.mf.delta.y(), 0))
            self._x += self.mf.delta.x()
            self._y += self.mf.delta.y()
            self._z += 0
        else:
            glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()
    def setPosition(self,pos):
        self.mf.setPosition(pos)

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @property
    def z(self):
        return self._z

class BSpline:

    def __init__(self, reference_points, discrete_num = 10, closed = False):
        self.points = reference_points
        self.d_num = int(discrete_num)
        self.closed = closed
        self.active_mfs = []
        
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
    
    # def setPosition(self,pos):
    #     self.mf.setPosition(pos)
    
    def init(self):
        for p in self.points:
            ap = active_point(p)
            ap.setPosition(Vec(p[0], p[1], p[2]))
            self.active_mfs.append(ap)

    def draw_vertexes(self):
        glEnable(GL_PROGRAM_POINT_SIZE)
        glPointSize(10)
        for p in self.active_mfs:
            p.draw()
        glPushMatrix()
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0 , 0.0)
        for i in range(len(self.active_mfs)-1):
            glVertex3f(self.active_mfs[i].x, self.active_mfs[i].y, self.active_mfs[i].z)
            glVertex3f(self.active_mfs[i+1].x, self.active_mfs[i+1].y, self.active_mfs[i+1].z)
        if self.closed:
            glVertex3f(self.active_mfs[0].x, self.active_mfs[0].y, self.active_mfs[0].z)
            glVertex3f(self.active_mfs[-1].x, self.active_mfs[-1].y, self.active_mfs[-1].z)
        glEnd()
        glPopMatrix()

    def draw_spline_curve(self):
        if not self.closed:     
            segmentsCount = len(self.active_mfs) - 1
            glBegin(GL_LINE_STRIP)
        else:
            segmentsCount = len(self.active_mfs) #Сегмент между первой и последней вершиной
            glBegin(GL_LINE_LOOP)  
        glColor3f(1.0, 1.0, 0.0)
        for i in range(segmentsCount):
            self.draw_glvertex_for_one_segment_of_spline(i)
        glEnd()

    def draw_glvertex_for_one_segment_of_spline(self, segment_id):
        pNum = len(self.active_mfs)
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
            x =   self.coefs[i][0] * self.active_mfs[p0].x \
                + self.coefs[i][1] * self.active_mfs[p1].x \
                + self.coefs[i][2] * self.active_mfs[p2].x
            y =   self.coefs[i][0] * self.active_mfs[p0].y \
                + self.coefs[i][1] * self.active_mfs[p1].y \
                + self.coefs[i][2] * self.active_mfs[p2].y
            z =   self.coefs[i][0] * self.active_mfs[p0].z \
                + self.coefs[i][1] * self.active_mfs[p1].z \
                + self.coefs[i][2] * self.active_mfs[p2].z
 
            glVertex3f(x, y, z)

# Make spline
points = ((0,0,0),(0,3,0),(1,3,0),(1,1,0),(2,1,0),(3,2,0),(3,0,0))
spline =  BSpline(points, 10, True)

class Viewer(QGLViewer):

    def __init__(self,parent = None):
        QGLViewer.__init__(self,parent)
        self.setMouseTracking(True)
        # glEnable(GL_PROGRAM_POINT_SIZE)
        # glPointSize(10)
        # setMouseTracking(True)
        
    def draw(self):
        spline.draw_spline_curve()
        spline.draw_vertexes()
        # for ap in self.active_mfs:
        #     ap.draw()

    def init(self):
        spline.init()
    # def init(self):
    #     # glColor3f(0.0, 1.0 , 0.0)
    #     glEnable(GL_PROGRAM_POINT_SIZE)
    #     glPointSize(10)
    #     self.active_mfs = []
    #     for p in points:
    #         ap = active_point(p)
    #         ap.setPosition(Vec(p[0], p[1], p[2]))
    #         self.active_mfs.append(ap)

    # def init(self):
    #     self.setMouseTracking(True)

        # nbSpirals = len(points)
        # self.pts = []
        # for i in range(nbSpirals):
        #     s = self.pts[i]
        #     s.setPosition(self.pts[i])
        #     self.spiral.append(s)


    # def mousePressEvent(self, e):
    #     if (e.button() == Qt.RightButton) and (e.type() == 2):
    #         print("aboba")
    #     else:
    #         QGLViewer.mousePressEvent(self,e)
    
    # def mouseReleaseEvent(self, e):
    #     if (e.button() == Qt.RightButton) and (e.type() == 2):
    #         print("aboba")
    #     else:
    #         QGLViewer.mouseReleaseEvent(self,e)

    # def mouseMoveEvent(self, e):
    #     if (e.button() == Qt.RightButton) and (e.type() == 2):
    #         print("aboba")
    #     else:
    #         QGLViewer.mouseMoveEvent(self,e)
        
  
def main():
    qapp = QApplication([])
    viewer = Viewer()
    viewer.show()
    qapp.exec_()

if __name__ == '__main__':
    main()
