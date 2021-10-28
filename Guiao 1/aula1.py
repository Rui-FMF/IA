#Exercicio 1.1
def comprimento(lista):
	if lista == []:
		return 0
	else:
		return 1 + comprimento(lista[1:])

#Exercicio 1.2
def soma(lista):
	if lista == []:
		return 0
	else:
		return lista[0] + soma(lista[1:])

#Exercicio 1.3
def existe(lista, elem):

	if lista == []:
		return False
	
	if lista[0] == elem:
		return True
		
	return existe(lista[1:], elem)


#Exercicio 1.4
def concat(l1, l2):
	if l1 == []:
		return l2

	if l2 == []:
		return l1
	
	l1.append(l2[0])

	return concat(l1, l2[1:])

#Exercicio 1.5
def inverte(lista):
	if lista == []:
		return []

	inv = inverte(lista[1:])
	inv.append(lista[0])

	return inv

#Exercicio 1.6
def capicua(lista):
	if lista == []:
		return True

	if lista[0] != lista[-1]:
		return False
	else:
		return capicua(lista[1:-1])

#Exercicio 1.7
def explode(lista):
	if lista == []:
		return []
	else:
		return lista[0] + explode(lista[1:])

#Exercicio 1.8
def substitui(lista, original, novo):
	if lista == []:
		return []

	if lista[0] == original:
		return [novo] + substitui(lista[1:], original, novo)
	else:
		return [lista[0]] + substitui(lista[1:], original, novo)
	
#Exercicio 1.9
def junta_ordenado(lista1, lista2):
	
	if lista1 == []:
		return lista2
	
	if lista2 == []:
		return lista1

	if lista1[0] <= lista2[0]:
		return [lista1[0]] + junta_ordenado(lista1[1:], lista2)
	else:
		return [lista2[0]] + junta_ordenado(lista1, lista2[1:])

#Exercicio 2.1
def separar(lista):
	if lista == []:
		return [], []

	a, b = lista[0]
	la, lb = separar(lista[1:])

	return [a]+la, [b]+lb

#Exercicio 2.2
def remove_e_conta(lista, elem):
	if lista == []:
		return [], 0

	l, c = remove_e_conta(lista[1:], elem)

	if lista[0] == elem:
		return l, c+1
	
	return [lista[0]] + l, c

#Exercicio 3.1
def cabeca(lista):
	pass

#Exercicio 3.2
def cauda(lista):
	pass

#Exercicio 3.3
def juntar(l1, l2):
	if len(l1) != len(l2):
		return None

	if l1 == []:
		return []

	return [(l1[0], l2[0])] + juntar(l1[1:], l2[1:])

#Exercicio 3.4
def menor(lista):
	
	if lista == []:
		return None
	
	m = menor(lista[1:])
	
	if m is None or lista[0] < m:
		return lista[0]

	return m


#Exercicio 3.6
def max_min(lista):

	if lista == []:
		return None

	M, m = max_min(lista[1:])

	if M is None or m is None:
		return lista[0], lista[0]

	if lista[0] < m:
		return M, lista[0]
	
	if lista[0] > M:
		return lista[0], m

	return M, m
