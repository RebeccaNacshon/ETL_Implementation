class CorruptedException(Exception):
    def __init___(self, filename):
        #Exception.__init__(self, "my exception was raised with arguments {0}".format(filename))
        #self.filename = filename
        pass

def check_filename(filename):
    if filename == 'corrupt':
     raise CorruptedException(filename)
     """	This is a custom exception that deals with a file named 'corrupt' means it is corrupted.
     """