import numpy as np
import networkx as nx
from ..utils.misc import one_hot

def recur(ns,s,nen,candidates,i,Resultcandi,tmplt,world):
    m=len(ns)
    n=len(candidates[0]) #n is number of nodes in world graph
    candidates_copy=candidates.copy()
    if i <= m - 1 :
        candidates = candidates_copy
        idx = ns[i]
        UNC = np.nonzero(candidates[idx])[0] #UNC is the list of indexes of candidates of ith node
        ii = i#record i
        for w in UNC:    #for each index w in the candidate list
            i = ii #reset i
        #   candidates_copy=candidates.copy()
            for k in range(n):
                candidates[idx][k]= k == w #choose w as the candidate for ith node
            _, _, candidates = run_filters(
                tmplt, world, candidates=candidates, filters=cheap_filters,
                init_changed_cands=None,#run the cheap filters
                verbose=False)
            if ~np.all(candidates.any(axis=1)):
                continue  #if the candidate list is empty for some node, choose next w
            if i < m - 1:
                i = i + 1 #go to i+1 th node in template
                print(i)
                tmplt,world,candidates,Resultcandi=recur(ns,s,nen,candidates,i,Resultcandi,tmplt,world)#recursion
            else:
                candilist = []
                for index in ns:
                    ttemp=np.nonzero(candidates[index])[0]
                    candilist.append(ttmp[0])#record the current candidate combination
                rs=world.is_nbr[candilist[0]]
                for index in candilist:
                    b = world.is_nbr[index] 
                    rs = rs & b # find the common neighbours of all the current candidates
                rs=rs & candidate[s] #should also be in the candidate set of s
                if sum(rs) >= nen:
                    for j in range(m):
                        k=candilist[j]
                        Resultcandi[ns[j]][k]=True #add j th node in the candidate combination to the candidate of jth node
    return tmplt, world, candidates,Resultcandi

        
def nfilter(s,nen,tmplt, world, candidates):
    """
    ns is the neighbours of one supernode
    nen is the number of equivalent nodes to that supernode
    """
    Resultcandi=candidates
    ns=np.nonzero(tmplt.is_nbr[s])[0]
    for index in ns:
        for k in range(len(candidates[1])):
            Resultcandi[index][k]=False
    i = 0
    tmplt,world,candidates,Resultcandi=recur(ns,s,nen,candidates,i,Resultcandi,tmplt,world)
    candidates=Resultcandi
    return tmplt, world, candidates
    
def new_filter(supernodeslist, nenlist,tmplt,world,candidates):
    for i in range(len(supernodeslist)):
        s=supernodeslist[i]
        nen=nenlist[i]
        tmplt,world,candidates=nfilter(s,nen,tmplt,world,candidates)
    return tmplt, world, candidates