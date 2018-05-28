import logging
import socket
from database.sqlite_program import Database
from heartbeat.heartbeat import Heartbeat
from exception import corrupted_file_exception
import jsocket.tserver
import time

logger = logging.getLogger("jsocket.example_servers")
count = 1

"""	custom server which inherits ThreadedServer and implementing the _processMessage(obj) method."""
class MyServer(jsocket.tserver.ThreadedServer):
    """	This is a basic example of a custom ThreadedServer.	"""

    def __init__(self):
        super(MyServer, self).__init__()
        self.timeout = 40.0

        logger.warning("MyServer class in customServer is for example purposes only.")

    def _process_message(self, obj):
        """ virtual method """
        if obj != '':
            if obj['message'] == "new connection":
                logger.info("new connection.")
            else:
                logger.info(obj)


class MyFactoryThread(jsocket.tserver.ServerFactoryThread):
    """	This is an example factory thread, which the server factory will
        instantiate for each new connection.
    """

    def __init__(self):
        super(MyFactoryThread, self).__init__()
        self.timeout = 40.0


    def _process_message(self, obj):

        global count
        """
        Here I catch the message recieved from the client and 	procees it
        """
        if obj != '':

            if obj['message'] == "new connection":
                logger.info("new connection.")
            else:
                logger.info(obj)
                db = Database('test.db')
                """
                Definition of the database 	
                """
                db.create_table()

                """	if database already exists I retrieve the max id to increase the global parameter count for the new id
                   """
                max_id = db.retrieve_max_id()
                print max_id
                count = max_id + 1
                print count
                """	This is the heartbeat signal we send from server to database every minute
                   """
                Heartbeat(3600, db)
                for json in obj['message']:

                        """	Here we go through the json and parse it into the files 
                        """
                        print json['filename']
                        file_name = json['filename']

                        """	I check here if the file is corrupted using the custom exception class which contains function that checks if the 
                        file is named "corrupt" if it is exception is raised."""

                        try:
                            corrupted_file_exception.check_filename(file_name)
                        except :
                            print "corrupted file found!"
                            continue

                            """	here I insert the new file into the database
                               """

                        db.insert(count, file_name)
                        print count
                        print file_name
                        count = count + 1
                        print count

                        logger.info("in process method")


if __name__ == "__main__":
        server = jsocket.tserver.ServerFactory(MyFactoryThread, address=socket.gethostname(), port=8081)
        server.start()
        time.sleep(40)