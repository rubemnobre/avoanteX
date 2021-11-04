# Developed by Rubem Bezerra (rubemjrx@gmail.com) for Avoante Aeromec Aerodesign (aeromec@ufc.br)
# x forward, y right, z down

import numpy as np
import scipy.integrate

class Coefficients:
    def __init__(self):
        self.CL = lambda a, b : 0
        self.CY = lambda a, b : 0
        self.CD = lambda a, b : 0

        self.Cm = lambda a, b : 0
        self.Cn = lambda a, b : 0
        self.Cl = lambda a, b : 0
        

class Aircraft:
    @classmethod
    def from_params(cls, params):
        new = cls('')
        return new
    
    def __init__(self, name):
        self.name = name
        self.surfaces = []
        self.ref_S = 1
        self.ref_c = 1
        self.ref_b = 1
        self.mass = 0
        self.CG = np.array([0, 0, 0])

    def add_surface(self, surface, name, position, angle, group = 0, make_ref = False):
        self.surfaces.append((surface, name, position, angle, group))
        self.CG = (surface.mass*surface.CG + self.mass*self.CG)/(self.mass + surface.mass)
        if make_ref:
            self.ref_S = surface.S
            self.ref_c = surface.c
            self.ref_b = surface.b

    def avl_text(self, ge_height = None):
        avl_coord = lambda v : (-v[0], v[1], -v[2]) # Attention to the fact that AVL uses x downstream (back), z up
        text = "1\n"
        text += "0.0\n"
        if ge_height == None:
            text += "0 0 0.0\n"
        else:
            text += "0 1 %.3f\n" % -ge_height
        text += "%.3f %.3f %.3f\n" % (self.ref_S, self.ref_c, self.ref_b)
        text += "%.3f %.3f %.3f\n" % avl_coord(self.CG)
        for s in self.surfaces:
            text += s[0].avl_text(s[1], s[2], s[3], s[4])
        text += "\nend\n"
        return text


class Airfoil:
    def __init__(self, name: str, path = None, ac = 0.25, ach = 0):
        self.name = name
        self.path = path
        self.ac = ac
        self.ach = ach
    def __str__(self):
        return self.name

class Section:
    def __init__(self, pos, chord, ainc, airfoil : Airfoil):
        self.pos = np.array(pos)
        self.chord = chord
        self.ainc = ainc
        self.airfoil = airfoil
    def symmetric(self):
        pos = np.array([self.pos[0], -self.pos[1], self.pos[2]])
        return Section(pos, self.chord, self.ainc, self.airfoil)

