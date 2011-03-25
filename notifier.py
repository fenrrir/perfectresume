#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
    if sys.argv[1] == "resume":
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

