#this file is the interface of the main applciation
from tkinter import *
from tkinter import font
from tkinter import messagebox
import threading
import graph_2

#supporting files
from main_server import *


#event handler file
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
def click_add_ip():
    #checking if the text is empty
    input_txt  = block_ip_entry.get()
    if input_txt == "":
        messagebox.showwarning("Status", "The text box is empty")
    else:
        #add ip to the database
        pass


#main window 
root = Tk()

#font size
font_Size_lbl = font.Font(size=24)
font_Size_btn = font.Font(size=16)
#title of the application
root.title("Traffic Tracker")
# dimentions
root.geometry('700x500')

#lable welcoming
welcome_lbl = Label(root, text="Welcome, to start the server press start!", font=font_Size_lbl)
welcome_lbl.grid(column=2, padx=5, pady=5)

#boot the server
start_server = Button(root, text="Start Server", fg="white" , background="green", command=click_server,font=font_Size_btn )
start_server.grid(column=2, row= 5, padx=50, pady=50 )

#stopping the server
start_server = Button(root, text="Stop Server", fg="white" , background="red", command=click_stop,font=font_Size_btn )
start_server.grid(column=3, row = 5 )

#opening the graph
show_graph = Button(root, text= "Show Graph", fg="white", background="blue",command=click_graph, font=font_Size_btn )
show_graph.grid(column=2, row= 6)

#opening the graph
change_timeout = Button(root, text= "Change Timeout", fg="white", background="blue",command=click_timeout, font=font_Size_btn )
change_timeout.grid(column=3, row=6)

#fucntion for getting ips to block
add_ip_frame = Frame(root)
add_ip_frame.grid(column=2, row=7)
block_ip_lbl = Label(add_ip_frame, text= "Add ip address to block.", font=font.Font(size=14))
block_ip_lbl.grid(column=2, row = 7)

block_ip_entry = Entry(add_ip_frame)
block_ip_entry.grid(column=2, row=8)

block_ip_btn = Button(add_ip_frame, text="Submit", font=font.Font(size=10) )
block_ip_btn.grid(column=3, row=8)
#loop
root.mainloop()
