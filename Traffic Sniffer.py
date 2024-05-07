from scapy.all import *

def packet_callback(packet):
    #Prints summary of each captured packet
    print(packet)

def main():
    
    try:
        print("Starting packet capture. Press Ctrl+C to stop.")
        #Passes sniff fnc the packet callback
        sniff(prn=packet_callback)
    except KeyboardInterrupt:
        print("\nStopped packet capture.")
    except Exception as e:
        print(f"An error occurred: {e}")

main()