
# Based on:
# Module: tree_search
# by:
# (c) Luis Seabra Lopes
# Introducao a Inteligencia Artificial, 2012-2019,
# Inteligência Artificial, 2014-2019

# This module provides a set of classes for automated solving
# of the Sokoban problem through tree search:
#    Sokoban / Man  - problem domains
#    SearchProblem - concrete problems to be solved, includes Deadlock detetion methods
#    SearchNode    - search tree nodes
#    SearchTree / SearchTreeMan    - search trees with the necessary methods for searching

from abc import ABC, abstractmethod
from mapa import Map
from consts import Tiles
import copy
import asyncio
import time
from queue import PriorityQueue
# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc

class Sokoban:
    def __init__(self, max_y, max_x, sok_map):

        self.max_y = max_y
        self.max_x = max_x
        self.sok_map = sok_map

    def is_walkable(self,y,x,boxes):
        if(self.sok_map[y][x]==Tiles.WALL) or ((x,y) in boxes):
            return False
        else:
            return True

    def actions(self,state):
        if(state==None):
            return []
        actlist = []    # p = push ; u = up ; d = down ; l = left ; r = right
                        #action: pl/pr/pu/pd, box_pos, new_box_pos
        p = SearchProblem(Man(self.max_y,self.max_x,self.sok_map),state,None)
        t = SearchTreeMan(p, 'breadth')
        t.search()
        reachable = t.states_visited
        boxes = state[0]
        
        for box in boxes:
            box_x, box_y = box

            if self.is_walkable(box_y,box_x-1,boxes) and self.is_walkable(box_y,box_x+1,boxes) and (str((box_x+1,box_y)) in reachable):
                actlist.append( ("pl",box,(box_x-1,box_y)) )

            if self.is_walkable(box_y,box_x+1,boxes) and self.is_walkable(box_y,box_x-1,boxes) and (str((box_x-1,box_y)) in reachable):
                actlist.append( ("pr",box,(box_x+1,box_y)) )

            if self.is_walkable(box_y-1,box_x,boxes) and self.is_walkable(box_y+1,box_x,boxes) and (str((box_x,box_y+1)) in reachable):
                actlist.append( ("pu",box,(box_x,box_y-1)) )

            if self.is_walkable(box_y+1,box_x,boxes) and self.is_walkable(box_y-1,box_x,boxes) and (str((box_x,box_y-1)) in reachable):
                actlist.append( ("pd",box,(box_x,box_y+1)) )

        return actlist

    def result(self,state,action):
        if(state!=None):
            move,box_pos,nbox_pos = action
            
            nboxes = state[0].copy()
            nboxes.remove(box_pos)
            nboxes.add(nbox_pos)

            newstate = (nboxes, box_pos)
            return newstate

    def cost(self, state, action):
        return 1

    def heuristic(self, state, goal):
        boxes = state[0]
        h = 0
        counter = 0
        for b in boxes:
            g = goal[counter]
            counter+=1
            h += abs(b[0]-g[0])+abs(b[1]-g[1])
        return h

    def satisfies(self, state, goal):
        if(state==None):
            return False
        for pos in goal:
            if(pos not in state[0]):
                return False
        return True


