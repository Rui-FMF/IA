# Name: Rui Filipe Monteiro Fernandes
# NMEC: 92952
from tree_search import *
from cidades import *
from strips import *


class MyTree(SearchTree):

    def __init__(self,problem, strategy='breadth'): 
        super().__init__(problem,strategy)
        self.root.depth=0
        self.root.offset=0
        self.from_init=None
        self.to_goal=None

    def hybrid1_add_to_open(self,lnewnodes):
        while lnewnodes!=[]:
            self.open_nodes[:0] = [lnewnodes.pop(0)]
            if lnewnodes!=[]:
                self.open_nodes.append(lnewnodes.pop(0))

    def hybrid2_add_to_open(self,lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda n: n.depth - n.offset)

    def search2(self):
        offset_dic = {}
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                self.terminal = len(self.open_nodes)+1
                self.solution = node
                return self.get_path(node)
            self.non_terminal+=1
            node.children = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                if newstate not in self.get_path(node):
                    newnode = SearchNode(newstate,node)
                    newnode.depth = node.depth+1
                    if newnode.depth in offset_dic:
                        offset_dic[newnode.depth]+=1
                    else:
                        offset_dic[newnode.depth]=0
                    newnode.offset = offset_dic[newnode.depth]
                    node.children.append(newnode)
            self.add_to_open(node.children)
        return None


    def search_from_middle(self):

        init = self.problem.initial
        goal = self.problem.goal
        m = self.problem.domain.middle(init,goal)

        if m==None:
            return self.search()


        self.from_init = MyTree(SearchProblem(self.problem.domain, init, m))
        self.to_goal = MyTree(SearchProblem(self.problem.domain, m, goal))

        return self.from_init.search() + self.to_goal.search()[1:]


class MinhasCidades(Cidades):

    # state that minimizes heuristic(state1,middle)+heuristic(middle,state2)
    def middle(self,city1,city2):
        for con in self.connections:
            if city1 in con and city2 in con:
                return None

        m = []
        for c in self.coordinates:
            if c!=city1 and c!=city2:
                val = self.heuristic(city1,c)+self.heuristic(c,city2)
                m.append((c,val))
        return sorted(m, key=lambda c: c[1])[0][0]

class MySTRIPS(STRIPS):
    def result(self, state, action):
        if not all(p in state for p in action.pc):
            return None
        newstate = [p for p in state if p not in action.neg]
        newstate.extend(action.pos)
        return newstate

    def sort(self,state):
        return sorted(state, key=lambda p: str(p))





