import threading
import time
global starting_time

"""	This is a thread to send heartbeat messages from server to database.
     """
class Heartbeat(object):

        def __init__(self, interval,db):
            self.db = db
            self.interval = interval
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True  # Daemonize thread
            #self.function = function
            thread.start()

        def run(self):
            """ Method that runs forever """
            while True:
                print('Sending timestamp tp db')
                self.db.get_timestamp_message(time.time())
                time.sleep(self.interval)
