#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (C) 2011 Rodrigo Pinheiro Marques de Araujo
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#




import os
import sys
import signal
import socket
import psutil
import logging
import subprocess
import simplejson
import SocketServer



SOCKET_FILE="/tmp/.perfectresume"
LOG_FILE = SOCKET_FILE + ".log"
MAGIC_NUMBER = '42'


logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")



def remove_socket_on_signal(signum, frame):
    logging.info('removing socket on signal')
    os.remove(SOCKET_FILE)


signal.signal(signal.SIGTERM, remove_socket_on_signal)
signal.signal(signal.SIGINT, remove_socket_on_signal)


class RestartableProcess(object):

    def __init__(self, process):
        self.process = process
        cmdline = " ".join(self.cmdline)
        self.start_cmdline = cmdline.split()
        self.start_cmdline_str = " ".join(self.start_cmdline)


    def __getattr__(self, attr):
        return getattr(self.process, attr)

    def stop(self):

        logging.info("stopping " + self.start_cmdline_str)
        self.terminate()
        if self.is_running():
            self.kill()
        logging.info(self.start_cmdline_str +  " stopped")


    def start(self):
        logging.info("starting " + self.start_cmdline_str)
        popen = subprocess.Popen(self.start_cmdline, 
                                 stderr=subprocess.PIPE, 
                                 stdout=subprocess.PIPE)
        logging.info(self.start_cmdline_str +  " started")


    def restart(self):
        self.stop()
        self.start()




class Service(object):


    def get_process(self, cmdline):
        for process in psutil.process_iter():
            process_cmdline = " ".join(process.cmdline)
            if process_cmdline == cmdline:
                return RestartableProcess(process)


    def get_user_conf(self):
        filename = os.path.join(os.environ['HOME'], ".perfectresume.conf")
        try:
            with file(filename) as f:
                user_conf = simplejson.load(f)
                return user_conf
        except IOError, error:
            msg = "configuration file not fount at " + filename
            logging.error(msg)
            print msg
            return {}


    def run(self):

        os.setsid() #detach childs
        for program, conf in self.get_user_conf().items():
            logging.info('trying get pid of ' + conf['cmdline'] ) 
            process = self.get_process(conf['cmdline'])
            if process:
                process.stop()

                if 'subprocesses' in conf:
                    for subprocess_cmdline in conf["subprocesses"]:
                        logging.info('trying get pid of' + subprocess_cmdline ) 
                        subprocess = self.get_process(subprocess_cmdline)
                        if subprocess:
                            subprocess.stop()
                        else:
                            logging.error(subprocess_cmdline + ' not running') 


                process.start()

            else:
                logging.error(conf['cmdline'] + ' not running') 



class UnixHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        logging.info('request received') 
        self.data = self.request.recv(1024).strip()
        if self.data == MAGIC_NUMBER:
            logging.info('request is ok') 
            Service().run()
            self.request.send('ok')
        else:
            logging.error('request message error') 
            self.request.send('error')



class ForkingUnixStreamServer( SocketServer.ForkingMixIn, SocketServer.UnixStreamServer  ):
    pass


def main():
    if os.path.exists(SOCKET_FILE):
        logging.info('socketfile exists, removing') 
        os.remove(SOCKET_FILE)
    server = ForkingUnixStreamServer(SOCKET_FILE,UnixHandler)
    logging.info('starting server') 
    server.serve_forever()


if __name__ == "__main__":
    main()
