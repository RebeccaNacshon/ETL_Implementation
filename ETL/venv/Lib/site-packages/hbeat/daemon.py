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


import os
import sys
import stat
import signal
import atexit
from pwd import getpwnam
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError


class HeartBeatDaemon (object):
    """
    Daemon class of HeartBeat, this class runs the HeartBeat in a daemon
    state (by default). You can think about this class as the main
    class of HeartBeat. This class use the *option* parameter for its
    configuration. *option* parameter is an object that created with
    optparser class and contains the command line parameters.

    if user decide to run the HeartBeat in background, then all of the
    IO transactions will redirect to given *stdin*, *stdout* and
    *stderr*.
    """

    def __init__(self, options, stdin='/dev/null', stdout='/dev/null',
                 stderr='/dev/null'):

        from hbeat.logging.base import setup_logger

        self.options = options

        # PID configurations ===================================
        self.piddir = options.piddir.rstrip("/")

        # debbox pid files
        self.mpid = "/".join((self.piddir, "heartbeat.pid"))

        # creating configuration object ========================
        #: confifgurewr
        self.config = ConfigParser()
        if os.path.exists(self.options.conf):
            self.config.read(self.options.conf)
        else:
            raise self.CantFindConfigFile()

        try:
            self.db = {}
            for line in file(self.options.db).readlines():
                if not line.strip(" ").startswith("#"):
                    name, secret = line.split(":")
                    self.db[name.strip().lower()] = {"secret": secret.strip(),
                                              }

        except ValueError:
            print "Error: Check the syntax of hosts.db file."
            sys.exit(0)

        except OSError:
            print "Error: Access problem on %s" % self.options.db
            sys.exit(0)

        # setting standard IO
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

        # Webserver should run under which user and group
        try:
            self.slave_user = self.config.get("User", "user", "heartbeat")
        except NoSectionError:
            print "Error: Can't find a suitable username in config file."
            sys.exit(1)

        try:
            self.slave_group = self.config.get("User", "group", "heartbeat")
        except NoSectionError:
            print "Error: Can't find a suitable group name in config file."
            sys.exit(1)

        # Setting up log directory
        self.logfolder = self.config.get("Log", "folder")
        if not os.path.exists(self.logfolder):
            try:
                os.makedirs(self.logfolder)
            except OSError, e:
                print e
                sys.exit(1)

        try:
            uid = getpwnam(self.slave_user)[2]
            gid = getpwnam(self.slave_user)[3]
            os.chown(self.logfolder, uid, gid)
            os.chmod(self.logfolder,
                     stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR | \
                     stat.S_IXGRP | stat.S_IWGRP | stat.S_IRGRP)

            setup_logger(self.config, "/".join((self.logfolder,
                                                "heartbeat.log")),
                                        self.options.debug)
        except OSError, e:
            print "%s" % e
            print "Note: Did you forget to run heartbeatd as root?"
            sys.exit(1)

        # we import logger here because it should import after
        # setup_logger called
        from hbeat.logging import logger

        self.logger = logger

        # Registering a cleanup method
        atexit.register(self.__cleanup__)

    def __cleanup__(self):
        """
        HeartBeat destructor.
        """
        # removing servers pid files on exit
        if os.path.exists(self.mpid):
            try:
                os.remove(self.mpid)
            except OSError, e:
                self.logger.info("Error msg: %s" % e)
                raise

    def _status(self):
        """
        checking for heartbeat processes.
        """
        if not os.path.exists(self.mpid):
            return False

        self._masterpid = file(self.mpid).readlines()[0]
        if os.path.exists("/proc/%s" % self._masterpid):
            return True

        else:
            try:
                os.remove(self.mpid)
            except OSError:
                pass
            return False

    def start(self):
        """
        Start the HeartBeat server. all the daemon forking process runs here.
        """
        from hbeat.server import HeartBeatServer

        if self._status():
            print "Debbox is already running."
            return

        # Daemonizing Process ==============================
        # Please read about how a daemon work before asking
        # questions

        if not self.options.foreground:
            pid = None
            try:
                pid = os.fork()
            except OSError:
                raise self.CantFork("Can't create the master process.")

            if pid > 0:
                # Exist from parent
                sys.exit(0)

            os.umask(027)
            try:
                self._sid = os.setsid()
            except OSError:
                raise

            self._masterpid = os.getpid()
            self.logger.info("Master process at %s" % self._masterpid)

            file(self.mpid, "w+").write(str(self._masterpid))

            uid = getpwnam(self.slave_user)[2]
            gid = getpwnam(self.slave_user)[3]

            uid = getpwnam(self.slave_user)[2]
            os.chown(self.mpid, uid, gid)
            os.setuid(int(uid))
            #os.setgid(int(gid))
            os.umask(027)

        if self.options.foreground:
            atexit.register(self.stop)

        server = HeartBeatServer(self.options.host,
                                 self.options.port,
                                 db=self.db)

        print "Starting HeartBeat server . . ."
        if not self.options.debug or not self.options.foreground:
                self.io_redirect()

        signal.signal(signal.SIGUSR1, self._usr1_handler)
        server.serve_forever()

    def stop(self):
        """
        Stop the HeartBeat server, and clean the environment with
        removing any temporary files and pid files.
        """
        if not self.options.foreground:
            if not self._status():
                self.logger.info("HeartBeat is not running. . .")
                print "HeatBeat is not running. . ."
                return

            mpid = file(self.mpid).readlines()[0]
            self.__cleanup__()
            print "Stopping master process."
            os.kill(int(mpid), 15)

        sys.exit(0)

    def status(self):
        """
        Return the status of HeartBeat server.
        """
        if os.path.exists(self.mpid):
            print "HeartBeat Master process is running with '%s' pid" % \
                  file(self.mpid).readlines()[0]
        else:
            print "Debbox Master is not running."

    def io_redirect(self):
        """
        Redirect all the IO to given IOs in the constructor. and skip the
        redirecting process if daemon run in foreground ar debbug mode.
        """
        if not self.options.debug or not self.options.foreground:
            # Redirecting standard I/O to nowhere
            sys.stdout.flush()
            sys.stderr.flush()
            si = file(self.stdin, 'r')
            so = file(self.stdout, 'a+')
            se = file(self.stderr, 'a+', 0)
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())

    def _usr1_handler(self, signum, frame):
        """
        SIGUSR1 handler. HeartBeat will treat SIGUSR1 just like SIGTERM.
        """

        #os.waitpid(self._slavepid, 0)
        if self.options.foreground:
            mpid = os.getpid()
            os.kill(int(mpid), 15)
        self.stop()

    class CantFork (Exception):
        """
        This exception will raise if daemon can't for a new process.
        """
        pass

    class CantFindConfigFile (Exception):
        """
        This exception will raise if daemon can't find the Debbox
        main configuration file.
        """
        pass
