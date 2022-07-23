# vi: ts=4 et ai
'''
Behave demonstration of asynchronous coroutines sending and receiving
UDP datagrams.
'''
# This code is released under the GPL 3.0 license, and contains code
# from Python and Behave examples.

import asyncio
import logging

from behave import step, given, when, then # pylint: disable=E0611
from behave.api.async_step import \
    async_run_until_complete, use_or_create_async_context
from hamcrest import assert_that, equal_to, empty

from echoclient import EchoClientProtocol

#############################################################
# The following step is from the Behave notes documentation

@step('an async-step waits {duration:f} seconds')
@async_run_until_complete
async def step_wait(context, duration): # pylint: disable=W0613
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
def step_dispatch(context, param):
    '''Dispatch one asynchronous function.'''
    async_context = use_or_create_async_context(context, 'async_context1')
    task = async_context.loop.create_task(async_func(param))
    async_context.tasks.append(task)

@then('the collected result of the async-calls is "{expected}"')
def step_collect(context, expected):
    '''Get the results of an asynchronous function.'''
    async_context = context.async_context1
    done, pending = async_context.loop.run_until_complete(
        asyncio.wait(async_context.tasks, loop=async_context.loop))

    parts = [task.result() for task in done]
    joined_result = ', '.join(sorted(parts))
    assert_that(joined_result, equal_to(expected))
    assert_that(pending, empty())

#############################################################

async def start_client(async_context, on_con_lost, object_queue):
    '''Start the echo client

    :param async_context: Transport-specific async loop context.
    :param on_con_lost: Python future for connection failure or closure.
    :param object_queue: Used to return the transport and protocol objects.
    '''
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
def step_send_words(context, words): # pylint: disable-msg=E0102
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
def step_rcv_words(context, expected): # pylint: disable-msg=E0102
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
                assert task.result().get_nowait() == word

#############################################################

@given('the client is started')
@async_run_until_complete
async def step_start_client(context):
    '''Start the echo client'''
    logging.info('start_client')

    # Save transport and protocol in test scenario context
    async_context = use_or_create_async_context(context, 'udp_datagram')
    on_con_lost = async_context.loop.create_future()
    context.echo_transport, context.echo_protocol = \
        await async_context.loop.create_datagram_endpoint(
            lambda: EchoClientProtocol(on_con_lost),
            remote_addr=('127.0.0.1', 9999))

@then('the client sends the word "{word}"')
def step_send_word(context, word):
    '''Send a word via network transport.'''
    context.echo_transport.sendto(word.encode())

@then('the client will receive the word "{expected}"')
@async_run_until_complete(async_context='udp_datagram')
async def step_rcv_word(context, expected): # pylint: disable-msg=E0102
    '''Receive a word via network transport.'''
    echo_msg = await context.echo_protocol.recvd_msgs.get()
    assert echo_msg == expected

#############################################################

@given('the fixture transport context is available')
def step_check_context(context):
    '''Check for transport context'''
    assert hasattr(context, 'udp_transport')
    assert hasattr(context, 'echo')

@when('the client using the fixture transport sends "{word}"')
def step_fx_send(context, word):
    '''Send a word via network transport.'''
    transport = context.echo[0]
    assert transport is not None
    transport.sendto(word.encode())

@then('the client using the fixture transport receives "{word}"')
@async_run_until_complete
async def step_fx_rcv(context, word):
    '''Receive a word via network transport.'''
    echo_msg = await context.echo[1].recvd_msgs.get()
    assert echo_msg == word
