from constraintsearch import *

region = ['A', 'B', 'C', 'D', 'E']
colors = ['red', 'blue', 'green', 'yellow', 'white']

def mapa_constraint(r1, c1, r2, c2):
    return c1 != c2


def make_constraint_graph(mapa):
    return { (X,Y):mapa_constraint for X in mapa.keys() for Y in mapa[X] if X!=Y }


def make_domain(mapa):
    return { reg:colors for reg in mapa.keys() }


mapa_a = {
    'A': ['D', 'E', 'B'],
    'B': ['A', 'E', 'C'],
    'C': ['B', 'E', 'D'],
    'D': ['A', 'E', 'C'],
    'E': ['A', 'B', 'C', 'D']

}

mapa_b = {
    'A': "DEB",
    'B': "AEC",
    'C': "BEF",
    'D': "AEF",
    'E': "ABCDF",
    'F': "DEC"
}

mapa_c = {
    'A': "BFED",
    'B': "AFC",
    'C': "BFGD",
    'D': "AEGC",
    'E': "AFGD",
    'F': "ABCGE",
    'G': "EFCD"
}


cs = ConstraintSearch(make_domain(mapa_a), make_constraint_graph(mapa_a))
print(cs.search())
csb = ConstraintSearch(make_domain(mapa_b), make_constraint_graph(mapa_b))
print(csb.search())
csc = ConstraintSearch(make_domain(mapa_c), make_constraint_graph(mapa_c))
print(csc.search())
