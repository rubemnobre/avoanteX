# Developed by Rubem Bezerra (rubemjrx@gmail.com) for Avoante Aeromec Aerodesign (aeromec@ufc.br)
# x forward, y right, z down
import numpy as np
import scipy.integrate
import copy

class Aircraft:
    def __init__(self):
        return

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

    def chord(self, y):
        if not self.vertical:
            for i in range(len(self.sections[:-1])):
                if self.sections[i][0][1] <= y and self.sections[i+1][0][1] >= y:
                    y1 = self.sections[i][0][1]
                    y2 = self.sections[i+1][0][1]

                    c1 = self.sections[i][1]
                    c2 = self.sections[i+1][1]
                    return c1 + (c2-c1)*(y-y1)/(y2-y1)
        else:
            for i in range(len(self.sections[:-1])):
                if self.sections[i][0][2] <= y and self.sections[i+1][0][2] >= y:
                    y1 = self.sections[i][0][2]
                    y2 = self.sections[i+1][0][2]

                    c1 = self.sections[i][1]
                    c2 = self.sections[i+1][1]
                    return c1 + (c2-c1)*(y-y1)/(y2-y1)
        return 0

    def analyze_geometry(self):
        self.b = abs(self.sections[0][0][1] - self.sections[-1][0][1])
        self.c = scipy.integrate.quad(lambda y : self.chord(y)**2, -self.b/2, self.b/2)[0]/scipy.integrate.quad(self.chord, -self.b/2, self.b/2)[0]
        self.S = scipy.integrate.quad(self.chord, -self.b/2, self.b/2)[0]
        self.AR = self.b*self.b/self.S
        if self.vertical:
            self.AC = ()