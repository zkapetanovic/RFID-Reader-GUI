# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:38:10 2014
@note: TOA clock offset is +- 4cm 
       line fit error of p4 is changing the result
@author: yizhao
@fun:   #two trilateration algorithm
        1 PML
        2 non-linear
        #comput EPC into 3D location 
"""


import scipy,csv,sys 
import numpy as np
from numpy import*
import globals
from plot3D import*
#read csv file for test
#toa is counts for 32.768 KHZ clock

def coplane(dpr,plane):
    for i in xrange(len(dpr)):
        #print((dot(plane,dpr[i])/(np.linalg.norm(dpr[i])*np.linalg.norm(plane))))
        if (dot(plane,dpr[i])/(np.linalg.norm(dpr[i])*np.linalg.norm(plane)))>0.95:
           #print('coplane is',i,'th:',dpr[i],'plane is:',plane)
           return i
    return i+1      

def pairSelect(TOAs,rOpt='r',numTx=3):
    """
     PML Method:
    """
    #numTx = 4
    toa=[]
    toa.extend(TOAs[0:numTx])
    #print('opt in pairSelect',rOpt)
    #self.toa   = [1,2,3,4]
    if(toa[-1]==0):
        return np.array([0,0,0]) 
    p = globals.p[0:numTx]
    #parameters for after line fit
    fit = globals.fit[0:numTx]  

    tagTOA = np.array(toa,dtype = np.float32)
    #print(tagTOA,fit)
    r    = tagTOA * fit[:,0] + fit[:,1]
    if(min(r)<0):
        #do not have enough valid TOA
        print('TOA is wrong')
        return np.array([0,0,0]) 
      
    
    #pr     = np.c_[p,r]
    #dpr    = np.zeros(((numTx*numTx-1)/2,3))
    dpr    = np.zeros((0,3))
    ranks  = np.zeros(0)
    B      = np.zeros(0)
    Bp      = np.zeros(0)
    
    index = 0
    Mark = 1000
    pairs =[]
    
    err =  5
    errp  = 5
    for i in xrange(numTx-1):
        for j in range (i+1,numTx):
            plane=p[i]-p[j]
            pairs.append([i,j]) 
            #note: weight must larger than 25
            #weight=35
            rank={
                    'r':    (max(r[i],r[j])/min(r[i],r[j])),
                    'r*p':  (max(r[i],r[j])/min(r[i],r[j]))*(1/np.linalg.norm(plane)),
                    'r+p':  ((max(r[i],r[j])-min(r[i],r[j]))/min(r[i],r[j]))
                  }[rOpt]    
            #rank = (max(r[i],r[j])/min(r[i],r[j]))*(1/np.linalg.norm(plane))
            #rank = (max(r[i],r[j])/min(r[i],r[j]))+(1/np.linalg.norm(plane))
            #rank = (max(r[i],r[j])/min(r[i],r[j]))
            b = 0.5*((np.linalg.norm(p[i]))**2-(np.linalg.norm(p[j]))**2 + \
                r[j]**2 - r[i]**2 -err*(r[j]-r[i]) )
            bp= 0.5*((np.linalg.norm(p[i])**2)-(np.linalg.norm(p[j])**2) + \
                r[j]**2 - r[i]**2 +errp*(r[j]-r[i]))
            B = np.r_[B,b]
            Bp= np.r_[Bp,bp]
            ranks = np.r_[ranks,rank]
            if index!=0:
                coplanes= coplane(dpr,plane)
                #print('coplanes:',coplanes)
                if(ranks[coplanes]>rank):
                    ranks[coplanes] = Mark
                elif(ranks[coplanes]<rank):
                    ranks[index] = Mark        
            dpr=np.vstack([dpr,plane])
            #print('ranks:',ranks,'r',r)
            #self.pairs.append([index,[i,j],rank])
            index = index+1
    #pairs = np.c_[dpr,r,]
    #array of x1-x2 y1-y2 z1-z2 rank
    #print('ranks',ranks)
    dprank = np.c_[dpr,ranks,B,Bp,pairs]
    #print('dprank:',dprank)
    sortPlane = dprank[dprank[:,3].argsort()]
    #print('sortPlane:',sortPlane)
    if sortPlane[1,2]==Mark:
        print('cannot find noncoplane array')
        return np.array([0,0,0]) 
    else:
	    #sortPlane
	    #x1-x2 y1-y2 z1-z2 rank B bB i j]
        A = sortPlane[0:2,0:2]
        #print('selected pair',sortPlane[:,6:8])
        #the equacial is solvable
        if(np.linalg.matrix_rank(A)==2):
            sortPair = sortPlane[:,6:8]
            sortPair = sortPair.astype(int)
            #print('A:',A,'rank(a)',np.linalg.matrix_rank(A))
            rErr = np.linalg.solve(A, sortPlane[0:2,4])
            rpErr = np.linalg.solve(A, sortPlane[0:2,5])
            #print('B',sortPlane[0:3,4])
            #print('bB',sortPlane[0:3,5])
            #print('rErr',rErr,'rpErr',rpErr)
            xy=(rErr+rpErr)/2
            #print('xy',xy)
            z = r[sortPair[0]]**2-(p[sortPair[0],0]-xy[0])**2- \
                (p[sortPair[0],1]-xy[1])**2
            #z = r[sortPair[2]]**2-(p[sortPair[2],0]-xy[0])**2- \
            #(p[sortPair[2],1]-xy[1])**2
            #print('z',z)
            if(mean(z)<0):
                print('cannot calibrate toa',tagTOA)
                #print('sortPlane',sortPlane)
                return np.array([0,0,0])  
            z = np.sqrt(z)    
            p0 = np.r_[xy,mean(z)]
            #print('p0',p0)
            return p0
        else: 
            print('rank(A)<2:',A)
            #print('sortPlane',sortPlane)
            return np.array([0,0,0]) 



def caliXYZ(TOAs,numTx=3):
    """
     An efficient least-squares trilateration algorithm \
     for mobile robot localization

    """
    #print('TOAs:',TOAs)
    #coordinates of reference points(cm)
    p = globals.p[0:numTx]
    #parameters for after line fit
    fit = globals.fit[0:numTx]  
    
    toa=[]
    toa.extend(TOAs[0:numTx])
    tagTOA = np.array(toa,dtype = np.float64)
    #please note that x1^2 + x2^2 + x2^3 != x1*x2+x1*x3+x2*x3
    #[4,1,2,3]
    if numTx != p.shape[0]:
        print p.shape[0]
        print "Error:the num of referneces points is not correct"          
    # Tx-rx distance(cm)    
    r = tagTOA * fit[:,0] + fit[:,1]
    a = zeros((3,1))
    B = zeros((3,3))
    c = zeros((3,1))
    qtq = 0
    ff = zeros((2,1))
    H = zeros((3,3))
    HH = zeros((2,3))
    hh = zeros(((2,1)))
    
    for i in xrange(numTx):
        a = a + dot(dot(p[i][:,None],p[i][:,None].T),p[i][:,None]) - \
            r[i]**2*p[i][:,None]
        B = B + (-2*dot(p[i][:,None],p[i][:,None].T))- \
            dot(p[i][:,None].T,p[i][:,None])*eye((3))+r[i]**2*eye((3))
        c = c + p[i][:,None]    
    a = a/numTx
    B = B/numTx
    c = c/numTx
    f = a + dot(B,c)+2*dot(dot(c,c.T),c)
    #D = B + 2*dot(c,c.T)+dot(c.T,c)*eye((numTx))
    
    for i in xrange(numTx):
        qtq= qtq-dot(p[i][:,None].T,p[i][:,None]) + r[i]**2
        H = H-dot(p[i][:,None],p[i][:,None].T)
    qtq = qtq/numTx + dot(c.T,c)
    H = H*2/numTx + 2*dot(c,c.T)
    #print('qtq:',qtq)


    #################       solve function    ####################################
    for i in xrange(2):
        ff[i] = f[i]-f[2]
        HH[i,:] = H[i]-H[2]
        
    [Q,u] = linalg.qr(HH)
    v = dot(Q.T,ff)#Q.T * ff
    
    #(a+b*q3)^2 +(c+d*q3)^2+q3^2+qtq
    aa=(u[0,1]*v[1])/(u[0,0]*u[1,1]) - v[0]/u[0,0]
    bb=((u[0,1]*u[1,2])/(u[0,0]*u[1,1])) - u[0,2]/u[0,0]
    cc=v[1]/u[1,1]
    dd=u[1,2]/u[1,1]
   
    q = zeros((3,1))
    ae = bb*bb+dd*dd+1
    be = 2*aa*bb+2*cc*dd
    ce = aa*aa+cc*cc-qtq
    delta_s = be*be-4*ae*ce
    if(delta_s <0):
        #print("delta_s is smaller than 0")
        return q
    dl = np.sqrt(delta_s)
    q[2] = (-be+dl)/(2*ae)
    q[0] = aa+bb*q[2]
    q[1] = -cc-dd*q[2]
    p0 = q + c	    
    
    #print('p0:',p0)
    #print('qtq is',q[0]**2+q[1]**2+q[2]**2)
    return p0
    
#################   Computing EPC function    ###################################

def caliFile(filename,rOpt='r',numTx=3):
    """Given EPC logfile (*.csv), comput location"""
    print('rOpt',rOpt)
    win=plot3D()
    #create new points
    pointR = points(pos=[(0,0,0)],size=3,color=color.red)
    pointB = points(pos=[(0,0,0)],size=3,color=color.blue)
    #create new spoint with trail
    #ballR = sphere(make_trail=True,color=color.yellow) 
    #filename = 'test.csv'    
    f = open(filename,'rb')
    reader = f.readlines()
    l = len(reader)
    count = 0
    rerr=0
    berr=0
    while l > count and l > 0:    
        #reader = f.readlines()
        row = reader[count].split(',')
        count = count + 1
        if ((not row[0].endswith('FFFF')) and (row[0].startswith('B7')) and \
            (not row[0].endswith('0000'))) and int(row[4])>75:
        
            ##PML method
            #rp0=caliXYZ([int(row[4]),int(row[5]),int(row[6]),int(row[7])],4).T
            bp0 = [pairSelect([int(row[4]),int(row[5]),int(row[6]),int(row[7])],rOpt,numTx)]     
#           print('rp0',rp0)
            if not any(bp0)==0:
                pointB.pos=np.r_[pointB.pos,bp0]
            else:
                #print('failure calibate EPC',row[0])
                berr =berr+1
            #if not rp0[0][0]==0:
                #ballR.pos=rp0[0]
             
                
            ##non-linear close form
            rp0 = caliXYZ([int(row[4]),int(row[5]),int(row[6]),int(row[7])],numTx).T
            if not any(rp0)==0:
                pointR.pos=np.r_[pointR.pos,rp0]
            else:
                rerr = rerr+1
            #ppoint.radius = 10/p0[2]
            #rate(100,5,5,5)
            
            
            
    #red is for non-least square 
    mean=np.mean(pointR.pos,axis=0)
    std=np.std(pointR.pos,axis=0)
    dis= ellipsoid(pos=mean,length=std[0], height=std[1], width=std[2],color=color.red,opacity=1)
    print('distribution,least square mean',mean,'std',std)        
    
    mean2=np.mean(pointB.pos,axis=0)
    std2=np.std(pointB.pos,axis=0)
    dis2= ellipsoid(pos=mean2,length=std2[0], height=std2[1], width=std2[2],color=color.blue,opacity=1)
    print('distribution, PML mean',mean2,'std2',std2)        
    print('RedErr:',rerr,'BlueErr',berr)
               
                
if __name__ == "__main__":
    """
    Main function to convert EPC logfile into location logfile
    """
    #plot3D()
    #name='../test_data/'+globals.logName+'.csv'
    #print('file:',name)
    #caliFile(name,'r*p',numTx=4)
    #caliFile(name,'r*p',numTx=3)
    #caliFile(name,'r*p')
    toa=[  115.0000  ,199.9195  ,320.6142 , 409.9117]
#        [100.6020,  200.0713,  297.8535,  397.6452],
#        [105.2029 , 196.1548,  302.1547,  394.1621],
#        [106.7451 , 205.8638,  292.3278,  391.6112],
#        [110.8731,  202.2836,  296.8993,  388.7559]]
    #toa=[110.8731,  202.2836,  296.8993,  388.7559]
    #for toa in toas:
#    print('toa :',toa)
    #ed=pairSelect(toa,'r',3)
    ed=caliXYZ(toa,4)
    gt=np.array([-43.2000,  -32.4000, 93.1100, ])
    print('err',gt-ed.T,'norm',np.linalg.norm(gt-ed.T))
    print('estimate result',ed.T,'ground truth',gt)  
#    print('toa :',toa)
#    print('3TOA',caliXYZ(toa,3))  
#    print('4TOA',caliXYZ(toa,4))  
#    print('PML r*p',pairSelect(toa,'r*p',3))  
#    print('PML r',pairSelect(toa,'r',3))       