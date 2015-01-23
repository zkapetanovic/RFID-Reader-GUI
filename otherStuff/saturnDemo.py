from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import sys, math, os, Image, threading

try:
	from PIL.Image import open
except ImportError, err:
	from Image import open


class SaturnDemo(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.angle = 0						#calculateDisk()
		self.j =  0 						#drawDisk()
		self.i = 0

		self.diskVertexX = []
		self.diskVertexY = []


		#Initial rotation
		self.defViewAngleX = 10
		self.defViewAngleY = 45

		self.viewAngleX = self.defViewAngleX
		self.viewAngleY = self.defViewAngleY
		self.angleX = 0 - self.viewAngleX
		self.angleY = 0 - self.viewAngleY
		self.angleZ = 0


	def run(self):
		self.drawInit()


	def drawInit():
		glutInit()
		glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)
		glutInitWindowSize(700, 700)
		glutCreateWindow('Saturn Demo')

		glClearColor(0.0, 0.0, 0.0, 0.0)
		glEnable(GL_TEXTURE_2D)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		self.initLighting()
		self.initMaterial()
		self.loadPlanet()
		#self.loadRings()
		self.calculateDisk()
		glutDisplayFunc(self.drawSaturn)

		self.planet = gluNewQuadric()
		gluQuadricTexture(self.planet, GL_TRUE)

		glMatrixMode(GL_PROJECTION)
		gluPerspective(30.0, 1.0, 1.0, 30)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
		glutMainLoop()


	def loadPlanet(self):
		self.saturnImage = Image.open("saturn.jpg")		

		try:
			ix, iy, sImageData = self.saturnImage.size[0], self.saturnImage.size[1], self.saturnImage.tostring("raw", "RGBA", 0, -1)
		except SystemError:
			ix, iy, sImageData = self.saturnImage.size[0], self.saturnImage.size[1], self.saturnImage.tostring("raw", "RGBX", 0, -1)
			
		self.ID = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.ID)
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		
		glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, sImageData)


	def loadRings(self):
		self.ringsImage = Image.open("saturnringcolor.jpg")

		try:
			ix2, iy2, rImageData = self.ringsImage.size[0], self.ringsImage.size[1], self.ringsImage.tostring("raw", "RGBA", 0, -1)
		except SystemError:
			ix2, iy2, rImageData = self.ringsImage.size[0], self.ringsImage.size[1], self.ringsImage.tostring("raw","RGBX", 0, -1)

		self.ID_2 = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.ID_2)
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

		glTexImage2D(GL_TEXTURE_2D, 0, 3, ix2, iy2, 0, GL_RGBA, GL_UNSIGNED_BYTE, rImageData)

		self.calculateDisk()

	def loadPlanetTexture(self):
		#Configure texture rendering parameters
		glEnable(GL_TEXTURE_2D)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		#glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

		#Reselect the texture (if there are multiple textures)
		glBindTexture(GL_TEXTURE_2D, self.ID)


	def loadRingsTexture(self):
		glEnable(GL_TEXTURE_2D)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

		glBindTexture(GL_TEXTURE_2D, self.ID_2)


	def drawSaturn(self):
		glClearColor(0.0, 0.0, 0.0, 1.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		#glLoadIdentity()   #makes the planet disappear

		glPushMatrix()

		#Rotate
		glRotatef(self.angleX, 1.0, 0.0, 0.0)
		glRotatef(self.angleY, 0.0, 1.0, 0.0)

		#Draw Planet
		self.loadPlanetTexture()
		glColor3f(1.0, 1.0, 1.0)
		gluSphere(self.planet, 0.601, 40, 40)

		#Draw Rings 
		#self.loadRingsTexture()
		#glColor3f(1.0, 0.88, 0.82)
		#self.drawDisk()

		glColor3ub(209, 172, 143)
		glutSolidTorus(0.03, 0.89, 3, 40) #1st
		glColor3ub(249, 178, 123)
		glutSolidTorus(0.03, 0.94, 3, 40) #2nd
		glColor3ub(223, 152, 97)
		glutSolidTorus(0.04, 1, 3, 40) #3rd
		glColor3ub(220, 198, 124)
		glutSolidTorus(0.05, 1.06, 3, 40) #4th
		glColor3ub(182, 157, 75)
		glutSolidTorus(0.02, 1.08, 3, 40) #5th
		glColor3ub(201, 183, 124)
		glutSolidTorus(0.03, 1.1, 3, 40) #6th
		glColor3ub(102, 51, 0)
		glutSolidTorus(0.02, 1.13, 3, 40) #7th

		glPopMatrix()

		glutSwapBuffers()
		glutPostRedisplay()


	def calculateDisk(self):
		rads = math.atan(1) / 45.
		radius1 = 0.744
		radius2 = 1.402

		while self.angle <= 360:
			self.angle += 8

			self.diskVertexX.append(radius1 * math.sin(rads * (self.angle - 90.)))
			self.diskVertexY.append(radius1 * math.sin(rads * self.angle))

			self.diskVertexX.append(radius2 * math.sin(rads * (self.angle - 90.)))
			self.diskVertexY.append(radius2 * math.sin(rads * self.angle))


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



	def updatePlanet(self, xAccel, yAccel, zAccel):		
		xAccel = xAccel - 50
		yAccel = yAccel - 50
		zAccel = zAccel - 50

		if zAccel != 0.0:
			senseAngleX = ((180. / 3.14159) * math.atan(xAccel / zAccel)) 
			senseAngleY = (math.sign(zAccel) * (180./ 3.14159) * math.atan(yAccel / zAccel))
	
		self.angleX = senseAngleX - self.viewAngleX
		self.angleY = senseAngleY - self.viewAngleY	


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



#if __name__ == '__main__': SaturnDemo()