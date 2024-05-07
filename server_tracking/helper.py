##this file contains that tracks the connection strength 
import os
from pythonping import ping

#global avg ping time 
#in miliseconds
ping_time = 2.3

#checking the state 
def state(client_ip :str) -> bool :
    try:
        res = ping(target=client_ip)
    except:
        print("invalid client cannot ping the ip: " + client_ip)
    #printing the averrage time into a file
    try:
        with open("ping_time.txt", "a") as file:
            file.write(" " + str(res.rtt_avg_ms))
    except:
        print("cannot open the ping time file " )
    #comparing if the time is above avg
    if res.rtt_avg_ms > ping_time :
        return True
    else: 
        return False
    