class Surface:
    # Sections is a list of tuples: ((leading edge coordinates x, y, z), chord, angle, airfoil), start from 0,0,0 if ysim
    def __init__(self, sections, discretization = "10 1.0 15 -1.0",y_symmetry = False, vertical = False):
        self.vertical = vertical
        self.discretization = discretization
        self.controls = []
        self.mass = 1
        self.CG = [0, 0, 0]
        self.coefficients = None
        self.ydup = y_symmetry
        self.original_sections = sections.copy()
        if len(sections) >= 2:
            if y_symmetry:
                self.sections = []
                zero = sections[0]
                if zero.pos[1] == 0:
                    sections.pop(0)
                for sec in sections[::-1]:
                    self.sections.append(sec.symmetric())
                self.sections.append(zero)
                self.sections.extend(sections)
            else:
                self.sections = sections
        else:
            raise Exception("At least 2 sections are needed, got %d" % len(sections))
        self.analyze_geometry()

    def chord(self, sb):
        for i in range(len(self.sections[:-1])):
            if self.sections[i].pos[1] <= sb and self.sections[i+1].pos[1] >= sb:
                y1 = self.sections[i].pos[1]
                y2 = self.sections[i+1].pos[1]

                c1 = self.sections[i].chord
                c2 = self.sections[i+1].chord
                return c1 + (c2-c1)*(sb-y1)/(y2-y1)
                
        for i in range(len(self.sections[:-1])):
            if self.sections[i].pos[2] <= sb and self.sections[i+1].pos[2] >= sb:
                z1 = self.sections[i].pos[2]
                z2 = self.sections[i+1].pos[2]

                c1 = self.sections[i].chord
                c2 = self.sections[i+1].chord
                return c1 + (c2-c1)*(sb-z1)/(z2-z1)
        return 0
    
    def ca(self, sb):
        for i in range(len(self.sections[:-1])):
            if self.sections[i].pos[1] <= sb and self.sections[i+1].pos[1] >= sb:
                y1 = self.sections[i].pos[1]
                y2 = self.sections[i+1].pos[1]

                c1 = self.sections[i].chord
                c2 = self.sections[i+1].chord

                ac1 = self.sections[i].airfoil.ac
                ac2 = self.sections[i+1].airfoil.ac
                return (c1 + (c2-c1)*(sb-y1)/(y2-y1))*(ac1 + (ac2-ac1)*(sb-y1)/(y2-y1))
                
        for i in range(len(self.sections[:-1])):
            if self.sections[i].pos[2] <= sb and self.sections[i+1].pos[2] >= sb:
                z1 = self.sections[i].pos[2]
                z2 = self.sections[i+1].pos[2]

                c1 = self.sections[i].chord
                c2 = self.sections[i+1].chord

                ac1 = self.sections[i].airfoil.ac
                ac2 = self.sections[i+1].airfoil.ac
                return (c1 + (c2-c1)*(sb-z1)/(z2-z1))*(ac1 + (ac2-ac1)*(sb-z1)/(z2-z1))
        return 0
    
    def leading_edge(self, sb):
        x, y, z = 0, 0, 0
        for i in range(len(self.sections[:-1])):
            if self.sections[i].pos[1] <= sb and self.sections[i+1].pos[1] >= sb:
                x1 = self.sections[i].pos[0]
                x2 = self.sections[i+1].pos[0]

                y1 = self.sections[i].pos[1]
                y2 = self.sections[i+1].pos[1]
                
                z1 = self.sections[i].pos[2]
                z2 = self.sections[i+1].pos[2]
                x = x1 + (x2 - x1)*(sb - y1)/(y2 - y1)
                y = sb
                z = z1 + (z2 - z1)*(sb - y1)/(y2 - y1)
                return (x, y, z)
                
        for i in range(len(self.sections[:-1])):
            if self.sections[i].pos[2] <= sb and self.sections[i+1].pos[2] >= sb:
                x1 = self.sections[i].pos[0]
                x2 = self.sections[i+1].pos[0]

                y1 = self.sections[i].pos[1]
                y2 = self.sections[i+1].pos[1]
                
                z1 = self.sections[i].pos[2]
                z2 = self.sections[i+1].pos[2]
                x = x1 + (x2 - x1)*(sb - z1)/(z2 - z1)
                y = y1 + (y2 - y1)*(sb - z1)/(z2 - z1)
                z = sb
                return (x, y, z)

    def analyze_geometry(self):
        if self.vertical:
            self.b = abs(self.sections[0].pos[2] - self.sections[-1].pos[2])
        else:
            self.b = abs(self.sections[0].pos[1] - self.sections[-1].pos[1])
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

    def avl_text(self, name, position, angle, component):
        avl_coord = lambda v : (-v[0], v[1], -v[2]) # Attention to the fact that AVL uses x downstream (back), z up
        text = '\n'
        text += 'SURFACE\n'                     # Keyword
        text += name + '\n'                   # Surface name
        text += self.discretization + '\n'         # Discretization settings
        text += 'ANGLE\n%.5f\n' % angle       # Surface Incidence
        text += 'COMPONENT\n%d\n' % component # Index
        text += 'TRANSLATE\n%.3f\t%.3f\t%.3f\n' % avl_coord(position)
        if self.ydup:
            text += 'YDUPLICATE\n0.0\n'
        for sec in self.original_sections:
            text += 'SECTION\n'
            text += '%.3f %.3f %.3f ' % avl_coord(sec.pos) # Coordenadas
            text += '%.3f %.3f\n' % (sec.chord, sec.ainc)
            text += 'AFILE\n%s\n' % sec.airfoil.path
        return text
    
    def add_control(self, start, end, chord, multiplier):
        pass