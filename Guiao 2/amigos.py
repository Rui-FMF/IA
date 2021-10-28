from constraintsearch import *

amigos = ["Andre", "Bernardo", "Claudio"]

def amigos_constraint(a1,t1,a2,t2):
    b1, c1 = t1
    b2, c2 = t2

    if b1 == b2 or c1 == c2:
        return False

    #Ninguem leva a sua bicicleta/chapeu
    if a1==b1 or a1==c1 or a2==b2 or a2==c2:
        return False

    #anda na bicicleta de um dos amigos e leva o chapeu de um dos outros
    if b1==c1 or b2==c2:
        return False

    #O que leva o chapeu do caludio anda na bicicleta do bernardo
    if (c1 == "Claudio" and b1 != "Bernardo") or (c2 == "Claudio" and b2 != "Bernardo"):
        return False

    return True

def make_constraint_graph():
    return { (X,Y):amigos_constraint for X in amigos for Y in amigos if X!=Y }

def make_domain():
    return { amigo:[(bicicleta, chapeu) for bicicleta in amigos for chapeu in amigos] for amigo in amigos }


cs = ConstraintSearch(make_domain(), make_constraint_graph())

#print(cs.search())
#print(cs.calls)
