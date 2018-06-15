from socket import *
import ctypes

print(ctypes.windll.shell32.IsUserAnAdmin())
#UDP_IP = "172.16.0.255"
UDP_IP = "255.255.255.255"
UDP_PORT = 56700
MESSAGE = "Hello, World!"

#print "UDP target IP:", UDP_IP
#print "UDP target port:", UDP_PORT
#print "message:", MESSAGE

sock = socket(AF_INET, # Internet
                     SOCK_DGRAM) # UDP

sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)					 
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))


#from socket import *
#cs = socket(AF_INET, SOCK_DGRAM)
#cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#cs.sendto('This is a test'.encode(), ('255.255.255.255', 54545))