class Man:
    def __init__(self, max_y, max_x, sok_map):
        self.max_y = max_y
        self.max_x = max_x
        self.sok_map = sok_map

    def actions(self,state):
        if(state==None):
            return []
        actlist = [] # u = up ; d = down ; l = left ; r = right
        man_pos = state[1]
        man_x,man_y = man_pos
        
        l = [ (man_x-1,man_y), self.sok_map[man_y][man_x-1]]

        r = [ (man_x+1,man_y), self.sok_map[man_y][man_x+1]]

        u = [ (man_x,man_y-1), self.sok_map[man_y-1][man_x]]

        d = [ (man_x,man_y+1), self.sok_map[man_y+1][man_x]]

        if (not l[1]==Tiles.WALL) and (l[0] not in state[0]):  #if not a box and not a wall
            actlist.append(("a",man_pos,l[0]))
        if (not r[1]==Tiles.WALL) and (r[0] not in state[0]):
            actlist.append(("d",man_pos,r[0]))
        if (not u[1]==Tiles.WALL) and (u[0] not in state[0]):
            actlist.append(("w",man_pos,u[0]))
        if (not d[1]==Tiles.WALL) and (d[0] not in state[0]):
            actlist.append(("s",man_pos,d[0]))
        return actlist

    def result(self,state,action):
        if(state!=None):
            move,pos,pos1 = action
            newstate = (state[0].copy(), pos1)
            
            return newstate

    def cost(self, state, action):
        return 1

    def heuristic(self, state, goal, strategy):
        if strategy=='a*':
            man = state[1]
            return abs(man[0]-goal[0])+abs(man[1]-goal[1])
        return 0

    def satisfies(self, state, goal): #goal: obective coordinates
        if(state==None):
            return False
        if(goal==state[1]):
            return True
        return False


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
        self.max_y = domain.max_y
        self.max_x = domain.max_x
        self.dead_spaces = set()

        if isinstance(domain, Sokoban):
            for y in range(1,self.max_y-1):
                for x in range(1,self.max_x-1):
                    if self.is_dead_space(y,x,domain.sok_map):
                        self.dead_spaces.add((x,y))

    def is_box(self,tile):
        if(tile==Tiles.BOX or tile==Tiles.BOX_ON_GOAL):
            return True
        else:
            return False

    def is_walkable(self,tile):
        if(tile==Tiles.FLOOR or tile==Tiles.GOAL or tile==Tiles.MAN or tile==Tiles.MAN_ON_GOAL):
            return True
        else:
            return False

    def is_dead_space(self, y, x, sok_map):
        if sok_map[y][x]==Tiles.WALL:
            return True
        if sok_map[y][x]==Tiles.GOAL or sok_map[y][x]==Tiles.BOX_ON_GOAL or sok_map[y][x]==Tiles.MAN_ON_GOAL:
            return False

        for offset in [-1, 1]:
            if(sok_map[y+offset][x]==Tiles.WALL):     #Vertical Check
                if(sok_map[y][x-1]==Tiles.WALL or sok_map[y][x+1]==Tiles.WALL):     #Literal Corners
                    return True

                for direction in [-1, 1]:   #Dead Row?
                    i = x + direction
                    while (i>=0) and (i<self.max_x) and not sok_map[y][i]==Tiles.WALL:
                        if self.is_walkable(sok_map[y + offset][i]):
                            return False
                        elif self.is_box(sok_map[y + offset][i]):
                            return self.freeze_lock(y+offset,i,sok_map,"h")
                        elif sok_map[y][i]==Tiles.GOAL or sok_map[y][i]==Tiles.MAN_ON_GOAL or sok_map[y][i]==Tiles.BOX_ON_GOAL:
                            return False
                        i += direction
                return True
            
            if(sok_map[y][x+offset]==Tiles.WALL):     #Horizontal Check             
                if(sok_map[y-1][x]==Tiles.WALL or sok_map[y+1][x]==Tiles.WALL):     #Literal Corners
                    return True

                for direction in [-1, 1]:   #Dead Collumn?
                    i = y + direction
                    while (i>=0) and (i<self.max_y) and not sok_map[i][x]==Tiles.WALL:
                        if self.is_walkable(sok_map[i][x + offset]):
                            return False
                        elif self.is_box(sok_map[i][x + offset]):
                            return self.freeze_lock(i,x+offset,sok_map,"v")
                        elif sok_map[i][x]==Tiles.GOAL or sok_map[i][x]==Tiles.MAN_ON_GOAL or sok_map[i][x]==Tiles.BOX_ON_GOAL:
                            return False
                        i += direction
                return True
            
        return False

    def square_lock(self,y,x,boxes):
        if (x-1,y-1) in boxes:
            if (x,y-1) in boxes and (x-1,y) in boxes:
                return True
        if (x+1,y+1) in boxes:
            if (x,y+1) in boxes and (x+1,y) in boxes:
                return True
        if (x+1,y-1) in boxes:
            if (x,y-1) in boxes and (x+1,y) in boxes:
                return True
        if (x-1,y+1) in boxes:
            if (x,y+1) in boxes and (x-1,y) in boxes:
                return True
        return False

    def freeze_lock(self, y, x, boxes, skip=None):
        blocked_h = False
        blocked_v = False

        if self.square_lock(y,x,boxes):
            return True

        if skip=="v":
            blocked_v = True
        else:
            if self.domain.sok_map[y-1][x]==Tiles.WALL or self.domain.sok_map[y+1][x]==Tiles.WALL:
                blocked_v = True
            elif (x,y-1) in self.dead_spaces and (x,y+1) in self.dead_spaces:
                blocked_v = True
            elif (x,y-1) in boxes:
                blocked_v = self.freeze_lock(y-1,x,boxes,"v")
            elif (x,y+1) in boxes:
                blocked_v = self.freeze_lock(y+1,x,boxes,"v")

        if skip=="h":
            blocked_h = True
        else:
            if self.domain.sok_map[y][x-1]==Tiles.WALL or self.domain.sok_map[y][x+1]==Tiles.WALL:
                blocked_h = True
            elif (x-1,y) in self.dead_spaces and (x+1,y) in self.dead_spaces:
                blocked_h = True
            elif (x-1,y) in boxes:
                blocked_h = self.freeze_lock(y,x-1,boxes,"h")
            elif (x+1,y) in boxes:
                blocked_h = self.freeze_lock(y,x+1,boxes,"h")
        
        return (blocked_h and blocked_v)

    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent, depth, cost, heuristic, action, strategy='breadth'):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.action = action
        self.strategy=strategy

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)
    def __lt__(self, other):
        if self.strategy=='a*':
            selfPriority = self.heuristic+self.cost
            otherPriority = other.heuristic+other.cost
        else:
            selfPriority = self.heuristic
            otherPriority = other.heuristic
        return selfPriority < otherPriority

