# vi: ai ts=4 sw=4 et
# To see logging, use parameters: --no-logcapture -T -c
'''Basic implementation of UDP protocol sample echo client.'''

import asyncio
import logging

class EchoClientProtocol:
    '''
    Basic implementation of an echo client protocol factory,
    based on Python docs.
    '''
    def __init__(self, on_con_lost):
        '''Initialize the echo client'''
        logging.info('__init__')
        self.on_con_lost = on_con_lost
        self.transport = None
        self.recvd_msgs = asyncio.Queue()

    def connection_made(self, transport):
        '''Base protcol: Called when a connection is made.'''
        logging.info('connection_made')
        self.transport = transport

    def connection_lost(self, exc):             # pylint: disable=W0613
        '''Base protcol: Called when a connection is lost or closed.'''
        logging.info('connection_lost')
        self.on_con_lost.set_result(True)

    def datagram_received(self, data, addr):    # pylint: disable=W0613
        '''Datagram protcol: Called when a datagram is received.'''
        logging.info('datagram_received')
        self.recvd_msgs.put_nowait(data.decode())

    def error_received(self, exc):              # pylint: disable-msg=R0201,W0613
        '''Datagram protcol: Called when an error is received.'''
        logging.info('error_received')

    def send_datagram(self, message):
        '''Send a datagram to the server.'''
        logging.info('send_datagram')
        self.transport.sendto(message.encode())
