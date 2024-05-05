#file containg the webserver code

#libraries
import http
import http.server
from os import path

#variables 
host_name = "loalhost"
#any valid port
port = 8080
#home directory of the html code
page_directory = "c:\\Users\\harsi\\desktop\\TSE"

#server web class
class myserverhandel(http.server.BaseHTTPRequestHandler):

    my_add : str
    #header of the page
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
    
    #setting the path to get the correct page 
    def get_path(self) -> str :
        content_path = path.join(page_directory, "myser.html")
        return content_path
    
    #adding content 
    def get_content(self, content_path) -> bytes :
        with open(content_path, mode='r' , encoding='utf-8') as f:
            content = f.read()
            return bytes(content,'utf-8')

    #get http request
    def do_GET(self) -> None:
        self._set_headers()
        #getting clients address
        self.my_add =  self.client_address[0]

        #checking if the  ip is blocked 
        #get list of blocked ip from the database
        blocked_ip = []
        #check bit
        parity = 0
        for ip in blocked_ip:
            if ip == self.my_add :
                parity = 1
                break
        #checking for parity
        if parity == 0 :
            #address is not blocked 
             #writing the address into a text file
            try:
                with open("ip_file.txt", "a") as file:
                    file.write(self.my_add + "\n")
            except:
                print("Cannot open the file")
            
            #loading the web page
            self.wfile.write(self.get_content(self.get_path()))
        else:
            #sending a 404 code back
            self.send_response(404)
       