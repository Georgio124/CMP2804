import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time

#x = [0]
#x = np.linspace(0, 2 * np.pi, 200)
#y = np.sin(x)


#this  function updates the value of y axis x axis 
#and returns a tuple
def update_axes():
    yAxis = []
    try :
        with open("ping_time.txt") as file:
            while True:
                mid_value = file.readline()
                #checking if the list is empty
                if mid_value == '':
                    break
                else:
                    mid_value = mid_value.split()
                    for i in mid_value:
                        yAxis.append(float(i))
        #x axis 
        xAxis =  np.linspace(0,len(yAxis), len(yAxis))
        return  xAxis,yAxis
    except:
        print("cannot open the ping time file")
          
        
#this function plots the graph
def plot_graph():
    #creating the plot figure
    fig, ax = plt.subplots()
    #calculating the x and y values 
    xAxis,yAxis = update_axes()
    #plotting the graph
    ax.plot(xAxis, yAxis)
    #setting labels
    ax.set(xlabel = "Time", ylabel="Ping")
    #displaying the graph
    plt.show()
        
