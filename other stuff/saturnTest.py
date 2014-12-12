from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import sys, math, os, Image, threading


texture = [0 for x in range(4)]

saturnImage = Image.open('saturn.jpg')
ringsImage = Image.open('saturnringcolor.jpg')

class SaturnDemo(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
		self.angle = 0						#calculateDisk()
		self.j =  0 						#drawDisk()

		self.diskVertexX = []
		self.diskVertexY = []

		#Initial rotation
		self.defViewAngleX = 0
		self.defViewAngleY = 90

		self.viewAngleX = self.defViewAngleX
		self.viewAngleY = self.defViewAngleY
		self.angleX = 0 - self.viewAngleX
		self.angleY = 0 - self.viewAngleY
	
	def run(self):
		self.initDisplay()
	
	
	def initDisplay(self):
		glutInit()
		glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)
		glutInitWindowSize(730, 730)
		glutCreateWindow("Saturn Demo")
		
		self.initLighting()
		self.initMaterial()
		
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glEnable(GL_TEXTURE_2D)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		
		self.loadPlanet()
		self.loadRings()
		glutDisplayFunc(self.render)
		glMatrixMode(GL_PROJECTION)
		gluPerspective(30.0, 1.0, 1.0, 30)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
		glutMainLoop()
		

	def loadPlanet(self):
		glGenTextures(4, texture)
		glBindTexture(GL_TEXTURE_2D, texture[0])
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

		try:
			ix, iy, sImageData = saturnImage.size[0], saturnImage.size[1], saturnImage.tostring("raw", "RGBA", 0, -1)
		except SystemError:
			ix, iy, sImageData = saturnImage.size[0], saturnImage.size[1], saturnImage.tostring("raw", "RGBX", 0, -1)
			
		glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, sImageData)
		
		self.planet = gluNewQuadric()
		gluQuadricTexture(self.planet, GL_TRUE)


	def loadRings(self):
		glBindTexture(GL_TEXTURE_2D, texture[1])
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

		glBindTexture(GL_TEXTURE_2D, texture[2])
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

		glBindTexture(GL_TEXTURE_2D, texture[3])
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		
		try:
			ix2, iy2, rImageData = ringsImage.size[0], ringsImage.size[1], ringsImage.tostring("raw", "RGBA", 0, -1)
		except SystemError:
			ix2, iy2, rImageData = ringsImage.size[0], ringsImage.size[1], ringsImage.tostring("raw","RGBX", 0, -1)

		glTexImage2D(GL_TEXTURE_2D, 0, 3, ix2, iy2, 0, GL_RGBA, GL_UNSIGNED_BYTE, rImageData)


	def calculateDisk(self):
		rads = math.atan(1) / 45.
		radius1 = 0.744
		radius2 = 1.402

		while self.angle <= 360:
			self.angle += 8
			            
			#Calculate position of vertices for inner circle
			self.diskVertexX.append(radius1 * math.sin(rads * (self.angle - 90)))
			self.diskVertexY.append(radius1 * math.sin(rads * self.angle))

			#Calculate position of vertices for outer circle
			self.diskVertexX.append(radius2 * math.sin(rads * (self.angle - 90)))
			self.diskVertexY.append(radius2 * math.sin(rads * self.angle))
			self.drawDisk()


	def drawDisk(self):
		while self.j <= (len(self.diskVertexX) - 3) and self.j <= (len(self.diskVertexY) - 3):
			glBegin(GL_TRIANGLES)

			#1st triangle
			glTexCoord2f(0, 0)
			glVertex3f(self.diskVertexX[self.j], self.diskVertexY[self.j], 0)
			glTexCoord2f(1, 0)
			glVertex3f(self.diskVertexX[self.j + 1], self.diskVertexY[self.j + 1], 0)
			glTexCoord2f(0, 1)
			glVertex3f(self.diskVertexX[self.j + 2], self.diskVertexY[self.j + 2], 0)

			#2nd triangle
			glTexCoord2f(1, 1)
			glVertex3f(self.diskVertexX[self.j + 3], self.diskVertexY[self.j + 3], 0)
			glTexCoord2f(0, 1)
			glVertex3f(self.diskVertexX[self.j + 2], self.diskVertexY[self.j + 2], 0)
			glTexCoord2f(1, 0)
			glVertex3f(self.diskVertexX[self.j + 1], self.diskVertexY[self.j + 1], 0)

			self.j += 2

			glEnd()


	def setAngles (self, x, y, z):
		if x != self.angleX or y != self.angleY or self.angleZ != z:
			self.angleX = x
			self.angleY = y
			self.angleZ = z

		xAccel = x - 50
		yAccel = y - 50
		zAccel = z - 50

		if zAccel != 0.0:
			senseAngleX = float((180. / 3.14149) * math.atan(xAccel / zAccel))
			senseAngleY = float(math.sin(zAccel) * (180. / 3.14149) * math.atan(yAccel / zAccel))

		self.angleX = senseAngleX - self.viewAngleX
		self.angleY = senseAngleY - self.viewAngleY


	def render(self):
		glClearColor(0.0, 0.0, 0.0, 1.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		glPushMatrix()
		glTranslatef(0.0, 0.0, 0.0)
		glRotatef(self.angleX, 1.0, 0.0, 0.0)
		glTranslatef(0.0, 0.0, 0.0)
		glRotatef(self.angleY, 0.0, 1.0, 0.0)
		glTranslatef(0.0, 0.0, 0.0)
		
		glBindTexture(GL_TEXTURE_2D, texture[0])
		glColor3f(1.0, 1.0, 1.0)
		gluSphere(self.planet, 0.601, 40, 40)

		self.calculateDisk()
		
		glPopMatrix()
		
		glutSwapBuffers()
		glutPostRedisplay()
		

	def initLighting(self):
		ambientLight 	= [1.0, float(0.8), float(0.8), 1.0]
		diffuseLight 	= [1.0, float(0.8), float(0.8), 1.0]
		lightPos	 	= [0.0, 0.0, 50.0, 0.0]
		spotDirection	= [0.0, -2.0, -1.0, 1.0]
		
		glEnable(GL_LIGHT0)
		glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
		glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
		glEnable(GL_LIGHTING)
		

	def initMaterial(self):
		mat_specular 	= [0.0, 0.0, 1.0, 1.0]
		mat_diffuse 	= [0.0, 0.0, float(0.7), 1.0]
		mat_ambient 	= [0.0, 0.0, 1.0, 1.0]
		mat_shininess 	= [5.0]

		glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
		glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)
		glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
		glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)

		glEnable(GL_COLOR_MATERIAL)		
