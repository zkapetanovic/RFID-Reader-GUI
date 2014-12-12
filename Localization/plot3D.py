# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 13:59:20 2014

@author: yizhao
@fun:   3D Canvas view setting
"""
from visual import *
import globals

class plot3D():
    def __init__(self):
         l= 80
         rx=16.25
         ry=14.25
         w = 6
         h = 6
         self.x = arrow(pos=(0,0,0), axis=(l/2,0,0), shaftwidth=3,color=color.red)
         self.xt =text(pos=(l/3,3,3),text='X',axis=self.x.axis,
                       align='center', depth=-0.3, color=color.red,height=h,width=w)
    
         self.y = arrow(pos=(0,0,0), axis=(0,l/2,0), shaftwidth=3,color=color.red)
         self.yt =text(pos=(15,l/3,3),text='Y',axis=self.x.axis,
                       align='center', depth=-0.3, color=color.red,height=h,width=w)
                       
         self.z = arrow(pos=(0,0,0), axis=(0,0,l), shaftwidth=3,color=color.red)
         self.zt =text(pos=(2,10,l-30),text='',axis=-self.z.axis,
                       align='center', depth=-0.3, color=color.red,height=h,width=w)
         
         self.groundT1 = sphere(pos=globals.p[0],radius=3,color=color.orange,opacity=0.4)
         self.groundT2 = sphere(pos=globals.p[1],radius=3,color=color.orange,opacity=0.4)
         self.groundT3 = sphere(pos=globals.p[2],radius=3,color=color.orange,opacity=0.4)
         self.groundT4 = sphere(pos=globals.p[3],radius=3,color=color.orange,opacity=0.4)
         #self.groundT = sphere(pos=(-10,-27,79.375),radius=3,color=color.green)
         
         #self.ground1 = sphere(pos=(-rx,ry,0.25),radius=3,color=color.orange)
         #self.ground2 = sphere(pos=(-rx,-ry,0.25),radius=3,color=color.orange)
         #self.ground3 = sphere(pos=(rx,ry,0.25),radius=3,color=color.orange)
         #self.ground4 = sphere(pos=(rx,-ry,0.25),radius=3,color=color.orange)
         #lamp = local_light(pos=(8,80,100), color=color.yellow)
         c=1    #white
         cc=0.9   #black
         checkerboard = ((cc,c,cc,c,cc,c,cc,c), 
                         (c,cc,c,cc,c,cc,c,cc),
                         (cc,c,cc,c,cc,c,cc,c),
                         (c,cc,c,cc,c,cc,c,cc),
                         (cc,c,cc,c,cc,c,cc,c), 
                         (c,cc,c,cc,c,cc,c,cc),
                         (cc,c,cc,c,cc,c,cc,c),
                         (c,cc,c,cc,c,cc,c,cc))
         tex = materials.texture(data=checkerboard,mapping="rectangular", interpolate=False)
         self.reader = box(pos=(0,0,l/2),size=(33,29,l),color=color.cyan,opacity=0.3)
         #self.floorzx = box(axis=(0,1,0),pos=(0,0,l/2),size=(0.1,l,l),material=tex,opacity=0.8)
         #self.floorzy = box(axis=(1,0,0),pos=(0,0,l/2),size=(0.1,l,l),material=tex,opacity=0.8)
         self.floorxy = box(axis=(0,0,1),pos=(0,0,0),size=(0.1,l,l),material=tex,opacity=0.6)
         
         self.wallU   = box(axis=(0,1,0),pos=(0,l/2,l/2),size=(0.1,l,l),material=materials.wood,opacity=0.1)
         self.wallB   = box(axis=(0,1,0),pos=(0,-l/2,l/2),size=(0.1,l,l),material=materials.wood,opacity=0.1)
         self.wallL   = box(axis=(1,0,0),pos=(-l/2,0,l/2),size=(0.1,l,l),material=materials.wood,opacity=0.1)
         self.wallR   = box(axis=(1,0,0),pos=(l/2,0,l/2),size=(0.1,l,l),material=materials.wood,opacity=0.1)
         self.redDot  = points(pos=[(0,0,0)],size=5,color=color.red)
         self.blueDot  = points(pos=[(0,0,0)],size=5,color=color.blue)
         self.redDis  = ellipsoid(pos=(0,0,0),length=0, height=0, width=0,color=color.red,opacity=0.6)
         self.blueDis  =ellipsoid(pos=(0,0,0),length=0, height=0, width=0,color=color.blue,opacity=0.6)
         #create new spoint with trail
         self.redBall = sphere(make_trail=False,radius=2,color=color.yellow) 
    def  RedPoint():
         self.RedP=points(pos=[(0,0,0)],size=3,color=color.red)
         #self.numP = size(self.points)
         return self.RedP