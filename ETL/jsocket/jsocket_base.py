import json
import socket
import struct
import logging
import time

logger = logging.getLogger("jsocket")
logger.setLevel(logging.DEBUG)
FORMAT = '[%(asctime)-15s][%(levelname)s][%(module)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT)

"""	
The JsonSocket class below is the base class for both the client and server objects. 
Its responsible for handling all the socket level send/receive operations. 
Each message contains two parts, a header and a payload. The header is nothing more then the length of the payload and 
the payload is just a JSON object.
"""

class JsonSocket(object):
    def __init__(self, address=socket.gethostname(), port=8081):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = self.socket
        self._timeout = None
        self._address = address
        self._port = port

    def send_obj(self, obj):
        msg = json.dumps(obj)
        if self.socket:
            frmt = "=%ds" % len(msg)
            packed_msg = struct.pack(frmt, msg)
            packed_hdr = struct.pack('!I', len(packed_msg))

            self._send(packed_hdr)
            self._send(packed_msg)

    def _send(self, msg):
        sent = 0
        while sent < len(msg):
            sent += self.conn.send(msg[sent:])

    def _read(self, size):
        data = ''
        while len(data) < size:
            data_tmp = self.conn.recv(size - len(data))
            data += data_tmp
            if data_tmp == '':
                raise RuntimeError("socket connection broken")
        return data

    def _msg_length(self):
        d = self._read(4)
        s = struct.unpack('!I', d)
        return s[0]

    def read_obj(self):
        size = self._msg_length()
        data = self._read(size)
        frmt = "=%ds" % size
        msg = struct.unpack(frmt, data)
        return json.loads(msg[0])

    def close(self):
        self._close_socket()
        if self.socket is not self.conn:
            self._close_connection()

    def _close_socket(self):
        logger.debug("closing main socket")
        self.socket.close()

    def _close_connection(self):
        logger.debug("closing the connection socket")
        self.conn.close()

    def _get_timeout(self):
        return self._timeout

    def _set_timeout(self, timeout):
        self._timeout = timeout
        self.socket.settimeout(timeout)

    def _get_address(self):
        return self._address

    def _set_address(self, address):
        pass

    def _get_port(self):
        return self._port

    def _set_port(self, port):
        pass

    timeout = property(_get_timeout, _set_timeout, doc='Get/set the socket timeout')
    address = property(_get_address, _set_address, doc='read only property socket address')
    port = property(_get_port, _set_port, doc='read only property socket port')

"""	
The JsonServer class defined below inherits the above JsonSocket and makes available many of the standard server 
operations such as listen, bind and accept. You can invoke this class directly if you want to add a 
JsonServer to an already existing thread. However, the preferred method is to inherit the ThreadedServer class described below.


"""
class JsonServer(JsonSocket):
    def __init__(self, address=socket.gethostname(), port=8081):
        super(JsonServer, self).__init__(address, port)
        self._bind()

    def _bind(self):
        self.socket.bind((self.address, self.port))

    def _listen(self):
        self.socket.listen(4)

    def _accept(self):
        return self.socket.accept()

    def accept_connection(self):
        self._listen()
        self.conn, addr = self._accept()
        self.conn.settimeout(self.timeout)
        logger.debug("connection accepted, conn socket (%s,%d)" % (addr[0], addr[1]))

    def _is_connected(self):
        return True if not self.conn else False

    connected = property(_is_connected, doc="True if server is connected")

"""	
Just like the JsonServer class above, the JsonClient also inherits the JsonSocket base class. For simplicity, 
and thanks to the functionality encapsulation of JsonSocket, the client only needs to support one connect method.


"""
class JsonClient(JsonSocket):
    def __init__(self, address=socket.gethostname(), port=8081):
        super(JsonClient, self).__init__(address, port)

    def connect(self):
        for i in range(10):
            try:
                self.socket.connect((self.address, self.port))
            except socket.error as msg:
                logger.error("SockThread Error: %s" % msg)
                time.sleep(40)
                continue
            logger.info("...Socket Connected")
            return True
        return False