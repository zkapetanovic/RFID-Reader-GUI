# -*- coding: utf-8 -*-
"""
Created on Thu Feb 06 11:51:39 2014
#the max error should be within 4cm
#error should be adaptively choose
@author: yizhao
@fun:   PML refinement Trilateration
"""

import numpy as np



class Pairs():
    def __init__(self,toa,numTx=4):
        self.toa =toa
        self.numTx = numTx
    def pairSelect(self):
        self.toa   = [1,2,3,4]
        p     = np.array([[18,28.8,0],[18,0,0],[-15.25,28.8,0],[-15.25,0,0]],dtype = np.float64)
        fit   = np.array([[1.044,-6.394],[1.063,-109.6],[1.057,-210.1],[1.971,-670.1]])
    
        tagTOA = np.array(self.toa,dtype = np.float64)
        r      = tagTOA * fit[:,0] + fit[:,1]
        #r      = list(r)
        pr     = np.c_[p,r]
        dpr    = np.zeros(0)
        pairs  = np.zeros(0)
        index = 0
        Mark = 1000
		#list all possible pair
        for i in xrange(self.numTx-1):
            for j in range (i+1,self.numTx):
                plane=pr[i]-pr[j]
                rank = (max(r[i],r[j])/min(r[i],r[j]))*(1/np.linalg.norm(plane))
                pairs = np.r_[pairs,rank]                 
                if index!=0:
                    coplaner= coplane(dpr,plane)
                    if(pairs[coplanner]>rank):
                        pairs[coplanner] = Mark
                dpr = np.r_[dpr,plane]
                #self.pairs.append([index,[i,j],rank])
                index = index+1
        #pairs = np.c_[dpr,r,]
        print('dpr:',dpr)
        dprank = np.c_(dpr,pairs)
        sortPlane = dprank[dprank[:,3].argsort()]
        A = sortPlane[0:3,:]
        #pair of neighboring tx
        for pair in pairs:
            if coplaner(pair,sPairs) and (rank(pair)<min(rSelect)):
                #replace the previous co-plannar pari with current pair
                sPairs.replace(pair,id)            
            else:
                if nSelect < nPair:
                    #add the current pair to the selected pairs                
                    sPairs.append(pair)
                    #resort the pair based on the rank
                else:
                    #replace the worst ranking selected pair with the current pair                
                    sPairs.replace(pair,id)
        return sPairs            
    
    #empirical ranking 
    #the larger pi,ps distance and the smaller difference of ri,rj
    # the larger the rank is                      
                
    def coplane(dpr,plane):
        for i in xrange(len(dpr)):
            if plane*dpr[i]/(np.abs(dpr[i])*np.abs(plane))>0.9:
               return i
        return i+1        
     
        
    def rank(p1,p2) :
        #p1=(x,y,z,r)
        return R
        
    def matrix(pairs):
        
        
