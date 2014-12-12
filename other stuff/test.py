import sys, os, math

class updateTagReport:
	def __init__(self):
		self.i = 0
		self.k = 0
		self.doSomeStuff()
		self.printSomeStuff()
		print "Done"
	def doSomeStuff(self):
		self.i = 22
		self.k = self.i + 2

	def printSomeStuff(self):
		print self.i 
		print self.k


def main():
	test = updateTagReport()

if __name__ == '__main__': main()