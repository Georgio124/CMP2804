#this file contains all the event handler function for the gui interace buttons
#libraries
from tkinter import *
from tkinter import messagebox
import threading
import graph_2

#supporting files
from main_server import *
#from interface import block_ip_entry

#threading class
class thread_Server(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(thread_Server, self).__init__(*args,**kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        raise Exception

    def stopped(self):
        return self._stop_event.is_set()
    
#global threads
#first thread
server_Thread = thread_Server(target=serve,args=())
#second thread
health_check = thread_Server(target=check_state,args=())

#booting the server button
#it contains two threads
#first runs the server and second runs the background checks to determine the health of the connection
def click_server():    
    server_Thread.start()
    #server_Thread.stop()   
    health_check.start()
    #displying the status
    messagebox.showinfo("Status", "Server is started!")

def click_stop():
    #checking if the thread is still running
    if server_Thread.is_alive():
        #stopping the server
        server_stopped()
        messagebox.showinfo("Status", "Server has stoped!")
                      
    else:
        #displying that the server is stopped
        messagebox.showinfo("Status", "Server is not running!")

#displaying the graph 
def click_graph():
    #graph disply
    graph_display = threading.Thread(target=graph_2.plot_graph, args=())
    graph_display.start()

#changing tcp request time
def click_timeout():
    #checking if the thread is still running
    if server_Thread.is_alive():
        reduce_connection_time()
        messagebox.showinfo("Status", "Request time has changed!")
                      
    else:
        #displying that the server is stopped
        messagebox.showinfo("Status", "Server is not running!")
    

#blocking an ip by adding it to the database
"""def click_add_ip():
    #checking if the text is empty
    input_txt  = block_ip_entry.get()
    if input_txt == "":
        messagebox.showwarning("Status", "The text box is empty")
    else:
        #add ip to the database
        pass"""