# Arvores de pesquisa
class SearchTree:
    # construtor
    def __init__(self,problem, strategy='breadth'): 
        self.problem = problem
        self.root = SearchNode(problem.initial, None, 0, 0, 0, None, strategy)
        self.open_nodes = PriorityQueue()
        self.open_nodes.put(self.root)
        self.strategy = strategy
        self.solution = None
        self.terminals = 1
        self.non_terminals = 0
        self.states_visited = set()
        
    @property
    def avg_branching(self):
        return round((self.terminals + self.non_terminals -1) / self.non_terminals , 2)

    @property
    def length(self):
        return self.solution.depth

    @property
    def cost(self):
        return self.solution.cost

    @property
    def plan(self):
        return self.get_plan(self.solution)

    def is_deadlock(self, newstate):
        if newstate==None:
            return True
        
        for box in newstate[0]:
            if box in self.problem.goal:
                continue
            if (box in self.problem.dead_spaces) or self.problem.freeze_lock(box[1],box[0],newstate[0]):
                return True
        return False

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return path

    def get_plan(self, node):
        if node == None or node.parent == None:
            return []
        plan = self.get_plan(node.parent)
        plan += [node.action]
        return plan

    # procurar a solucao com async
    async def async_search(self, limit=None):
        while self.open_nodes != []:
            await asyncio.sleep(0)
            node = self.open_nodes.get()
            if self.problem.goal_test(node.state):
                self.solution = node
                self.terminals = self.open_nodes.qsize() + 1
                return self.get_path(node)
            lnewnodes = []
            self.non_terminals += 1
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                
                if (not str(( tuple(newstate[0]), newstate[1] )) in self.states_visited) and (not self.is_deadlock(newstate))  and (limit == None or newnode.depth <= limit):
                    newnode = SearchNode(newstate,node, node.depth+1, node.cost+self.problem.domain.cost(node.state,a), self.problem.domain.heuristic(newstate, self.problem.goal), a, self.strategy)
                    lnewnodes.append(newnode)
                    self.states_visited.add(str(( tuple(newstate[0]), newstate[1] )))
            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
            for n in lnewnodes:
                self.open_nodes.put(n)

class SearchTreeMan:
    # construtor
    def __init__(self,problem, strategy='breadth'): 
        self.problem = problem
        self.root = SearchNode(problem.initial, None, 0, 0, 0, None)
        self.open_nodes = [self.root]
        self.strategy = strategy
        self.solution = None
        self.terminals = 1
        self.non_terminals = 0
        self.states_visited = set()

    @property
    def cost(self):
        return self.solution.cost

    @property
    def plan(self):
        return self.get_plan(self.solution)

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return path

    def get_plan(self, node):
        if node == None or node.parent == None:
            return []
        plan = self.get_plan(node.parent)
        plan += [node.action]
        return plan

    # procurar a solucao sem async
    def search(self, limit=None):
        self.states_visited.add(str(self.problem.initial[1]))
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            
            if self.problem.goal!=None and self.problem.goal_test(node.state):
                self.solution = node
                self.terminals = len(self.open_nodes) + 1
                return self.get_path(node)
            lnewnodes = []
            self.non_terminals += 1
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                if (not str(newstate[1]) in self.states_visited)  and (limit == None or newnode.depth <= limit):
                    newnode = SearchNode(newstate,node, node.depth+1, node.cost+self.problem.domain.cost(node.state,a), self.problem.domain.heuristic(newstate, self.problem.goal, self.strategy), a)
                    lnewnodes.append(newnode)
                    self.states_visited.add(str(newstate[1]))
            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'a*':
            self.open_nodes= sorted(self.open_nodes + lnewnodes, key = lambda node: node.cost + node.heuristic)
