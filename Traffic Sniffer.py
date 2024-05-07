from scapy.all import *

def packet_callback(packet):
    #Prints summary of a captured packet
    print(packet)

def main():
    
    try:
        print("Starting packet capture. Press Ctrl+C to stop.")
        #prn passes sniff fnc the packet callback, making function print each packet it captures
        sniff(prn=packet_callback)

    #IO Management
    except KeyboardInterrupt:
        print("\nStopped packet capture.")
    except Exception as e:
        print(f"An error occurred: {e}")

main()
