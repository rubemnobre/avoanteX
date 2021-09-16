# Developed by Rubem Bezerra (rubemjrx@gmail.com) for Avoante Aeromec Aerodesign (aeromec@ufc.br)
# x forward, y right, z down
import numpy as np
import scipy.integrate
import copy

class Aircraft:
    def __init__(self):
        return

class Airfoil:
    def __init__(self, name, path = None, ac = 0.25):
        self.name = name
        self.path = path
        self.ac = ac
    def __str__(self):
        return self.name

class Surface:
    # Sections is a list of tuples: ((leading edge coordinates x, y, z), chord, angle, airfoil), start from 0,0,0 if ysim
    def __init__(self, sections, y_symmetry = False, vertical = False):
        self.vertical = vertical
        if len(sections) >= 2:
            if y_symmetry:
                self.sections = []
                zero = sections[0]
                if zero[0][1] == 0:
                    sections.pop(0)
                for sec in sections[::-1]:
                    (x, y, z), c, i, a = copy.deepcopy(sec)
                    self.sections.append(((x, -y, z), c, i, a))
                self.sections.append(zero)
                for sec in sections:
                    (x, y, z), c, i, a = copy.deepcopy(sec)
                    self.sections.append(((x, y, z), c, i, a))
            else:
                self.sections = copy.deepcopy(sections)
        else:
            raise Exception("At least 2 sections are needed, got %d" % len(sections))

    def chord(self, sb):
        for i in range(len(self.sections[:-1])):
            if self.sections[i][0][1] <= sb and self.sections[i+1][0][1] >= sb:
                y1 = self.sections[i][0][1]
                y2 = self.sections[i+1][0][1]

                c1 = self.sections[i][1]
                c2 = self.sections[i+1][1]
                return c1 + (c2-c1)*(sb-y1)/(y2-y1)
                
        for i in range(len(self.sections[:-1])):
            if self.sections[i][0][2] <= sb and self.sections[i+1][0][2] >= sb:
                z1 = self.sections[i][0][2]
                z2 = self.sections[i+1][0][2]

                c1 = self.sections[i][1]
                c2 = self.sections[i+1][1]
                return c1 + (c2-c1)*(sb-z1)/(z2-z1)
        return 0
    
    def ca(self, sb):
        for i in range(len(self.sections[:-1])):
            if self.sections[i][0][1] <= sb and self.sections[i+1][0][1] >= sb:
                y1 = self.sections[i][0][1]
                y2 = self.sections[i+1][0][1]

                c1 = self.sections[i][1]
                c2 = self.sections[i+1][1]

                ac1 = self.sections[i][3].ac
                ac2 = self.sections[i+1][3].ac
                return (c1 + (c2-c1)*(sb-y1)/(y2-y1))*(ac1 + (ac2-ac1)*(sb-y1)/(y2-y1))
                
        for i in range(len(self.sections[:-1])):
            if self.sections[i][0][2] <= sb and self.sections[i+1][0][2] >= sb:
                z1 = self.sections[i][0][2]
                z2 = self.sections[i+1][0][2]

                c1 = self.sections[i][1]
                c2 = self.sections[i+1][1]

                ac1 = self.sections[i][3].ac
                ac2 = self.sections[i+1][3].ac
                return (c1 + (c2-c1)*(sb-z1)/(z2-z1))*(ac1 + (ac2-ac1)*(sb-z1)/(z2-z1))
        return 0
    
    def leading_edge(self, sb):
        x, y, z = 0, 0, 0
        for i in range(len(self.sections[:-1])):
            if self.sections[i][0][1] <= sb and self.sections[i+1][0][1] >= sb:
                x1 = self.sections[i][0][0]
                x2 = self.sections[i+1][0][0]

                y1 = self.sections[i][0][1]
                y2 = self.sections[i+1][0][1]
                
                z1 = self.sections[i][0][2]
                z2 = self.sections[i+1][0][2]
                x = x1 + (x2 - x1)*(sb - y1)/(y2 - y1)
                y = sb
                z = z1 + (z2 - z1)*(sb - y1)/(y2 - y1)
                return (x, y, z)
                
        for i in range(len(self.sections[:-1])):
            if self.sections[i][0][2] <= sb and self.sections[i+1][0][2] >= sb:
                x1 = self.sections[i][0][0]
                x2 = self.sections[i+1][0][0]
                
                y1 = self.sections[i][0][1]
                y2 = self.sections[i+1][0][1]

                z1 = self.sections[i][0][2]
                z2 = self.sections[i+1][0][2]
                x = x1 + (x2 - x1)*(sb - z1)/(z2 - z1)
                y = y1 + (y2 - y1)*(sb - z1)/(z2 - z1)
                z = sb
                return (x, y, z)

    def analyze_geometry(self):
        if self.vertical:
            self.b = abs(self.sections[0][0][2] - self.sections[-1][0][2])
        else:
            self.b = abs(self.sections[0][0][1] - self.sections[-1][0][1])
        self.c = scipy.integrate.quad(lambda y : self.chord(y)**2, -self.b/2, self.b/2)[0]/scipy.integrate.quad(self.chord, -self.b/2, self.b/2)[0]
        self.S = scipy.integrate.quad(self.chord, -self.b/2, self.b/2)[0]
        self.AR = self.b*self.b/self.S
        cma_x = lambda sb : self.leading_edge(sb)[0] + self.ca(sb)
        cma_y = lambda sb : self.leading_edge(sb)[1]
        cma_z = lambda sb : self.leading_edge(sb)[2]
        xac = scipy.integrate.quad(cma_x, -self.b/2, self.b/2)[0]/self.b
        yac = scipy.integrate.quad(cma_y, -self.b/2, self.b/2)[0]/self.b
        zac = scipy.integrate.quad(cma_z, -self.b/2, self.b/2)[0]/self.b
        self.AC = (xac, yac, zac)
