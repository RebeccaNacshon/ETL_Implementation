import logging
import socket
import time
import json
import jsocket.jsocket_base
logger = logging.getLogger("jsocket.example_servers")

if __name__ == "__main__":
    """ basic json echo server """

cPids=[]

logger.debug("starting JsonClient")

"""	Here I connect the client to the socket
   """

client = jsocket.jsocket_base.JsonClient(address=socket.gethostname(), port=8081)
cPids.append(client)
client.connect()

"""	I send the json object to the server .
   """
client.send_obj({"message": "new connection"})
client.send_obj({"message": [{"filename": "file1"}, {"filename": "file2"},{"filename": "corrupt"}, {"filename": "file3"},{"filename": "file4"},{"filename": "file5"}, {"filename": "file6"},{"filename": "file7"},{"filename": "file8"},{"filename": "file9"},{"filename": "file10"}]})

print("Enter 'quit' to exit")

"""	here the user has the option to input the json
and we send the json input by the user to the server 
   """

message = raw_input(" Please enter the json --> :")
client.send_obj(json.loads(message))
logger.info("client connected")
logger.info(message)


time.sleep(40)
