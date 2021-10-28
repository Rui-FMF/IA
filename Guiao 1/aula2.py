#Exercicio 4.1
impar = lambda num: num%2 == 1

#Exercicio 4.2
positivo = lambda num: num > 0

#Exercicio 4.3
comparar_modulo = lambda x, y: abs(x) < abs(y)

#Exercicio 4.4
import math
cart2pol = lambda x, y: (math.sqrt(x*x + y*y), math.atan2(y, x))

#Exercicio 4.5
ex5 = lambda f, g, h: lambda x, y, z: f(g(x,y), h(y,z))

#Exercicio 4.6
def quantificador_universal(lista, f):
    #return lista == [e for e in lista if f(e)]
    return [e for e in lista if not f(e)] == []


#Exercicio 4.9
def ordem(lista, f):
    if len(lista) == 1:
        return lista[0]

    m = ordem(lista[1:], f)

    return lista[0] if f(lista[0], m) else m

#Exercicio 4.10
def filtrar_ordem(lista, f):
    if len(lista) == 1:
        return lista[0], []

    m, l = filtrar_ordem(lista[1:], f)

    return (lista[0], lista[1:]) if f(lista[0], m) else (m, [lista[0]] + l)

#Exercicio 5.2
def ordenar_seleccao(lista, ordem):
    if len(lista) == 1:
        return[lista[0]]

    m, l = filtrar_ordem(lista, ordem)

    return [m] + ordenar_seleccao(l, ordem)
    
