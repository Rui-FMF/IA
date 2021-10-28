#encoding: utf8

from semantic_network import *
from bayes_net import *
from constraintsearch import *
from collections import Counter

class MyBN(BayesNet):

    def individual_probabilities(self):
        res = {}

        variables = [k for k in self.dependencies.keys()]

        for v in variables:
            temp_vars = [k for k in self.dependencies.keys() if k != v]
            res[v] = sum([ self.jointProb([(v, True)] + conj) for conj in self._generate_conjunctions(temp_vars) ])
        
        return res

    def _generate_conjunctions(self, variaveis):
        if len(variaveis) == 1:
            return [ [(variaveis[0], True)] , [(variaveis[0], False)] ]

        l = []
        for c in self._generate_conjunctions(variaveis[1:]):
            l.append([(variaveis[0], True)] + c)
            l.append([(variaveis[0], False)] + c)

        return l


class MySemNet(SemanticNetwork):
    def __init__(self):
        SemanticNetwork.__init__(self)

    def translate_ontology(self):
        res = []
        rels = list(set([d.relation for d in self.declarations if isinstance(d.relation, Subtype)]))

        for parent in sorted(list(set([r.entity2 for r in rels]))):
            formula = 'Qx '
            for child in sorted(list(set([r.entity1 for r in rels if r.entity2==parent]))):
                if len(formula)!=3:
                    formula+=' or '
                formula+=child.capitalize()+'(x)'
            formula+=' => '+parent.capitalize()+'(x)'
            res.append(formula)

        return res

    def query_inherit(self,entity,assoc):
        pds = [self.query_inherit(d.relation.entity2, assoc) for d in self.declarations if isinstance(d.relation, (Member, Subtype)) and d.relation.entity1==entity]

        query = [d for d in self.query_local(e1=entity, relname=assoc) if isinstance(d.relation, (Association))]

        rev_query = [d for d in self.query_local(e2=entity) if isinstance(d.relation, (Association)) and d.relation.inverse == assoc]

        return [d for sublist in pds for d in sublist] + query + rev_query

    def query(self,entity,relname):
        
        if relname=='subtype' or relname=='member':
            return [d.relation.entity2 for d in self.query_local(e1=entity, relname=relname)]

        local = self.query_local(e1=entity, relname=relname)

        properties, count = Counter([d.relation.assoc_properties() for d in local]).most_common(1)[0]
        
        if properties[0]=='single':
            dec = [d for d in self.query_cancel(entity, relname) if d.relation.assoc_properties()==properties]
            return [Counter(dec).most_common(1)[0][0].relation.entity2]
        elif properties[0]=='multiple':
            return list(set([d.relation.entity2 for d in self.query_inherit(entity, relname) if d.relation.assoc_properties()==properties]))


    def query_cancel(self, entity, assoc):
        pds = [self.query_cancel(d.relation.entity2, assoc) for d in self.declarations if isinstance(d.relation, (Member, Subtype)) and d.relation.entity1==entity]

        local = self.query_local(e1=entity, relname=assoc)

        pds_query = [d for sublist in pds for d in sublist if d.relation.name not in [l.relation.name for l in local]]

        return pds_query + local

class MyCS(ConstraintSearch):

    def search_all(self,domains=None,xpto=None):
        if domains==None:
            domains = self.domains

        # se alguma variavel tiver lista de valores vazia, falha
        if any([lv==[] for lv in domains.values()]):
            return None

        # se nenhuma variavel tiver mais do que um valor possivel, sucesso
        if all([len(lv)==1 for lv in list(domains.values())]):
            return [{ v:lv[0] for (v,lv) in domains.items() }]
       
        # continuação da pesquisa
        for var in domains.keys():
            if len(domains[var])>1:
                solutions = []
                for val in domains[var]:
                    newdomains = dict(domains)
                    newdomains[var] = [val]
                    
                    edges = [(v1,v2) for (v1,v2) in self.constraints if v2==var]
                    newdomains = self.constraint_propagation(newdomains,edges)

                    solution = self.search_all(newdomains)
                    if solution != None and solution not in solutions:
                        solutions+=solution
                return solutions
        
        return None


