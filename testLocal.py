
import threading
from localThread import localThread
import globals 

def main():
	thread = localThread()
	thread.daemon = True
	thread.start()

if __name__ == '__main__':
	main()