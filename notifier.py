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

import sys
import socket
import logging


SOCKET_FILE="/tmp/.perfectresume"
LOG_FILE = SOCKET_FILE + ".client.log"
MAGIC_NUMBER = '42'

logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    logging.info("params " + " ".join(sys.argv))
    if sys.argv[1] == "resume" or sys.argv[1] == "thaw":
        logging.info("sending message")
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(SOCKET_FILE)
            s.send(MAGIC_NUMBER)
            data = s.recv(1024)
            if data == 'ok':
                logging.info("message is ok")
                sys.exit(0)
            else:
                logging.error("data is " + data)
                sys.exit(1)
        except Exception, error:
            logging.exception("error")
            sys.exit(1)
        finally:
            s.close()

if __name__ == "__main__":
    main()

