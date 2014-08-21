# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
1 stream real time camera
2 track small camera circles and plot
3 calibrate the camera model base on the chess board
4 plot the object as a circle based on 3D world coordinates and camera model
Author (C version): Eve Zhao
"""

#Camera Lib
import cv2.cv as cv
import cv2
from common import *
import video
import time,sys

#Math Lib
import numpy as np
import numpy

#System Lib
import sys, getopt
import os
from glob import glob
from multiprocessing import Pool
from time import sleep
#from PyQt4 import QtCore, QtGui

class cam():
    counter = 0; 
    def __init__(self,cam=0,root=1,canvas=1,mode='open'):
        #Creat Canvas for vedio stream
        self.index = cam
        self.cam = video.create_capture(0)
        self.root = root
        self.canvas = canvas
        self.winN = "cam"+str(cam)
        self.circleFlg = 0;
        self.tagPosition = np.asarray([(0,0,0)],dtype=np.float32)
        cv2.namedWindow(self.winN) #debug: Final Cam Frame     
		#Triangulation tracking parameter
        cv2.createTrackbar('x',self.winN,1000,2000,nothing)
        cv2.createTrackbar('y',self.winN,1000,2000,nothing)
        cv2.createTrackbar('z',self.winN,1000,2000,nothing)
		
        '''  
        ##Circle tracking
        #setting circle tracking parameters
        cv2.namedWindow("edge") #debug: plot edge frame
        cv2.createTrackbar('thrs1','edge',500,1000,nothing)
        cv2.createTrackbar('thrs2','edge',1000,2000,nothing)
        cv2.createTrackbar('dp','edge',2,8,nothing)
        cv2.createTrackbar('param1','edge',40,60,nothing)
        cv2.createTrackbar('param2','edge',100,200,nothing)
        cv2.createTrackbar('minRadius','edge',6,25,nothing)
        cv2.createTrackbar('maxRadius','edge',5,15,nothing)
        '''
        flag, self.img = self.cam.read()
        cv2.imshow(self.winN,self.img)	
        if mode == 'remodelCam':
		self.getChess()
		self.modelCam()
        elif mode == 'modelCam':
		self.modelCam()
        else:
            self.camera_matrix = np.loadtxt('./lib/camModel_result/camera_matrix.txt')
            self.dist_coefs    = np.loadtxt('./lib/camModel_result/dist_coefs.txt')
            self.rvecs = np.array([0,0,0],dtype=np.float64)
            self.tvecs = np.array([0,0,0],dtype=np.float64)
            
##Capture Chess Table to calibrate cameral Model
    # return:   Failure or Cameral Model Param         
    def getChess(self):
        #square_size = 33
        print "take numPhoto pictures of chess"
        numPhoto = 10 #10 will be better
        for i in xrange(numPhoto):
            #@TODO: trigger by button
            print "Click cam0 window and press "'SPACE'" to capture the %sth chess photo " % (i+1)
            while True:
                self.updateCam("Click cam0 window and press "'SPACE'"")
                key = cv2.waitKey(40)
                if key==32:
                     print "save to %s_chess.jpg" % (i+1)
                     cv2.imwrite('./lib/chess_photo/%s_chess.jpg' % (i+1),self.img)
                     break
                elif key == 27:
                     #use ESC key to close window
                     cv2.destroAllWindows()
                     break
        print "Finish capture %s chess picture" %numPhoto
        
    #Calibrate Cam model     
    def modelCam(self):
        #@TODO: check if the caliCam is sucessful
        #if self.square_size == Null:
        #square unit 33mm
        self.square_size = 33
        img_mask = './lib/chess_photo/*_chess.jpg'
        #debug_dir = './debug_dir'
        pattern_size = (7-1,6-1)  #width 7,height6
        pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
        pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)
        pattern_points *= self.square_size
        obj_points = []
        img_points = []
        img_names = glob(img_mask)
        h, w = 0, 0
        error_num = 0
        for fn in img_names:
            print 'processing %s...' % fn,
            img = cv2.imread(fn, 0)
            h, w = img.shape[:2]
            found, corners = cv2.findChessboardCorners(img, pattern_size)
            if found:
                term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )
                cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
            #if debug_dir:
                vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                cv2.drawChessboardCorners(vis, pattern_size, corners, found)
                path, name, ext = splitfn(fn)
                cv2.imwrite('./lib/foundCorner_photo/%s_chess_findCornor.bmp' % (name), vis)
                print path
                print name
                #print debug_dir
            if not found:
                print 'chessboard not found'
                error_num +=1
                continue
            img_points.append(corners.reshape(-1, 2))
            obj_points.append(pattern_points)
            print 'ok'
        rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h))
        #np.savetxt('./lib/camModel_result/rms.txt',rms)
        np.savetxt('./lib/camModel_result/camera_matrix.txt',camera_matrix)
        np.savetxt('./lib/camModel_result/dist_coefs.txt',dist_coefs)
        np.savetxt('./lib/camModel_result/rvecs.txt',rvecs)
        np.savetxt('./lib/camModel_result/tvecs.txt',tvecs)
        #recalibrate it again
        #rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h),camera_matrix,dist_coefs,rvecs,tvecs,flags=)
		
    
                    
    def closeCam(self):
        cv2.destroyAllWindows()
      
      
    def updateCam(self,fun):
        flag,img = self.cam.read()
        #print('update %s',fun)
        #while(img== 'NULL'):
            #print('wait for cam.read')
            #flag,img = self.cam.read()
        #print self.img.shape
        #print "current mode = %s" %fun
        self.img = img
        flag = False
        if fun== "trackCircle":
            self.circleTrack()
        elif fun=="trackTag" :
            self.projectTag(self.tagPosition)
        elif fun=="trackTagAndCircle":
            flag=self.projectTag(self.tagPosition)
            self.circleTrack()
        else :
            print "do nothing"
            if self.circleFlg == 1:        
                cv2.circle(self.img,self.circles,10,(255,0,0),3,8,0)
        #print('update img')  
        cv2.imshow(self.winN,self.img)
        cv2.waitKey(1)
        return flag
        #QImage(self.img.tostring(),self.img.width,self.img.height, QImage.Format_RGB888)
        #pixmap = QPixmap.fromImage(image)
       
     
    def projectTag(self,tagPosition):
        if tagPosition.any():
            print('tagPosition',tagPosition)
            #tagPosition[0][1] = 288-tagPosition[0][1]
            self.circleFlg = 1;
    		# 3Dpoint is the location of WISP
            #TODO the x,y,z is not scaled correctly
            #self.tagPosition = np.float64([10,20,40])
            #rvecs         = np.loadtxt('./lib/camModel_result/rvecs.txt')       
            #tvecs         = np.loadtxt('./lib/camModel_result/tvecs.txt')        
            #rvecsM = np.array([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float64)
            #rvecs = cv2.Rodrigues(rvecsM)
            tagPoint,jacobian = cv2.projectPoints(tagPosition,self.rvecs,self.tvecs,self.camera_matrix,self.dist_coefs)
            #print "tagPosition is:" 
            #print tagPoint
            #print tagPoint[0,0]
            #tagPoint,jacobian = cv2.projectPoints(tagPosition, rvecs,tvecs,camera_matrix,dist_coefs)
            #tagPoint = int(tagPoint)
            #radius = int(100/(self.tagPosition[0,2]+0.05))
            radius = 6
            #print "radius = %d" %radius
            print(tagPoint)
            x=int(tagPoint[0,0,0])
            y=int(tagPoint[0,0,1])
            if type(x) == long or type(y)==long:
                print('x,y is out range:',x,y)
                return
            self.circles = (x,y)
            cv2.circle(self.img,self.circles,radius,(0,0,255),3,8,0)
            return
         
    def circleTrack(self):
        ##TODO:filter out other color to track the circle with the same color as the WISP
        #hsv = cv2.cvtColor(self.img,cv.CV_BGR2HSV)
        #color = cv2.inRange(self.img,(0,10, 10),(240, 30,70))
        #gray =cv2.erode(self.img,color)
        #track circle
        self.circleFlg = 1
        '''
        #Optimized parameter
        thrs1 =700
        thrs2 =1240
        dp = 5
        param1 = 20
        param2 = 38
        minRadius = 14
        maxRadius = 4
        '''
        thrs1 = cv2.getTrackbarPos('thrs1','edge')
        thrs2 = cv2.getTrackbarPos('thrs2', 'edge')
        dp = cv2.getTrackbarPos('dp','edge')
        param1 = cv2.getTrackbarPos('param1', 'edge')
        param2 = cv2.getTrackbarPos('param2','edge')
        minRadius = cv2.getTrackbarPos('minRadius', 'edge')
        maxRadius = cv2.getTrackbarPos('maxRadius','edge')
       
	    #Img processing
        gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)       
        gray2=cv.fromarray(gray)
        edge = cv2.Canny(gray,thrs1,thrs2, apertureSize=5)
        cv.Smooth(cv.fromarray(gray),gray2,cv.CV_GAUSSIAN, 9,9)
        minDist = gray2.height/4
		
        #show edge frame
        vis = self.img.copy()
        vis /= 2
        vis[edge !=0] = (0,150,150)
        cv2.imshow("edge",vis)
       
        circles = cv2.HoughCircles(edge,cv2.cv.CV_HOUGH_GRADIENT,dp,minDist,param1,param2,minRadius,maxRadius)
        #circles = np.uint16(np.around(circles),decimals=0)
        try: 
            n = np.shape(circles)
            circles=np.reshape(circles,(n[1],n[2]))
            circles1=cv.fromarray(circles)
            #print circles
            for i in xrange ((circles1.width)-1):
                radius = int(np.around(circles1[i,2]))
                #print "radius: %s" % radius
                if (radius < 75) and (radius> 8):   
                    center = (circles1[i,0], circles1[i,1])
                    center = (np.around(center))
                    #print "center is : %s" %center
                    x = int(center[0])
                    y = int(center[1])
                    cv2.circle(self.img, (x,y), radius, (0, 0, 255), 3, 8, 0)
        except:
            print "circle track error or no circle"
         
    
    