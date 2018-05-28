import jsocket_base
import threading
import socket
import time
import logging


logger = logging.getLogger("jsocket.tserver")



class ThreadedServer(threading.Thread, jsocket_base.JsonServer):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        jsocket_base.JsonServer.__init__(self, **kwargs)
        self._isAlive = False

    def _process_message(self, obj):
        """ Pure Virtual Method

            This method is called every time a JSON object is received from a client

            @param	obj	JSON "key: value" object received from client
            @retval	None
        """
        pass

    def run(self):
        while self._isAlive:
            try:
                self.accept_connection()
            except socket.timeout as e:
                logger.debug("socket.timeout: %s" % e)
                continue
            except Exception as e:
                logger.exception(e)
                continue

            while self._isAlive:
                try:
                    obj = self.read_obj()
                    self._process_message(obj)
                except socket.timeout as e:
                    logger.debug("socket.timeout: %s" % e)
                    continue
                except Exception as e:
                    logger.exception(e)
                    self._close_connection()
                    break
            self.close()

    def start(self):
        """ Starts the threaded server.
            The newly living know nothing of the dead

            @retval None
        """
        self._isAlive = True
        super(ThreadedServer, self).start()
        logger.debug("Threaded Server has been started.")

    def stop(self):
        """ Stops the threaded server.
            The life of the dead is in the memory of the living

            @retval None
        """
        self._isAlive = False
        logger.debug("Threaded Server has been stopped.")


class ServerFactoryThread(threading.Thread, jsocket_base.JsonSocket):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        jsocket_base.JsonSocket.__init__(self, **kwargs)

    def swap_socket(self, new_sock):
        """ Swaps the existing socket with a new one. Useful for setting socket after a new connection.

            @param	new_sock	socket to replace the existing default jsocket.JsonSocket object
            @retval	None
        """
        del self.socket
        self.socket = new_sock
        self.conn = self.socket

    def run(self):
        while self.isAlive():
            try:
                obj = self.read_obj()
                self._process_message(obj)
            except socket.timeout as e:
                logger.debug("socket.timeout: %s" % e)
                continue
            except Exception as e:
                logger.info("client connection broken, closing socket")
                self._close_connection()
                break
        self.close()


class ServerFactory(ThreadedServer):
    def __init__(self, server_thread, **kwargs):
        ThreadedServer.__init__(self, **kwargs)
        if not issubclass(server_thread, ServerFactoryThread):
            raise TypeError("serverThread not of type", ServerFactoryThread)
        self._thread_type = server_thread
        self._threads = []

    def run(self):
        while self._isAlive:
            tmp = self._thread_type()
            self._purge_threads()
            while not self.connected and self._isAlive:
                try:
                    self.accept_connection()
                except socket.timeout as e:
                    logger.debug("socket.timeout: %s" % e)
                    continue
                except Exception as e:
                    logger.exception(e)
                    continue
                else:
                    tmp.swap_socket(self.conn)
                    tmp.start()
                    self._threads.append(tmp)
                    break

        self._wait_to_exit()
        self.close()

    def stop_all(self):
        for t in self._threads:
            if t.isAlive():
                t.exit()
                t.join()

    def _purge_threads(self):
        for t in self._threads:
            if not t.isAlive():
                self._threads.remove(t)

    def _wait_to_exit(self):
        while self._get_num_of_active_threads():
            time.sleep(0.2)

    def _get_num_of_active_threads(self):
        return len([True for x in self._threads if x.isAlive()])

    active = property(_get_num_of_active_threads, doc="number of active threads")