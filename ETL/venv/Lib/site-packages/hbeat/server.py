# -----------------------------------------------------------------------------
#    HeartBeat - Yet Another HeartBeat Server
#    Copyright (C) 2011 Some Hackers In Town
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------------
import socket
import hashlib
import threading
import SocketServer

from hbeat.logging import logger


STATUS = {
    1: "OK",
    }


class HBProtocol (object):
    """
    HeartBeat protocol v1
    """
    status = 0
    host = None
    secret = None

    def __init__(self, data=None, status=0,
                 host=None, secret=None):
        if data:
            self.check(data)
            self.data = data
        self.host = host
        self.secret = secret
        self.status = status

    def check(self, data):
        """
        Check the integration of data.
        """
        if len(data) == 48:
            return True
        raise ValueError("'data' should have 48 byte of length.")

    def parse_data(self):
        """
        Return the status code for current data.
        """
        self.check(self.data)
        if self.data:
            self.status = ord(self.data[15])
            self.host = self.data[:15]
            self.hash_ = self.data[16:]
            return self.status, self.host.strip('\0'), self.hash_
        return None, None, None

    def create_packet(self):
        """
        Create a HeartBeat packet from status,
        host and secret key.
        """
        packet = None
        if self.host and self.status and self.secret:
            if len(self.host) <= 15:
                space = "\0" * (15 - len(self.host))
                if space:
                    packet = "%s%s" % (self.host, space)
                else:
                    packet = self.host

            else:
                raise TypeError("The size of 'host' should be less that" +
                                "15 charachter")
            if 1 <= self.status <= 255:
                packet = "%s%s" % (packet, chr(self.status))
            else:
                raise TypeError("'status' should be between 0 and 255.")

            m = hashlib.md5()
            m.update("%s%s" % (packet, self.secret))
            packet = "%s%s" % (packet, m.hexdigest())
            return packet
        raise ValueError("Missing some parameter to create packet.")

    def is_valid(self, secret):
        """
        check the current packet checksum.
        """
        secstring = "%s%s" % (self.data[:16],
                              secret)
        m = hashlib.md5()
        m.update(secstring)
        if self.data[16:] == m.hexdigest():
            return True
        else:
            return False


class TCPHandler(SocketServer.BaseRequestHandler, object):
    """
    The RequestHandler class for HearBeat server.

    It is instantiated once per connection to the server.
    """

    def __init__(self, *args, **kwargs):
        self.db = kwargs['db']
        del kwargs['db']
        super(TCPHandler, self).__init__(*args, **kwargs)

    def handle(self):
        self.data = self.request.recv(48).strip()
        packet = HBProtocol(data=self.data)
        status, host, hash_ = packet.parse_data()
        if not host.lower() in self.db.keys():
            self.request.send(chr(1))
            logger.warn("Invalid Host: '%s' IP: %s" % (host,
                                                     self.client_address[0]))
        else:

            if not packet.is_valid(self.db[host]["secret"]):
                logger.warn("Invalid packet form Host: '%s' IP: %s" % (host,
                                                    self.client_address[0]))
                self.request.send(chr(1))
            else:
                logger.info("Host: '%s' IP: %s Status: %s" % (host,
                                                        self.client_address[0],
                                                        STATUS[status]))
                self.request.send(chr(0))


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.currentThread()
        response = "%s: %s" % (cur_thread.getName(), data)
        self.request.send(response)


class ThreadedTCPServer(SocketServer.ThreadingMixIn,
                        SocketServer.TCPServer):
    pass


class TCPServer (SocketServer.TCPServer, object):

    def __init__(self, address, handler, db):
        super(TCPServer, self).__init__(address, handler)
        self.db = db

    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        self.RequestHandlerClass(request, client_address,
                                 self, db=self.db)


class ThreadedHeartBeatServer(object):
    """
    Threaded HeartBeat Server class.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = ThreadedTCPServer((host, int(port)),
                                        ThreadedTCPRequestHandler)

    def serve_forever(self):
        self.server.serve_forever()

    def start(self):
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.setDaemon(True)
        server_thread.start()


class HeartBeatServer(object):
    """
    HeartBeat Server class.
    """

    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.server = TCPServer((host, int(port)),
                                TCPHandler, db=db)

    def serve_forever(self):
        self.server.serve_forever()
