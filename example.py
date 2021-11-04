from aircraft import *
import avl

s1223rtl = Airfoil("S1223RTL", path="c:/users/rubem/avl/s1223rtl.dat")
e169 = Airfoil("E169", path="c:/users/rubem/avl/e169.dat")
e193inv = Airfoil("E193INV", path="c:/users/rubem/avl/e193inv.dat")

wing_sections = [
    Section((0.00, 0.00, 0.00), 0.49, 0, s1223rtl),
    Section((0.00, 0.96, 0.00), 0.49, 0, s1223rtl),
    Section((0.00, 1.10, 0.00), 0.25, 0, s1223rtl)
]

wing = Surface(wing_sections, y_symmetry=True)


ht_sections = [
    Section((0.00, 0.00, 0.00), 0.29, 0, e193inv),
    Section((0.00, 0.75, 0.00), 0.29, 0, e193inv)
]

ht = Surface(ht_sections, y_symmetry=True)

vt_sections = [
    Section((0.00, 0.75, -0.00), 0.30, 0, e169),
    Section((-0.02, 0.75, -0.20), 0.28, 0, e169)
]

vt = Surface(vt_sections, y_symmetry=True)

jovita = Aircraft("JF21")

jovita.add_surface(wing, "Wing", (0.0, 0.0, 0.0), 6.0, group = 0)
jovita.add_surface(ht, "HT", (-0.415, 0.0, -0.438), -2.0, group = 1)
jovita.add_surface(vt, "VT", (-0.415, 0.0, -0.438), 0.0, group = 1)

print(avl.avl_results(jovita.avl_text(), ["trim"]))