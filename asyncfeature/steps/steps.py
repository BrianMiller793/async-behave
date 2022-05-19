# vi: ts=4 et ai
'''
Behave demonstration of asynchronous coroutines sending and receiving
UDP datagrams.
'''
# This code is released under the GPL 3.0 license, and contains code
# from Python and Behave examples.

import asyncio
import logging

from behave import step, given, then # pylint: disable=E0611
from behave.api.async_step import \
    async_run_until_complete, use_or_create_async_context
from hamcrest import assert_that, equal_to, empty, has_item

#############################################################
# The following step is from the Behave notes documentation


@step('an async-step waits {duration:f} seconds')
@async_run_until_complete
async def step_async_step_waits_seconds_py35(context, duration): # pylint: disable=W0613
    '''Simple example of a coroutine as async-step (in Python 3.5)'''
    await asyncio.sleep(duration)

#############################################################
# The following steps are from the Behave notes documentation

# Alice, Bob, "ALICE, BOB"
@asyncio.coroutine
def async_func(param):
    '''Sleep, then return result as upper-case.'''
    yield from asyncio.sleep(0.2)
    return str(param).upper()

@given('I dispatch an async-call with param "{param}"')
def step_dispatch_async_call(context, param):
    '''Dispatch one asynchronous function.'''
    async_context = use_or_create_async_context(context, 'async_context1')
    task = async_context.loop.create_task(async_func(param))
    async_context.tasks.append(task)

@then('the collected result of the async-calls is "{expected}"')
def step_collected_async_call_result_is(context, expected):
    '''Get the results of an asynchronous function.'''
    async_context = context.async_context1
    done, pending = async_context.loop.run_until_complete(
        asyncio.wait(async_context.tasks, loop=async_context.loop))

    parts = [task.result() for task in done]
    joined_result = ', '.join(sorted(parts))
    assert_that(joined_result, equal_to(expected))
    assert_that(pending, empty())

#############################################################
# To see logging, use parameters: --no-logcapture -T -c

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
        self.recvd_msgs = []

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
        self.recvd_msgs.append(data.decode())

    def error_received(self, exc):              # pylint: disable-msg=R0201,W0613
        '''Datagram protcol: Called when an error is received.'''
        logging.info('error_received')

    def send_datagram(self, message):
        '''Send a datagram to the server.'''
        logging.info('send_datagram')
        self.transport.sendto(message.encode())

async def start_client(async_context, on_con_lost, object_queue):
    '''Start the echo client'''
    logging.info('start_client')
    echo_transport, protocol = \
        await async_context.loop.create_datagram_endpoint(
            lambda: EchoClientProtocol(on_con_lost),
            remote_addr=('127.0.0.1', 9999))
    await object_queue.put(echo_transport)
    await object_queue.put(protocol)
    await object_queue.join()
    return protocol.recvd_msgs

async def send_echo_msg(object_queue, messages):
    '''Send messages to the echo server'''
    logging.info('send_echo_msg')
    # Get the transport and protocol objects
    transport = await object_queue.get()
    object_queue.task_done()
    logging.info('send_echo_msg, received transport')

    protocol = await object_queue.get()
    object_queue.task_done()
    logging.info('send_echo_msg, received protocol')

    for message in messages:
        logging.info('sending datagram')
        protocol.send_datagram(message)
        await asyncio.sleep(0.25)
    transport.close()
    return None

@given('the client sends the words "{words}"')
def step_dispatch_async_call(context, words): # pylint: disable-msg=E0102
    '''Start the echo client coroutines'''
    logging.info('sends the words')
    messages = words.split(', ')
    async_context = use_or_create_async_context(context, 'udp_datagram')
    object_queue = asyncio.Queue()
    on_con_lost = async_context.loop.create_future()

    # Create the task for the client
    task = async_context.loop.create_task(
        start_client(async_context, on_con_lost, object_queue))
    async_context.tasks.append(task)

    # Create the task for using the client
    task = async_context.loop.create_task(
        send_echo_msg(object_queue, messages))
    async_context.tasks.append(task)

@then('the client will receive the words "{expected}"')
def step_collected_async_call_result_is(context, expected): # pylint: disable-msg=E0102
    '''Collect the results from the echo coroutines'''
    logging.info('receive the words')
    async_context = context.udp_datagram

    # This is where the background tasks are started.
    # pylint: disable=W0612
    done, pending = async_context.loop.run_until_complete(
        asyncio.wait(async_context.tasks, loop=async_context.loop))
    # pylint: enable=W0612

    for task in done:
        logging.info('task done')
        logging.info(task.result())
        if task.result() is not None:
            for word in expected.split(', '):
                assert_that(task.result(), has_item(word))
