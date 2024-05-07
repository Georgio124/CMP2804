#main python file

#libraries
from _thread import *
import time
import socketserver

#additional files
import helper
import http_server
from tkinter import messagebox

#fucntion to check the ping average time
#checking function
def check_state()  :
    global RUN_CHECK 
    RUN_CHECK = True
    while RUN_CHECK :
        #getting the current in seconds
        this_second = int(time.time())
        #running only once in a minute
        if this_second % 10 == 0 :
            #try
            try:
                with open("ip_file.txt") as file:
                    ip_add = file.readline()
            except:
                print("cannot read the file")

            #getting only the ip address => removing the new line character    
            ip_add = ip_add.split()
            ip_add = ip_add[0]
            #calling the fucntion that calls the ping fucntion
            #if retuns true means there is posibility of attack
            if helper.state(ip_add):
                #rasing a dailog box
                messagebox.showinfo("Caution!", "Possiblity of an attack!")
            #offsetting the time so that it won't run in a loop
            time.sleep(1)

#server using the sockets
def serve():
    global httpd
    httpd =  socketserver.TCPServer(("", http_server.port), http_server.myserverhandel)
    #message displying the server is running
    print("it is running")
    #server in a loop
    httpd.serve_forever()
        
#stopping server 
def server_stopped():
    #shutting the server
    httpd.shutdown()
    RUN_CHECK = True


#mitigation techniques
def reduce_connection_time():
    httpd.timeout = 2.0